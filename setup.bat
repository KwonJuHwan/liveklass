@echo off
echo [1/3] 가상환경 생성 중...
python -m venv venv
call venv\Scripts\activate

echo [2/3] 라이브러리 설치 중...
pip install -r requirements.txt

echo [3/3] Docker 컨테이너 실행 중...
docker compose down
docker compose up -d

echo.
echo ========================================================
echo 초기 세팅 완료!
echo 아래 명령어를 입력하여 가상환경을 활성화하세요:
echo venv\Scripts\activate
echo ========================================================