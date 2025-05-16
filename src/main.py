# src/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import user, checklist, termsNconditons, contract, keypoint_result, checklist_result, ocr, pef, special
from services.system_service import SystemService
from services.ocr_service import OcrService
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# OCR 서비스 관련 환경 변수
OCR_LICENSE_KEY = os.getenv("OCR_LICENSE_KEY")
OCR_SERVER_URL = os.getenv("OCR_SERVER_URL")

app = FastAPI(title="IBK API", description="IBK Backend API Server")

# 애플리케이션 시작 시 시스템 계정 및 OCR 서비스 초기화
@app.on_event("startup")
async def startup_event():
    print("애플리케이션 시작: 시스템 계정 초기화 중...")
    SystemService.initialize_system_account()
    print("시스템 초기화 완료")
    
    # OCR 서비스 초기화
    if OCR_LICENSE_KEY and OCR_SERVER_URL:
        print(f"OCR 서비스 초기화 중... (서버: {OCR_SERVER_URL})")
        try:
            OcrService.initialize(OCR_LICENSE_KEY, OCR_SERVER_URL)
            print("OCR 서비스 초기화 완료")
        except Exception as e:
            print(f"OCR 서비스 초기화 실패: {str(e)}")
    else:
        print("OCR_LICENSE_KEY 또는 OCR_BASE_URL 환경 변수가 설정되지 않아 OCR 서비스를 초기화하지 않습니다.")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(contract.router, prefix="/contracts", tags=["Contracts"])
app.include_router(checklist.router, prefix="/checklist", tags=["Checklist"])
app.include_router(termsNconditons.router, prefix="/terms", tags=["Terms and Conditions"])
app.include_router(keypoint_result.router, prefix="/keypoint-results", tags=["Keypoint Results"])
app.include_router(checklist_result.router, prefix="/checklist-results", tags=["Checklist Results"])
app.include_router(ocr.router, prefix="/ocr", tags=["OCR"])
app.include_router(pef.router, prefix="/pefs", tags=["PEF 운용지시서"])
app.include_router(special.router, prefix="/special", tags=["특별자산 운용지시서"])


@app.get("/")
async def root():
    return {"message": "IBK API Server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)