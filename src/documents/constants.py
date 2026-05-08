from enum import Enum


class DocumentStatus(str,Enum):
    UPLOADED = "UPLOADED"

    PROCESSING = "PROCESSING"

    VERIFIED = "VERIFIED"

    REJECTED = "REJECTED"