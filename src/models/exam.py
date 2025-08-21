"""
Modelos Pydantic para exames médicos.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class FileType(str, Enum):
    """Tipos de arquivo suportados."""
    PDF = "application/pdf"
    PNG = "image/png"
    JPEG = "image/jpeg"
    JPG = "image/jpeg"
    TXT = "text/plain"


class ExamStatus(str, Enum):
    """Status do processamento do exame."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ExamUploadRequest(BaseModel):
    """Request para upload de exame."""
    patient_id: str = Field(..., description="ID do paciente")
    file_type: Optional[str] = Field(None, description="Tipo do arquivo (inferido automaticamente)")
    
    @validator('patient_id')
    def validate_patient_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("ID do paciente é obrigatório")
        return v.strip()


class ExamUploadResponse(BaseModel):
    """Response do upload de exame."""
    exam_id: str = Field(..., description="ID único do exame")
    file_name: str = Field(..., description="Nome do arquivo")
    file_size: int = Field(..., description="Tamanho do arquivo em bytes")
    file_type: str = Field(..., description="Tipo MIME do arquivo")
    status: ExamStatus = Field(..., description="Status do processamento")
    upload_timestamp: datetime = Field(..., description="Timestamp do upload")
    message: str = Field(..., description="Mensagem de confirmação")


class ExamProcessingStatus(BaseModel):
    """Status do processamento do exame."""
    exam_id: str = Field(..., description="ID do exame")
    status: ExamStatus = Field(..., description="Status atual")
    progress: Optional[float] = Field(None, ge=0, le=100, description="Progresso em %")
    message: Optional[str] = Field(None, description="Mensagem de status")
    processing_started_at: Optional[datetime] = Field(None, description="Início do processamento")
    processing_completed_at: Optional[datetime] = Field(None, description="Fim do processamento")
    error_message: Optional[str] = Field(None, description="Mensagem de erro se houver")


class ExamFileInfo(BaseModel):
    """Informações do arquivo do exame."""
    file_name: str = Field(..., description="Nome original do arquivo")
    file_path: str = Field(..., description="Caminho no storage")
    file_size: int = Field(..., description="Tamanho em bytes")
    mime_type: str = Field(..., description="Tipo MIME")
    uploaded_at: datetime = Field(..., description="Data/hora do upload")
    signed_url: Optional[str] = Field(None, description="URL assinada para download")
    expires_at: Optional[datetime] = Field(None, description="Expiração da URL")


class Exam(BaseModel):
    """Modelo completo do exame."""
    id: str = Field(..., description="ID único do exame")
    patient_id: str = Field(..., description="ID do paciente")
    user_id: str = Field(..., description="ID do usuário/médico")
    file_info: ExamFileInfo = Field(..., description="Informações do arquivo")
    status: ExamStatus = Field(..., description="Status do processamento")
    ocr_text: Optional[str] = Field(None, description="Texto extraído via OCR")
    ocr_confidence: Optional[float] = Field(None, ge=0, le=100, description="Confiança do OCR")
    processing_started_at: Optional[datetime] = Field(None, description="Início do processamento")
    processing_completed_at: Optional[datetime] = Field(None, description="Fim do processamento")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ExamListResponse(BaseModel):
    """Response para listagem de exames."""
    exams: List[Exam] = Field(..., description="Lista de exames")
    total: int = Field(..., description="Total de exames")
    page: int = Field(..., description="Página atual")
    per_page: int = Field(..., description="Itens por página")
    has_next: bool = Field(..., description="Tem próxima página")
    has_prev: bool = Field(..., description="Tem página anterior")
