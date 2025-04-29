from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class User(BaseModel):
    login_id: str
    ibk_id: str
    name: str
    password: str
    hiearchy: str
    system_role: str
    team_id: Optional[int] = None
    activate: str = 'T'
    refresh_token: Optional[str] = None

class LoginModel(BaseModel):
    login_id: str
    password: str

class LogoutRequest(BaseModel):
    user_id: int

class Checklist(BaseModel):
    checklist_id: Optional[int] = None  # 수정: create시에는 ID가 없을 수 있으므로 Optional 추가
    question: str

class TermsNConditions(BaseModel):
    termsNconditions_id: Optional[int] = None  # 수정: create시에는 ID가 없을 수 있으므로 Optional 추가
    code: str
    query: str

class Contract(BaseModel):
    id: Optional[int] = None
    contract_name: str # = 파일 위치, 생성 규칙 : 
    file_name: str
    embedding_id: Optional[str] = None
    uploader_id: int
    keypoint_processer_id: Optional[int] = None
    checklist_processer_id: Optional[int] = None
    uploaded_at: Optional[datetime]
    keypoint_processed: Optional[datetime] = None
    checklist_processed: Optional[datetime] = None
    checklist_printable_file_path: Optional[str] = None
    current_state: int = 0

class Checklist_Results(BaseModel):
    id: Optional[int] = None
    contract_id: int
    checklist_id: int
    memo: Optional[str] = None

class Checklist_Results_Values(BaseModel):
    id: Optional[int] = None
    checklist_results_id: int
    clause_num: str
    located_pate: int