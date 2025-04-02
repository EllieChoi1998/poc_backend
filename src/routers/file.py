from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import httpx
import os
import shutil
from typing import Optional
from pydantic import BaseModel

router = APIRouter()
UPLOAD_DIR = "uploads"
AI_SERVER_URL = "http://192.168.0.196:8001"  # AI 서버 주소

# 필요한 디렉토리 생성
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ProcessResult(BaseModel):
    success: bool
    message: str
    result_file: Optional[str] = None

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """클라이언트로부터 파일 업로드 받기"""
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return JSONResponse(content={"filename": file.filename, "url": f"/files/{file.filename}"})

@router.post("/process-document/")
async def process_document(
    filename: str = Form(...),
    source_type: str = Form(...)  # "운용지시서" or "계약서"
):
    """백엔드에서 업로드된 파일을 AI 서버로 전송하여 처리 요청"""
    
    # 업로드된 파일 경로 확인
    file_path = f"{UPLOAD_DIR}/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File {filename} not found in upload directory")
    
    # 파일 타입 검증
    if not filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # AI 서버에 파일 전송
    try:
        async with httpx.AsyncClient() as client:
            with open(file_path, "rb") as f:
                files = {"file": (filename, f, "application/pdf")}
                data = {"source_type": source_type}
                
                # 5분 타임아웃 설정 (대용량 문서 처리 시간 고려)
                response = await client.post(
                    f"{AI_SERVER_URL}/process/", 
                    files=files, 
                    data=data,
                    timeout=900.0
                )
            
            if response.status_code == 200:
                result = response.json()
                return ProcessResult(**result)
            else:
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"AI server error: {response.text}"
                )
    
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Processing timeout. The document may be too large or complex.")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Error connecting to AI server: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing request failed: {str(e)}")

@router.get("/results/{filename}")
async def get_result_from_ai_server(filename: str):
    """AI 서버에서 처리 결과 파일 가져오기"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AI_SERVER_URL}/results/{filename}",
                timeout=60.0
            )
            
            if response.status_code == 200:
                # 결과 파일을 백엔드 서버에 저장
                result_path = f"{UPLOAD_DIR}/results"
                os.makedirs(result_path, exist_ok=True)
                local_file_path = f"{result_path}/{filename}"
                
                with open(local_file_path, "wb") as f:
                    f.write(response.content)
                
                return JSONResponse(
                    content={
                        "message": "Result file retrieved successfully",
                        "filename": filename,
                        "url": f"/files/results/{filename}"
                    }
                )
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error retrieving result from AI server: {response.text}"
                )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve result: {str(e)}")

@router.get("/search/{filename}")
async def search_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(file_path):
        return JSONResponse(content={"error": "File not found"}, status_code=404)
    
    return JSONResponse(content={"file_url": f"http://192.168.0.196/uploads/{filename}"})

@router.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        return JSONResponse(content={"error": "File not found"}, status_code=404)

    return FileResponse(path=file_path, filename=filename, media_type="application/octet-stream")
