import shutil
import os
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return JSONResponse(content={"filename": file.filename, "url": f"/files/{file.filename}"})

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
