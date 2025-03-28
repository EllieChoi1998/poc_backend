from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import user, file  # 라우터 가져오기

app = FastAPI()

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
    return {"message": "Welcome to FastAPI"}
