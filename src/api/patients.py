"""
Endpoints para gestão de pacientes.
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.core.supabase_client import supabase_client
from src.core.logging import api_logger
from src.models.patient import (
    PatientCreate, PatientUpdate, PatientResponse,
    PatientListResponse, PatientSearchParams
)

router = APIRouter()
security = HTTPBearer()


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Middleware para obter ID do usuário autenticado.
    
    Args:
        credentials: Token de autorização
        
    Returns:
        ID do usuário autenticado
        
    Raises:
        HTTPException: Se token inválido
    """
    try:
        user_result = await supabase_client().get_current_user(credentials.credentials)
        
        if not user_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado"
            )
        
        return user_result["user"]["id"]
        
    except Exception as e:
        api_logger.log_error(
            error=str(e),
            operation="get_current_user_id"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erro na autenticação"
        )


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_data: PatientCreate,
    current_user_id: str = Depends(get_current_user_id)
) -> PatientResponse:
    """
    Cria um novo paciente.
    
    Args:
        patient_data: Dados do paciente
        current_user_id: ID do usuário autenticado
        
    Returns:
        Paciente criado
    """
    try:
        # Valida CPF único
        existing_patient = supabase_client().get_table("patients").select("id").eq("cpf", patient_data.cpf).execute()
        
        if existing_patient.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado"
            )
        
        # Prepara dados para inserção
        insert_data = patient_data.dict()
        insert_data["doctor_id"] = current_user_id
        insert_data["created_at"] = datetime.now().isoformat()
        insert_data["updated_at"] = datetime.now().isoformat()
        
        # Insere paciente no banco
        result = supabase_client().get_table("patients").insert(insert_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao criar paciente"
            )
        
        created_patient = result.data[0]
        
        # Log da operação
        api_logger.log_operation(
            operation="patient_creation",
            details={
                "patient_id": created_patient["id"],
                "doctor_id": current_user_id,
                "cpf": patient_data.cpf
            }
        )
        
        return PatientResponse(
            id=created_patient["id"],
            full_name=created_patient["full_name"],
            cpf=created_patient["cpf"],
            birth_date=created_patient["birth_date"],
            gender=created_patient["gender"],
            phone=created_patient["phone"],
            address=created_patient["address"],
            doctor_id=created_patient["doctor_id"],
            created_at=created_patient["created_at"],
            updated_at=created_patient["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.log_error(
            error=str(e),
            operation="patient_creation",
            details={"doctor_id": current_user_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )


@router.get("/", response_model=PatientListResponse)
async def list_patients(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros"),
    search: Optional[str] = Query(None, description="Termo de busca (nome ou CPF)"),
    current_user_id: str = Depends(get_current_user_id)
) -> PatientListResponse:
    """
    Lista pacientes do médico autenticado.
    
    Args:
        skip: Número de registros para pular
        limit: Número máximo de registros
        search: Termo de busca opcional
        current_user_id: ID do usuário autenticado
        
    Returns:
        Lista de pacientes com paginação
    """
    try:
        # Constrói query base
        query = supabase_client().get_table("patients").select("*").eq("doctor_id", current_user_id)
        
        # Aplica filtro de busca se fornecido
        if search:
            query = query.or_(f"full_name.ilike.%{search}%,cpf.ilike.%{search}%")
        
        # Aplica paginação
        query = query.range(skip, skip + limit - 1).order("created_at", desc=True)
        
        # Executa query
        result = query.execute()
        
        if not result.data:
            return PatientListResponse(
                patients=[],
                total=0,
                skip=skip,
                limit=limit,
                has_next=False,
                has_prev=False
            )
        
        # Conta total de registros para paginação
        count_query = supabase_client.get_table("patients").select("id", count="exact").eq("doctor_id", current_user_id)
        if search:
            count_query = count_query.or_(f"full_name.ilike.%{search}%,cpf.ilike.%{search}%")
        
        count_result = count_query.execute()
        total_count = count_result.count if hasattr(count_result, 'count') else len(result.data)
        
        # Constrói resposta
        patients = [
            PatientResponse(
                id=patient["id"],
                full_name=patient["full_name"],
                cpf=patient["cpf"],
                birth_date=patient["birth_date"],
                gender=patient["gender"],
                phone=patient["phone"],
                address=patient["address"],
                doctor_id=patient["doctor_id"],
                created_at=patient["created_at"],
                updated_at=patient["updated_at"]
            )
            for patient in result.data
        ]
        
        return PatientListResponse(
            patients=patients,
            total=total_count,
            skip=skip,
            limit=limit,
            has_next=skip + limit < total_count,
            has_prev=skip > 0
        )
        
    except Exception as e:
        api_logger.log_error(
            error=str(e),
            operation="patient_listing",
            details={"doctor_id": current_user_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    current_user_id: str = Depends(get_current_user_id)
) -> PatientResponse:
    """
    Obtém um paciente específico.
    
    Args:
        patient_id: ID do paciente
        current_user_id: ID do usuário autenticado
        
    Returns:
        Dados do paciente
    """
    try:
        # Busca paciente no banco
        result = supabase_client.get_table("patients").select("*").eq("id", patient_id).eq("doctor_id", current_user_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paciente não encontrado"
            )
        
        patient = result.data[0]
        
        return PatientResponse(
            id=patient["id"],
            full_name=patient["full_name"],
            cpf=patient["cpf"],
            birth_date=patient["birth_date"],
            gender=patient["gender"],
            phone=patient["phone"],
            address=patient["address"],
            doctor_id=patient["doctor_id"],
            created_at=patient["created_at"],
            updated_at=patient["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.log_error(
            error=str(e),
            operation="patient_retrieval",
            details={"patient_id": patient_id, "doctor_id": current_user_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str,
    patient_update: PatientUpdate,
    current_user_id: str = Depends(get_current_user_id)
) -> PatientResponse:
    """
    Atualiza um paciente.
    
    Args:
        patient_id: ID do paciente
        patient_update: Dados para atualização
        current_user_id: ID do usuário autenticado
        
    Returns:
        Paciente atualizado
    """
    try:
        # Verifica se paciente existe e pertence ao médico
        existing_patient = supabase_client.get_table("patients").select("id").eq("id", patient_id).eq("doctor_id", current_user_id).execute()
        
        if not existing_patient.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paciente não encontrado"
            )
        
        # Verifica CPF único se estiver sendo alterado
        if patient_update.cpf:
            cpf_check = supabase_client.get_table("patients").select("id").eq("cpf", patient_update.cpf).neq("id", patient_id).execute()
            
            if cpf_check.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CPF já cadastrado para outro paciente"
                )
        
        # Prepara dados para atualização
        update_data = patient_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.now().isoformat()
        
        # Atualiza paciente no banco
        result = supabase_client.get_table("patients").update(update_data).eq("id", patient_id).eq("doctor_id", current_user_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar paciente"
            )
        
        updated_patient = result.data[0]
        
        # Log da operação
        api_logger.log_operation(
            operation="patient_update",
            details={
                "patient_id": patient_id,
                "doctor_id": current_user_id,
                "updated_fields": list(update_data.keys())
            }
        )
        
        return PatientResponse(
            id=updated_patient["id"],
            full_name=updated_patient["full_name"],
            cpf=updated_patient["cpf"],
            birth_date=updated_patient["birth_date"],
            gender=updated_patient["gender"],
            phone=updated_patient["phone"],
            address=updated_patient["address"],
            doctor_id=updated_patient["doctor_id"],
            created_at=updated_patient["created_at"],
            updated_at=updated_patient["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.log_error(
            error=str(e),
            operation="patient_update",
            details={"patient_id": patient_id, "doctor_id": current_user_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )


@router.delete("/{patient_id}")
async def delete_patient(
    patient_id: str,
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Remove um paciente.
    
    Args:
        patient_id: ID do paciente
        current_user_id: ID do usuário autenticado
        
    Returns:
        Confirmação de remoção
    """
    try:
        # Verifica se paciente existe e pertence ao médico
        existing_patient = supabase_client.get_table("patients").select("id").eq("id", patient_id).eq("doctor_id", current_user_id).execute()
        
        if not existing_patient.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paciente não encontrado"
            )
        
        # Verifica se há exames associados
        exams_check = supabase_client.get_table("exams").select("id").eq("patient_id", patient_id).limit(1).execute()
        
        if exams_check.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível remover paciente com exames associados"
            )
        
        # Remove paciente do banco
        result = supabase_client.get_table("patients").delete().eq("id", patient_id).eq("doctor_id", current_user_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao remover paciente"
            )
        
        # Log da operação
        api_logger.log_operation(
            operation="patient_deletion",
            details={
                "patient_id": patient_id,
                "doctor_id": current_user_id
            }
        )
        
        return {
            "success": True,
            "message": "Paciente removido com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.log_error(
            error=str(e),
            operation="patient_deletion",
            details={"patient_id": patient_id, "doctor_id": current_user_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )


@router.get("/{patient_id}/exams")
async def get_patient_exams(
    patient_id: str,
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros"),
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Lista exames de um paciente específico.
    
    Args:
        patient_id: ID do paciente
        skip: Número de registros para pular
        limit: Número máximo de registros
        current_user_id: ID do usuário autenticado
        
    Returns:
        Lista de exames do paciente
    """
    try:
        # Verifica se paciente existe e pertence ao médico
        patient_check = supabase_client.get_table("patients").select("id").eq("id", patient_id).eq("doctor_id", current_user_id).execute()
        
        if not patient_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paciente não encontrado"
            )
        
        # Busca exames do paciente
        result = supabase_client.get_table("exams").select("*").eq("patient_id", patient_id).range(skip, skip + limit - 1).order("created_at", desc=True).execute()
        
        if not result.data:
            return {
                "exams": [],
                "total": 0,
                "skip": skip,
                "limit": limit,
                "has_next": False,
                "has_prev": False
            }
        
        # Conta total de exames
        count_result = supabase_client.get_table("exams").select("id", count="exact").eq("patient_id", patient_id).execute()
        total_count = count_result.count if hasattr(count_result, 'count') else len(result.data)
        
        return {
            "exams": result.data,
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "has_next": skip + limit < total_count,
            "has_prev": skip > 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.log_error(
            error=str(e),
            operation="patient_exams_retrieval",
            details={"patient_id": patient_id, "doctor_id": current_user_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )
