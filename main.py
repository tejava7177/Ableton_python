from __future__ import annotations

import json
from pathlib import Path
from typing import Any


VALID_FIELDS = {"value", "min", "max", "id"}


def convert_flat_to_nested(flat_data: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    nested: dict[str, dict[str, Any]] = {}
    skipped: dict[str, Any] = {}

    for key, value in flat_data.items():
        if not isinstance(key, str):
            skipped[str(key)] = value
            continue

        if "_" not in key:
            skipped[key] = value
            continue

        param_name, field = key.rsplit("_", 1)

        if field not in VALID_FIELDS:
            skipped[key] = value
            continue

        if not isinstance(value, (int, float, str, bool)):
            skipped[key] = value
            continue

        if param_name not in nested:
            nested[param_name] = {}

        nested[param_name][field] = value

    return nested, skipped


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"

    input_path = data_dir / "flat_params.json"
    output_path = data_dir / "nested_params.json"
    skipped_path = data_dir / "skipped_items.json"

    with input_path.open("r", encoding="utf-8") as f:
        flat_data = json.load(f)

    nested_data, skipped_items = convert_flat_to_nested(flat_data)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(nested_data, f, ensure_ascii=False, indent=2)

    with skipped_path.open("w", encoding="utf-8") as f:
        json.dump(skipped_items, f, ensure_ascii=False, indent=2)

    print(f"입력 key 수: {len(flat_data)}")
    print(f"변환된 파라미터 수: {len(nested_data)}")
    print(f"건너뛴 항목 수: {len(skipped_items)}")
    print(f"저장 완료: {output_path}")
    print(f"저장 완료: {skipped_path}")


if __name__ == "__main__":
    main()