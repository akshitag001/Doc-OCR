from pydantic import BaseModel
from typing import Optional, Dict, Literal
from datetime import datetime


class HolderInfo(BaseModel):
    name: Optional[str] = None
    fatherName: Optional[str] = None
    dob: Optional[str] = None


class CredentialInfo(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    year: Optional[str] = None
    cgpa: Optional[str] = None


class IssuerInfo(BaseModel):
    name: Optional[str] = None


class ExtractionResult(BaseModel):
    id: str
    status: Literal["pending", "processing", "completed", "failed"]
    filename: str
    documentType: Optional[str] = None
    holder: Optional[HolderInfo] = None
    credential: Optional[CredentialInfo] = None
    issuer: Optional[IssuerInfo] = None
    confidence: Dict[str, float] = {}
    rawText: Optional[str] = None
    errorMessage: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DocumentResponse(BaseModel):
    id: str
    filename: str
    status: str
    createdAt: str
