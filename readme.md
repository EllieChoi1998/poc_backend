# Backend Server Setup Guide 🚀

<div align="right">
    <a href="#한국어-가이드">🇰🇷 한국어</a> | <a href="#english-guide">🇺🇸 English</a>
</div>

## English Guide

### Project Setup and Installation

#### Prerequisites
- Python 3.8+ recommended
- pip package manager

#### Virtual Environment Setup (Recommended)
```bash
# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

#### Install Dependencies
```bash
# Install dependencies from requirements file
pip install -r requirements.txt
```

#### Alternative Direct Installation
If you prefer installing packages directly:
```bash
pip install fastapi uvicorn mysql-connector-python python-multipart python-jose passlib sqlalchemy
```

#### Troubleshooting
- Ensure you have the latest pip: `python -m pip install --upgrade pip`
- If you encounter SSL certificate issues, try: `pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt`

### How to Run Back-end Server?

#### Linux Environment Setup
Simply run the following command:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### WSL-Ubuntu Environment Configuration
If you're using WSL-Ubuntu, you may need to enable firewalls and set port-forwarding rules:

1. Open PowerShell as Administrator and execute:
```powershell
netsh interface portproxy add v4tov4 listenport=8000 connectport=8000 connectaddress=172.29.240.76
netsh advfirewall firewall add rule name="WSL FastAPI" dir=in action=allow protocol=TCP localport=8000 
```

#### Database Requirements
- **Recommended Database**: MySQL
- Create a database named `mydb`
- Default credentials:
  - User: `root`
  - Password: `admin`

> ⚠️ If using different database settings, modify `database.py` accordingly.

---

## 한국어 가이드

### 프로젝트 설정 및 설치

#### 사전 요구사항
- Python 3.8+ 권장
- pip 패키지 관리자

#### 가상 환경 설정 (권장)
```bash
# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

#### 종속성 설치
```bash
# requirements 파일에서 종속성 설치
pip install -r requirements.txt
```

#### 대안적 직접 설치
패키지를 직접 설치하려면:
```bash
pip install fastapi uvicorn mysql-connector-python python-multipart python-jose passlib sqlalchemy
```

#### 문제 해결
- 최신 pip 확인: `python -m pip install --upgrade pip`
- SSL 인증서 문제 발생 시: `pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt`

### 백엔드 서버 실행 방법?

#### Linux 환경 설정
다음 명령어를 실행하세요:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### WSL-Ubuntu 환경 구성
WSL-Ubuntu를 사용하는 경우, 방화벽을 활성화하고 포트 포워딩 규칙을 설정해야 합니다:

1. 관리자 권한으로 PowerShell을 열고 다음을 실행하세요:
```powershell
netsh interface portproxy add v4tov4 listenport=8000 connectport=8000 connectaddress=172.29.240.76
netsh advfirewall firewall add rule name="WSL FastAPI" dir=in action=allow protocol=TCP localport=8000 
```

#### 데이터베이스 요구사항
- **권장 데이터베이스**: MySQL
- `mydb`라는 이름의 데이터베이스 생성
- 기본 자격 증명:
  - 사용자: `root`
  - 비밀번호: `admin`

> ⚠️ 다른 데이터베이스 설정을 사용하는 경우, `database.py`를 수정하세요.