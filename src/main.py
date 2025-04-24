from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import user, file
from services.system_service import SystemService

app = FastAPI(title="IBK API", description="IBK Backend API Server")

# 애플리케이션 시작 시 시스템 계정 초기화
@app.on_event("startup")
async def startup_event():
    print("애플리케이션 시작: 시스템 계정 초기화 중...")
    SystemService.initialize_system_account()
    print("시스템 초기화 완료")

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
app.include_router(file.router, prefix="/files", tags=["Files"])

@app.get("/")
async def root():
    return {"message": "IBK API Server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)