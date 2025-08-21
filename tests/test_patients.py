"""
Testes para o módulo de pacientes.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException
from datetime import date

from src.models.patient import (
    PatientCreate, PatientUpdate, PatientResponse,
    PatientListResponse, PatientSearchParams
)
from src.api.patients import (
    create_patient, list_patients, get_patient,
    update_patient, delete_patient, get_patient_exams
)


class TestPatientModels:
    """Testes para os modelos de paciente."""
    
    def test_patient_create_request_valid(self):
        """Testa criação de PatientCreateRequest válido."""
        data = {
            "full_name": "João Silva",
            "date_of_birth": "1990-01-01",
            "cpf": "12345678901",
            "phone": "11999999999",
            "email": "joao@example.com"
        }
        
        patient = PatientCreateRequest(**data)
        assert patient.full_name == "João Silva"
        assert patient.date_of_birth == "1990-01-01"
        assert patient.cpf == "12345678901"
        assert patient.phone == "11999999999"
        assert patient.email == "joao@example.com"
    
    def test_patient_create_request_invalid_cpf(self):
        """Testa criação com CPF inválido."""
        data = {
            "full_name": "João Silva",
            "date_of_birth": "1990-01-01",
            "cpf": "123",  # CPF muito curto
            "phone": "11999999999",
            "email": "joao@example.com"
        }
        
        with pytest.raises(ValueError):
            PatientCreateRequest(**data)
    
    def test_patient_create_request_invalid_email(self):
        """Testa criação com email inválido."""
        data = {
            "full_name": "João Silva",
            "date_of_birth": "1990-01-01",
            "cpf": "12345678901",
            "phone": "11999999999",
            "email": "email-invalido"  # Email inválido
        }
        
        with pytest.raises(ValueError):
            PatientCreateRequest(**data)
    
    def test_patient_update_request_partial(self):
        """Testa atualização parcial de paciente."""
        data = {
            "full_name": "João Silva Atualizado"
        }
        
        patient = PatientUpdateRequest(**data)
        assert patient.full_name == "João Silva Atualizado"
        assert patient.date_of_birth is None
        assert patient.cpf is None
        assert patient.phone is None
        assert patient.email is None
    
    def test_patient_response_valid(self):
        """Testa criação de PatientResponse válido."""
        data = {
            "id": "patient-123",
            "full_name": "João Silva",
            "date_of_birth": "1990-01-01",
            "cpf": "12345678901",
            "phone": "11999999999",
            "email": "joao@example.com",
            "doctor_id": "doctor-456",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        patient = PatientResponse(**data)
        assert patient.id == "patient-123"
        assert patient.full_name == "João Silva"
        assert patient.doctor_id == "doctor-456"


class TestPatientAPI:
    """Testes para os endpoints de pacientes."""
    
    @pytest.fixture
    def mock_supabase(self):
        """Mock do cliente Supabase."""
        with patch("src.api.patients.supabase_client") as mock_client:
            # Mock das operações básicas
            mock_table = Mock()
            mock_client.get_table.return_value = mock_table
            
            # Mock para insert
            mock_insert = Mock()
            mock_insert.execute.return_value.data = [{"id": "patient-123"}]
            mock_table.insert.return_value = mock_insert
            
            # Mock para select
            mock_select = Mock()
            mock_select.eq.return_value.execute.return_value.data = [
                {
                    "id": "patient-123",
                    "full_name": "João Silva",
                    "date_of_birth": "1990-01-01",
                    "cpf": "12345678901",
                    "phone": "11999999999",
                    "email": "joao@example.com",
                    "doctor_id": "doctor-456",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z"
                }
            ]
            mock_table.select.return_value = mock_select
            
            # Mock para update
            mock_update = Mock()
            mock_update.eq.return_value.execute.return_value.data = [{"id": "patient-123"}]
            mock_table.update.return_value = mock_update
            
            # Mock para delete
            mock_delete = Mock()
            mock_delete.eq.return_value.execute.return_value.data = [{"id": "patient-123"}]
            mock_table.delete.return_value = mock_delete
            
            yield mock_client
    
    @pytest.fixture
    def mock_auth(self):
        """Mock da autenticação."""
        with patch("src.api.patients.get_current_user_id") as mock_get_user:
            mock_get_user.return_value = "doctor-456"
            yield mock_get_user
    
    async def test_create_patient_success(self, mock_supabase, mock_auth):
        """Testa criação bem-sucedida de paciente."""
        patient_data = PatientCreateRequest(
            full_name="João Silva",
            date_of_birth="1990-01-01",
            cpf="12345678901",
            phone="11999999999",
            email="joao@example.com"
        )
        
        result = await create_patient(patient_data)
        
        assert result["success"] is True
        assert result["patient"]["id"] == "patient-123"
        assert result["patient"]["full_name"] == "João Silva"
        assert result["patient"]["doctor_id"] == "doctor-456"
    
    async def test_create_patient_duplicate_cpf(self, mock_supabase, mock_auth):
        """Testa criação com CPF duplicado."""
        # Mock para simular CPF duplicado
        mock_supabase.get_table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"id": "existing-patient"}
        ]
        
        patient_data = PatientCreateRequest(
            full_name="João Silva",
            date_of_birth="1990-01-01",
            cpf="12345678901",
            phone="11999999999",
            email="joao@example.com"
        )
        
        result = await create_patient(patient_data)
        
        assert result["success"] is False
        assert "CPF já cadastrado" in result["error"]
    
    async def test_list_patients_success(self, mock_supabase, mock_auth):
        """Testa listagem bem-sucedida de pacientes."""
        result = await list_patients()
        
        assert result["success"] is True
        assert len(result["patients"]) == 1
        assert result["patients"][0]["full_name"] == "João Silva"
    
    async def test_get_patient_success(self, mock_supabase, mock_auth):
        """Testa busca bem-sucedida de paciente."""
        result = await get_patient("patient-123")
        
        assert result["success"] is True
        assert result["patient"]["id"] == "patient-123"
        assert result["patient"]["full_name"] == "João Silva"
    
    async def test_get_patient_not_found(self, mock_supabase, mock_auth):
        """Testa busca de paciente inexistente."""
        # Mock para simular paciente não encontrado
        mock_supabase.get_table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        
        result = await get_patient("patient-999")
        
        assert result["success"] is False
        assert "Paciente não encontrado" in result["error"]
    
    async def test_get_patient_unauthorized(self, mock_supabase, mock_auth):
        """Testa acesso não autorizado a paciente."""
        # Mock para simular paciente de outro médico
        mock_supabase.get_table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {
                "id": "patient-123",
                "full_name": "João Silva",
                "doctor_id": "other-doctor"  # Médico diferente
            }
        ]
        
        result = await get_patient("patient-123")
        
        assert result["success"] is False
        assert "Acesso não autorizado" in result["error"]
    
    async def test_update_patient_success(self, mock_supabase, mock_auth):
        """Testa atualização bem-sucedida de paciente."""
        update_data = PatientUpdateRequest(full_name="João Silva Atualizado")
        
        result = await update_patient("patient-123", update_data)
        
        assert result["success"] is True
        assert result["patient"]["id"] == "patient-123"
    
    async def test_delete_patient_success(self, mock_supabase, mock_auth):
        """Testa exclusão bem-sucedida de paciente."""
        result = await delete_patient("patient-123")
        
        assert result["success"] is True
        assert result["message"] == "Paciente excluído com sucesso"
    
    async def test_get_patient_exams_success(self, mock_supabase, mock_auth):
        """Testa busca bem-sucedida de exames do paciente."""
        # Mock para simular exames do paciente
        mock_supabase.get_table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {
                "id": "exam-123",
                "patient_id": "patient-123",
                "file_name": "exame.pdf",
                "status": "completed",
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
        
        result = await get_patient_exams("patient-123")
        
        assert result["success"] is True
        assert len(result["exams"]) == 1
        assert result["exams"][0]["id"] == "exam-123"
        assert result["exams"][0]["file_name"] == "exame.pdf"


class TestPatientSearchParams:
    """Testes para parâmetros de busca de pacientes."""
    
    def test_search_params_default(self):
        """Testa parâmetros de busca com valores padrão."""
        params = PatientSearchParams()
        
        assert params.page == 1
        assert params.limit == 10
        assert params.search is None
        assert params.sort_by == "created_at"
        assert params.sort_order == "desc"
    
    def test_search_params_custom(self):
        """Testa parâmetros de busca personalizados."""
        params = PatientSearchParams(
            page=2,
            limit=20,
            search="João",
            sort_by="full_name",
            sort_order="asc"
        )
        
        assert params.page == 2
        assert params.limit == 20
        assert params.search == "João"
        assert params.sort_by == "full_name"
        assert params.sort_order == "asc"
    
    def test_search_params_validation(self):
        """Testa validação de parâmetros."""
        with pytest.raises(ValueError):
            PatientSearchParams(page=0)  # Página deve ser > 0
        
        with pytest.raises(ValueError):
            PatientSearchParams(limit=0)  # Limite deve ser > 0
        
        with pytest.raises(ValueError):
            PatientSearchParams(sort_order="invalid")  # Ordem inválida


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
