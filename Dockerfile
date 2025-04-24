# Python 3.12 기반 이미지 사용
FROM python:3.12

# 작업 디렉토리 설정
WORKDIR .

# 환경 변수 설정 (PYTHONPATH 추가)
ENV PYTHONPATH=/src/

# 의존성 설치
COPY requirements.txt .  
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# FastAPI 실행 (모듈 경로 수정)
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8888"]
