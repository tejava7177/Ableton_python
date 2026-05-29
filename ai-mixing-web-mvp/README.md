# AI Mixing Assistant Web MVP

`mixing-extension`의 세션/분석 구조를 참고해 만든 웹 기반 AI Mixing Assistant 테스트 프로젝트다. 목표는 완전한 웹 DAW가 아니라, 로컬에서 다음 플로우를 검증하는 것이다.

```text
프로젝트 생성
-> WAV 업로드
-> 트랙 목록 표시
-> 기본 오디오 분석
-> Low / High Cut 처리
-> 처리 전/후 미리듣기 URL 확인
-> 승인/취소용 Action 상태 저장
```

## 현재 구현 범위

- FastAPI 백엔드
- Next.js 프론트엔드
- 인메모리 Project / Track / Analysis / Action 세션 저장소
- WAV 업로드
- 기본 분석
  - duration
  - sample_rate
  - channels
  - peak_dbfs
  - rms_dbfs
- Low / High Cut 처리
- 원본/처리본 정적 파일 제공
- 단일 페이지 테스트 UI

## 제외된 기능

- 완전한 웹 DAW
- 실시간 다중트랙 믹서
- 로그인/결제/권한
- DB 영속 저장
- WebSocket/SSE
- LLM 채팅
- Compressor
- 레퍼런스 비교
- 고급 EQ UI
- Ableton/M4L 연동

## 지원 파일 형식

- `.wav`

## Backend 실행

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

기본 주소:
- API: `http://127.0.0.1:8000`
- 정적 파일: `http://127.0.0.1:8000/files/uploads/...`

## Frontend 실행

```bash
cd frontend
npm install
npm run dev
```

기본 주소:
- UI: `http://127.0.0.1:3000`

필요하면 환경변수로 API 주소를 지정할 수 있다.

```bash
NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000 npm run dev
```

## 테스트 순서

1. 백엔드 실행
2. 프론트엔드 실행
3. 페이지에서 프로젝트 이름 입력 후 생성
4. WAV 파일 업로드
5. Track List에서 업로드 확인
6. Analyze 클릭
7. 분석 결과 확인
8. Low Cut / High Cut 값 입력
9. Apply 클릭
10. 원본/처리본 audio player 비교

## 프로젝트 구조

```text
ai-mixing-web-mvp/
├── backend/
└── frontend/
```

