from fastapi import FastAPI
import os
from dotenv import load_dotenv

from ocr_engine import router as ocr_router, initialize_ocr_engine

# 환경 변수 로드
load_dotenv()

# API 라이센스 키와 서버 주소 환경 변수에서 가져오기
LICENSE_KEY = os.getenv("OCR_LICENSE_KEY")
BASE_URL = os.getenv("OCR_BASE_URL")

app = FastAPI(
    title="OCR API",
    description="OCR 처리를 위한 FastAPI 애플리케이션",
    version="1.0.0",
)

# 애플리케이션 시작 시 OCR 엔진 초기화
@app.on_event("startup")
async def startup_event():
    if not LICENSE_KEY or not BASE_URL:
        raise ValueError("OCR_LICENSE_KEY 및 OCR_BASE_URL 환경 변수가 필요합니다.")
    initialize_ocr_engine(LICENSE_KEY, BASE_URL)

# OCR 라우터 등록
app.include_router(ocr_router)

# 기본 라우트
@app.get("/")
async def root():
    return {"message": "OCR API에 오신 것을 환영합니다!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)