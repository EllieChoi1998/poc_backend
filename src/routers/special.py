from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status, Query, Path
from fastapi.responses import JSONResponse
from services.special_service import SpecialService
from auth.jwt_utils import get_current_user
import os
import shutil
from typing import List, Dict, Any, Optional
from models import InstructionSpecial, InstructionSpecialResult, Attachment
import uuid
from datetime import datetime
# from utils.ai_client import send_to_ai_server  # AI 서버 통신 유틸리티 가정

router = APIRouter()
UPLOAD_DIR = "./special/original"
ATTACHMENT_DIR = "./special/attachments"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(ATTACHMENT_DIR, exist_ok=True)

@router.post("/special-start", status_code=status.HTTP_201_CREATED)
async def upload_process_special_instruction(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = current_user["id"]

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # 파일 저장
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 저장 중 오류가 발생했습니다: {str(e)}"
        )
    
    # AI 서버로 파일 전송하여 분석 결과 받기
    try:
        # ai_result = await send_to_ai_server(file_path)

        # 일단, 예시로 더미데이터 생성
        ai_result = {
            "content": "분석된 내용 예시",
            "quality": "Unknown dpi",
            "average_quality": "Unknown dpi",
            "saved_json": "{}"
        }
        
        # 특별 지시서 객체 생성
        special = InstructionSpecial(
            performer_id=user_id,
            file_name=file.filename
        )
        
        # 결과 객체 생성
        result = InstructionSpecialResult(
            result_content=ai_result.get("content", ""),
            all_qualities=ai_result.get("quality", "Unknown dpi"),
            average_quality=ai_result.get("average_quality", "Unknown dpi"),
            saved_json=ai_result.get("saved_json", "{}")
        )
        
        # 지시서와 결과 저장
        instruction_special_id = SpecialService.create_special_instruction_with_result(
            user_id=user_id,
            special=special,
            result=result
        )
        
        return {
            "message": "특별 지시서가 성공적으로 업로드되었습니다.",
            "instruction_special_id": instruction_special_id
        }
        
    except Exception as e:
        # 파일 저장에 성공했지만 처리 중 오류가 발생한 경우, 저장된 파일 삭제
        if os.path.exists(file_path):
            os.remove(file_path)
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 처리 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/{instruction_special_id}/attachment", status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    instruction_special_id: int = Path(..., description="특별 지시서 ID"),
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = current_user["id"]
    
    # 고유한 파일명 생성
    # unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(ATTACHMENT_DIR, file.filename)
    
    # 파일 저장
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"첨부 파일 저장 중 오류가 발생했습니다: {str(e)}"
        )
    
    try:
        # 첨부 파일 객체 생성
        attachment = Attachment(
            instruction_special_id=instruction_special_id,
            file_name=unique_filename
        )
        
        # DB에 첨부 파일 정보 저장
        attachment_id = SpecialService.create_attachment(
            user_id=user_id,
            instruction_special_id=instruction_special_id,
            attachment=attachment
        )
        
        return {
            "message": "첨부 파일이 성공적으로 업로드되었습니다.",
            "attachment_id": attachment_id,
            "file_name": unique_filename
        }
    except Exception as e:
        # 파일 저장에 성공했지만 DB 저장 중 오류가 발생한 경우, 저장된 파일 삭제
        if os.path.exists(file_path):
            os.remove(file_path)
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"첨부 파일 처리 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/{instruction_special_id}/result", status_code=status.HTTP_201_CREATED)
async def create_another_result(
    instruction_special_id: int = Path(..., description="특별 지시서 ID"),
    result_content: str = Form(""),
    all_qualities: str = Form("Unknown dpi"),
    average_quality: str = Form("Unknown dpi"),
    saved_json: str = Form("{}"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = current_user["id"]
    
    try:
        # 결과 객체 생성
        result = InstructionSpecialResult(
            instruction_special_id=instruction_special_id,
            result_content=result_content,
            all_qualities=all_qualities,
            average_quality=average_quality,
            saved_json=saved_json
        )
        
        # 새로운 결과 저장
        success = SpecialService.create_another_result(
            user_id=user_id,
            instruction_special_id=instruction_special_id,
            result=result
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="결과 저장에 실패했습니다."
            )
        
        return {"message": "새로운 결과가 성공적으로 저장되었습니다."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"결과 저장 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/all", status_code=status.HTTP_200_OK)
async def get_all_special_instructions(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = current_user["id"]
    
    try:
        instructions = SpecialService.get_all_special_instructions(user_id=user_id)
        return {"instructions": instructions}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"지시서 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/{instruction_special_id}", status_code=status.HTTP_200_OK)
async def get_special_instruction_details(
    instruction_special_id: int = Path(..., description="특별 지시서 ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = current_user["id"]
    
    try:
        # 결과 목록 조회
        results = SpecialService.get_all_results_by_special_instruction_id(
            user_id=user_id,
            instruction_special_id=instruction_special_id
        )
        
        # 첨부 파일 목록 조회
        attachments = SpecialService.get_attachments_by_instruction_id(
            user_id=user_id,
            instruction_special_id=instruction_special_id
        )
        
        return {
            "instruction_special_id": instruction_special_id,
            "results": results,
            "attachments": attachments
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"지시서 상세 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/result/{result_id}", status_code=status.HTTP_200_OK)
async def get_result_details(
    result_id: int = Path(..., description="결과 ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = current_user["id"]
    
    try:
        result = SpecialService.get_result_by_id(
            user_id=user_id,
            result_id=result_id
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 결과를 찾을 수 없습니다."
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"결과 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.put("/{instruction_special_id}/result/{result_id}/content", status_code=status.HTTP_200_OK)
async def update_result_content(
    instruction_special_id: int = Path(..., description="특별 지시서 ID"),
    result_id: int = Path(..., description="결과 ID"),
    content: str = Form(..., description="새 내용"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = current_user["id"]
    
    try:
        success = SpecialService.update_result_content(
            user_id=user_id,
            instruction_special_id=instruction_special_id,
            result_id=result_id,
            new_content=content
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="결과를 찾을 수 없거나 업데이트에 실패했습니다."
            )
        
        return {"message": "결과 내용이 성공적으로 업데이트되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"결과 업데이트 중 오류가 발생했습니다: {str(e)}"
        )

@router.put("/{instruction_special_id}/result/{result_id}/usability", status_code=status.HTTP_200_OK)
async def update_result_usability(
    instruction_special_id: int = Path(..., description="특별 지시서 ID"),
    result_id: int = Path(..., description="결과 ID"),
    usability: str = Form(..., description="새 사용성 여부 (T 또는 F)"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = current_user["id"]
    
    # 사용성 값 검증
    if usability not in ["T", "F"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="사용성 값은 'T' 또는 'F'여야 합니다."
        )
    
    try:
        success = SpecialService.update_result_usability(
            user_id=user_id,
            instruction_special_id=instruction_special_id,
            result_id=result_id,
            usability=usability
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="결과를 찾을 수 없거나 업데이트에 실패했습니다."
            )
        
        return {"message": "결과 사용성이 성공적으로 업데이트되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"결과 업데이트 중 오류가 발생했습니다: {str(e)}"
        )

@router.put("/{instruction_special_id}/result/{result_id}/json", status_code=status.HTTP_200_OK)
async def update_result_json(
    instruction_special_id: int = Path(..., description="특별 지시서 ID"),
    result_id: int = Path(..., description="결과 ID"),
    json_data: str = Form(..., description="새 JSON 데이터"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = current_user["id"]
    
    try:
        success = SpecialService.update_result_json(
            user_id=user_id,
            instruction_special_id=instruction_special_id,
            result_id=result_id,
            new_json=json_data
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="결과를 찾을 수 없거나 업데이트에 실패했습니다."
            )
        
        return {"message": "결과 JSON이 성공적으로 업데이트되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"결과 업데이트 중 오류가 발생했습니다: {str(e)}"
        )

@router.delete("/result/{result_id}", status_code=status.HTTP_200_OK)
async def delete_result(
    result_id: int = Path(..., description="결과 ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = current_user["id"]
    
    try:
        success = SpecialService.delete_result_by_id(
            user_id=user_id,
            result_id=result_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="결과를 찾을 수 없거나 삭제에 실패했습니다."
            )
        
        return {"message": "결과가 성공적으로 삭제되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"결과 삭제 중 오류가 발생했습니다: {str(e)}"
        )

@router.delete("/{instruction_special_id}", status_code=status.HTTP_200_OK)
async def delete_special_instruction(
    instruction_special_id: int = Path(..., description="특별 지시서 ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = current_user["id"]
    
    try:
        success = SpecialService.delete_special_instruction(
            user_id=user_id,
            instruction_special_id=instruction_special_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="특별 지시서를 찾을 수 없거나 삭제에 실패했습니다."
            )
        
        return {"message": "특별 지시서가 성공적으로 삭제되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"특별 지시서 삭제 중 오류가 발생했습니다: {str(e)}"
        )

@router.delete("/attachment/{attachment_id}", status_code=status.HTTP_200_OK)
async def delete_attachment(
    attachment_id: int = Path(..., description="첨부 파일 ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = current_user["id"]
    
    try:
        success = SpecialService.delete_attachment(
            user_id=user_id,
            attachment_id=attachment_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="첨부 파일을 찾을 수 없거나 삭제에 실패했습니다."
            )
        
        return {"message": "첨부 파일이 성공적으로 삭제되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"첨부 파일 삭제 중 오류가 발생했습니다: {str(e)}"
        )