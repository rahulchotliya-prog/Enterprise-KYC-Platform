import random
import re
from src.exceptions import AppException

ALLOWED_FILE_TYPES = [
    "application/pdf",
    "image/jpeg",
    "image/png"
]

MAX_FILE_SIZE = 5 * 1024 * 1024

def validate_file_type(content_type:str):
    if content_type not in ALLOWED_FILE_TYPES:
        raise AppException(status_code=400, message="Unsupported file type")
    

def validate_file_size(file_size:int):
    if file_size > MAX_FILE_SIZE:
        raise AppException(status_code=400, message="File size exceeds the maximum limit of 5MB")
    

def chunk_content(content:bytes,chunk_size:int = 1024*1024):
    for i in range(0,len(content),chunk_size):
        yield content[i:i+chunk_size]


def simulate_ocr_extraction():
    invoices = [
        {
            "invoice_number": "INV-001",
            "amount":5000,
            "vendor":"Amazon"
        },
        {
            "invoice_number": "INV-002",
            "amount":3000,
            "vendor":"Walmart"
        },
        {
            "invoice_number": "INV-003",
            "amount":7000,
            "vendor":"Target"
        }
    ]
    return random.choice(invoices)

def validate_extracted_data(data:dict):
    
    invoice_patter = r"^INV-\d+$"

    if not re.match(invoice_patter,data["invoice_number"]):
        raise AppException(status_code=400, message="Invalid invoice number format")
    return True