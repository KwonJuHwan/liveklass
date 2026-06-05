@echo off
echo [1/4] 가상환경 생성 중...
python -m venv venv
call venv\Scripts\activate

echo [2/4] 라이브러리 설치 중...
pip install -r requirements.txt

echo [3/4] Docker 컨테이너 실행 중 (DB 환경 세팅)...
docker compose down
docker compose up -d

echo 데이터베이스 연결 준비 중... 잠시 대기해 주세요.
timeout /t 5 /nobreak >nul

echo [4/4] 메인 애플리케이션 실행 중...
python -m app.main


echo ========================================================
echo 초기 세팅 및 애플리케이션 실행 완료!
echo 나중에 다시 실행하시려면 아래 명령어를 입력하여 가상환경을 활성화하세요:
echo venv\Scripts\activate
echo 데이터 적재 완료 후,
echo ========================================================