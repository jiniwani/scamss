@echo off
setlocal ENABLEDELAYEDEXPANSION
title Verio Demo Server

echo === Verio 로컬 데모 시작 ===
echo 현재 경로: %cd%

REM 1) 가상환경 생성
if not exist .venv\Scripts\python.exe (
  echo [1/4] 가상환경 생성 중...
  python -m venv .venv
)

REM 2) 가상환경 활성화
call .venv\Scripts\activate

REM 3) 라이브러리 설치
echo [2/4] 라이브러리 설치 중...
pip install --quiet -r requirements.txt

REM 4) 환경변수 설정 (제미나이 키 없으면 입력 받기)
if "%GEMINI_API_KEY%"=="" (
  set /p GEMINI_API_KEY=Gemini API Key 입력: 
  REM 사용자 환경변수로 저장(다음부터 자동 인식)
  setx GEMINI_API_KEY "%GEMINI_API_KEY%" >nul
)
set ENVIRONMENT=local

REM 5) 서버 실행
echo [3/4] 서버 실행 중... (http://127.0.0.1:8081/ui/)
python -m uvicorn src.app.main:app --host 127.0.0.1 --port 8081 --reload

echo [4/4] 서버가 종료되었습니다.
pause


