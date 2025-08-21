"""
Modelos Pydantic para pacientes.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date
from enum import Enum


class Gender(str, Enum):
    """Enum para gênero do paciente."""
    M = "M"
    F = "F"
    O = "O"  # Outro


class PatientCreate(BaseModel):
    """Dados para criação de paciente."""
    
    full_name: str = Field(..., min_length=3, description="Nome completo do paciente")
    cpf: str = Field(..., min_length=11, max_length=14, description="CPF do paciente")
    birth_date: date = Field(..., description="Data de nascimento")
    gender: Gender = Field(..., description="Gênero do paciente")
    phone: str = Field(..., description="Telefone de contato")
    address: str = Field(..., description="Endereço completo")
    
    @validator('cpf')
    def validate_cpf(cls, v):
        # Remove caracteres não numéricos
        cpf_clean = ''.join(filter(str.isdigit, v))
        
        if len(cpf_clean) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        
        # Validação básica de CPF
        if cpf_clean == cpf_clean[0] * 11:
            raise ValueError('CPF inválido')
        
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "full_name": "João Silva Santos",
                "cpf": "12345678901",
                "birth_date": "1985-03-15",
                "gender": "M",
                "phone": "(11) 99999-9999",
                "address": "Rua das Flores, 123 - São Paulo/SP"
            }
        }


class PatientUpdate(BaseModel):
    """Dados para atualização de paciente."""
    
    full_name: Optional[str] = Field(None, min_length=3, description="Nome completo do paciente")
    cpf: Optional[str] = Field(None, min_length=11, max_length=14, description="CPF do paciente")
    birth_date: Optional[date] = Field(None, description="Data de nascimento")
    gender: Optional[Gender] = Field(None, description="Gênero do paciente")
    phone: Optional[str] = Field(None, description="Telefone de contato")
    address: Optional[str] = Field(None, description="Endereço completo")
    
    @validator('cpf')
    def validate_cpf(cls, v):
        if v is None:
            return v
            
        # Remove caracteres não numéricos
        cpf_clean = ''.join(filter(str.isdigit, v))
        
        if len(cpf_clean) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        
        # Validação básica de CPF
        if cpf_clean == cpf_clean[0] * 11:
            raise ValueError('CPF inválido')
        
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "full_name": "João Silva Santos",
                "phone": "(11) 88888-8888"
            }
        }


class PatientResponse(BaseModel):
    """Resposta com dados do paciente."""
    
    id: str = Field(..., description="ID único do paciente")
    full_name: str = Field(..., description="Nome completo do paciente")
    cpf: str = Field(..., description="CPF do paciente")
    birth_date: date = Field(..., description="Data de nascimento")
    gender: Gender = Field(..., description="Gênero do paciente")
    phone: str = Field(..., description="Telefone de contato")
    address: str = Field(..., description="Endereço completo")
    doctor_id: str = Field(..., description="ID do médico responsável")
    created_at: str = Field(..., description="Data de criação")
    updated_at: str = Field(..., description="Data da última atualização")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "patient-123",
                "full_name": "João Silva Santos",
                "cpf": "12345678901",
                "birth_date": "1985-03-15",
                "gender": "M",
                "phone": "(11) 99999-9999",
                "address": "Rua das Flores, 123 - São Paulo/SP",
                "doctor_id": "doctor-456",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }


class PatientListResponse(BaseModel):
    """Resposta com lista de pacientes."""
    
    patients: List[PatientResponse] = Field(..., description="Lista de pacientes")
    total: int = Field(..., description="Total de pacientes")
    skip: int = Field(..., description="Número de registros pulados")
    limit: int = Field(..., description="Número máximo de registros")
    has_next: bool = Field(..., description="Indica se há mais páginas")
    has_prev: bool = Field(..., description="Indica se há páginas anteriores")
    
    class Config:
        schema_extra = {
            "example": {
                "patients": [
                    {
                        "id": "patient-123",
                        "full_name": "João Silva Santos",
                        "cpf": "12345678901",
                        "birth_date": "1985-03-15",
                        "gender": "M",
                        "phone": "(11) 99999-9999",
                        "address": "Rua das Flores, 123 - São Paulo/SP",
                        "doctor_id": "doctor-456",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z"
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 10,
                "has_next": False,
                "has_prev": False
            }
        }


class PatientSearchParams(BaseModel):
    """Parâmetros para busca de pacientes."""
    
    search: Optional[str] = Field(None, description="Termo de busca (nome ou CPF)")
    skip: int = Field(0, ge=0, description="Número de registros para pular")
    limit: int = Field(10, ge=1, le=100, description="Número máximo de registros")
    
    class Config:
        schema_extra = {
            "example": {
                "search": "João Silva",
                "skip": 0,
                "limit": 20
            }
        }
