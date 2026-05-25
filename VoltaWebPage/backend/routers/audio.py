from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from services.audio_processing import (
    AUDIO_FILE_SIZE_LIMIT_BYTES,
    analyze_audio,
    apply_high_pass,
    apply_low_pass,
    detect_silence_regions,
    load_audio,
    remove_internal_silence,
    save_audio,
    shorten_internal_silence,
    trim_start_end,
)


router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[1]
UPLOADS_DIR = BASE_DIR / "uploads"
PROCESSED_DIR = BASE_DIR / "processed"

TRIM_MODES = {
    "start_end_only",
    "remove_internal",
    "shorten_internal",
}


def _ensure_wav_file(upload_file: UploadFile) -> None:
    filename = (upload_file.filename or "").lower()
    content_type = (upload_file.content_type or "").lower()

    if not filename.endswith(".wav") and content_type not in {
        "audio/wav",
        "audio/x-wav",
        "audio/wave",
        "audio/vnd.wave",
    }:
        raise HTTPException(status_code=400, detail="Only WAV files are supported.")


async def _persist_upload(upload_file: UploadFile) -> Path:
    _ensure_wav_file(upload_file)

    content = await upload_file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(content) > AUDIO_FILE_SIZE_LIMIT_BYTES:
        limit_mb = AUDIO_FILE_SIZE_LIMIT_BYTES // (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail=f"File is too large. Maximum supported size is {limit_mb}MB.",
        )

    file_id = uuid4().hex
    safe_name = Path(upload_file.filename or "upload.wav").name
    output_path = UPLOADS_DIR / f"{file_id}_{safe_name}"
    output_path.write_bytes(content)
    return output_path


@router.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    saved_path = await _persist_upload(file)

    try:
        audio, sample_rate = load_audio(saved_path)
        analysis = analyze_audio(audio, sample_rate)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to analyze audio: {exc}")

    return {
        "file_id": saved_path.stem.split("_", 1)[0],
        "filename": file.filename,
        "duration": analysis["duration"],
        "sample_rate": analysis["sample_rate"],
        "channels": analysis["channels"],
        "peak_dbfs": analysis["peak_dbfs"],
        "rms_dbfs": analysis["rms_dbfs"],
        "original_file_url": f"/uploads/{saved_path.name}",
    }


def _validate_silence_inputs(
    threshold_db: float,
    min_silence_ms: int,
    padding_ms: int,
    mode: str | None = None,
) -> None:
    if threshold_db < -80 or threshold_db > -20:
        raise HTTPException(
            status_code=400,
            detail="Silence Threshold must be between -80 dBFS and -20 dBFS.",
        )
    if min_silence_ms < 50 or min_silence_ms > 2000:
        raise HTTPException(
            status_code=400,
            detail="Min Silence Duration must be between 50ms and 2000ms.",
        )
    if padding_ms < 0 or padding_ms > 500:
        raise HTTPException(
            status_code=400,
            detail="Padding must be between 0ms and 500ms.",
        )
    if mode is not None and mode not in TRIM_MODES:
        raise HTTPException(
            status_code=400,
            detail="Mode must be one of: start_end_only, remove_internal, shorten_internal.",
        )


@router.post("/detect-silence")
async def detect_silence(
    file: UploadFile = File(...),
    threshold_db: float = Form(...),
    min_silence_ms: int = Form(...),
    padding_ms: int = Form(...),
):
    _validate_silence_inputs(threshold_db, min_silence_ms, padding_ms)
    saved_path = await _persist_upload(file)

    try:
        audio, sample_rate = load_audio(saved_path)
        analysis = analyze_audio(audio, sample_rate)
        silence_regions = detect_silence_regions(audio, sample_rate, threshold_db, min_silence_ms)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to detect silence: {exc}")

    return {
        "duration": analysis["duration"],
        "silence_regions": silence_regions,
    }


@router.post("/trim-silence")
async def trim_silence(
    file: UploadFile = File(...),
    threshold_db: float = Form(...),
    min_silence_ms: int = Form(...),
    padding_ms: int = Form(...),
    mode: str = Form(...),
):
    _validate_silence_inputs(threshold_db, min_silence_ms, padding_ms, mode)
    saved_path = await _persist_upload(file)

    try:
        audio, sample_rate = load_audio(saved_path)
        silence_regions = detect_silence_regions(audio, sample_rate, threshold_db, min_silence_ms)

        if mode == "start_end_only":
            processed_audio = trim_start_end(audio, sample_rate, silence_regions, padding_ms)
        elif mode == "remove_internal":
            processed_audio = remove_internal_silence(audio, sample_rate, silence_regions, padding_ms)
        else:
            processed_audio = shorten_internal_silence(audio, sample_rate, silence_regions, padding_ms)

        original_duration = audio.shape[0] / sample_rate
        processed_duration = processed_audio.shape[0] / sample_rate
        removed_duration = max(0.0, original_duration - processed_duration)

        output_name = f"{uuid4().hex}_trim.wav"
        output_path = PROCESSED_DIR / output_name
        save_audio(processed_audio, sample_rate, output_path)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to trim silence: {exc}")

    return {
        "processed_file_url": f"/processed/{output_name}",
        "original_duration": round(original_duration, 3),
        "processed_duration": round(processed_duration, 3),
        "removed_duration": round(removed_duration, 3),
        "silence_regions": silence_regions,
        "applied": {
            "threshold_db": threshold_db,
            "min_silence_ms": min_silence_ms,
            "padding_ms": padding_ms,
            "mode": mode,
        },
    }


@router.post("/low-high-cut")
async def low_high_cut(
    file: UploadFile = File(...),
    low_cut_hz: float = Form(...),
    high_cut_hz: float = Form(...),
):
    if low_cut_hz < 20 or low_cut_hz > 1000:
        raise HTTPException(status_code=400, detail="Low Cut must be between 20Hz and 1000Hz.")
    if high_cut_hz < 1000 or high_cut_hz > 22000:
        raise HTTPException(status_code=400, detail="High Cut must be between 1000Hz and 22000Hz.")
    if low_cut_hz >= high_cut_hz:
        raise HTTPException(status_code=400, detail="Low Cut must be lower than High Cut.")

    saved_path = await _persist_upload(file)

    try:
        audio, sample_rate = load_audio(saved_path)
        before = analyze_audio(audio, sample_rate)

        processed_audio = apply_high_pass(audio, sample_rate, low_cut_hz)
        processed_audio = apply_low_pass(processed_audio, sample_rate, high_cut_hz)

        after = analyze_audio(processed_audio, sample_rate)
        output_name = f"{uuid4().hex}_low_high_cut.wav"
        output_path = PROCESSED_DIR / output_name
        save_audio(processed_audio, sample_rate, output_path)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to process audio: {exc}")

    return {
        "processed_file_url": f"/processed/{output_name}",
        "analysis_before": {
            "peak_dbfs": before["peak_dbfs"],
            "rms_dbfs": before["rms_dbfs"],
        },
        "analysis_after": {
            "peak_dbfs": after["peak_dbfs"],
            "rms_dbfs": after["rms_dbfs"],
        },
        "applied": {
            "low_cut_hz": low_cut_hz,
            "high_cut_hz": high_cut_hz,
        },
    }
