from dotenv import load_dotenv
import os 

# .env 파일 로드
load_dotenv()

# OCR 관련 설정
OCR_LICENSE_KEY = os.getenv("OCR_LICENSE_KEY", "your_default_license_key")
OCR_SERVER_ADDR = os.getenv("OCR_SERVER_ADDR", "http://ocr-server-address")
