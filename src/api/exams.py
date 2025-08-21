"""
Endpoints para gerenciamento de exames médicos.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional
import uuid
from datetime import datetime

from core.supabase_client import supabase_client
from services.storage_service import StorageService
from services.ocr_service import OCRService
from services.parser_service import biomarker_parser
from services.biomarker_service import biomarker_service
from models.exam import (
    ExamUploadRequest, ExamUploadResponse, ExamProcessingStatus,
    ExamStatus, ExamFileInfo
)
from core.logging import api_logger

router = APIRouter()


@router.post("/upload", response_model=ExamUploadResponse)
async def upload_exam(
    file: UploadFile = File(..., description="Arquivo do exame (PDF, PNG, JPG, TXT)"),
    patient_id: str = Form(..., description="ID do paciente"),
    user_id: str = Form(..., description="ID do usuário/médico")
):
    """
    Upload de exame médico com processamento OCR.
    
    Args:
        file: Arquivo do exame
        patient_id: ID do paciente
        user_id: ID do usuário/médico
        
    Returns:
        Dados do exame criado
    """
    try:
        # Validações básicas
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome do arquivo é obrigatório"
            )
        
        if not patient_id or not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID do paciente e usuário são obrigatórios"
            )
        
        # Lê conteúdo do arquivo
        file_content = await file.read()
        
        if not file_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Arquivo vazio"
            )
        
        # Inicializa serviços
        storage_service = StorageService(supabase_client)
        ocr_service = OCRService()
        
        # Upload para Supabase Storage
        upload_result = await storage_service.upload_file(
            file_content=file_content,
            file_name=file.filename,
            mime_type=file.content_type
        )
        
        if not upload_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro no upload: {upload_result['error']}"
            )
        
        # Gera ID único para o exame
        exam_id = str(uuid.uuid4())
        
        # Cria registro no banco
        exam_data = {
            "id": exam_id,
            "patient_id": patient_id,
            "user_id": user_id,
            "file_name": file.filename,
            "file_path": upload_result["file_path"],
            "file_size": upload_result["file_size"],
            "file_type": upload_result["mime_type"],
            "mime_type": upload_result["mime_type"],
            "status": ExamStatus.PENDING.value,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Insere na tabela exams
        try:
            result = supabase_client.get_table("exams").insert(exam_data).execute()
            
            if not result.data:
                raise Exception("Falha ao inserir exame no banco")
                
        except Exception as e:
            # Rollback: remove arquivo do storage se falhar no banco
            await storage_service.delete_file(upload_result["file_path"])
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao salvar exame: {str(e)}"
            )
        
        # Inicia processamento OCR em background
        asyncio.create_task(
            process_exam_background(
                exam_id=exam_id,
                file_content=file_content,
                mime_type=upload_result["mime_type"],
                file_name=file.filename
            )
        )
        
        # Log da operação
        api_logger.log_operation(
            operation="exam_upload",
            user_id=user_id,
            details={
                "exam_id": exam_id,
                "patient_id": patient_id,
                "file_name": file.filename,
                "file_size": upload_result["file_size"]
            }
        )
        
        return ExamUploadResponse(
            exam_id=exam_id,
            file_name=file.filename,
            file_size=upload_result["file_size"],
            file_type=upload_result["mime_type"],
            status=ExamStatus.PENDING,
            upload_timestamp=datetime.now(),
            message="Exame enviado com sucesso. Processamento OCR iniciado."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.log_error(
            error=str(e),
            operation="exam_upload",
            user_id=user_id if 'user_id' in locals() else None
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no upload do exame"
        )


@router.get("/{exam_id}/status", response_model=ExamProcessingStatus)
async def get_exam_status(exam_id: str, user_id: str):
    """
    Obtém status do processamento de um exame.
    
    Args:
        exam_id: ID do exame
        user_id: ID do usuário para validação
        
    Returns:
        Status atual do processamento
    """
    try:
        # Busca exame no banco
        result = supabase_client.get_table("exams").select("*").eq("id", exam_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exame não encontrado"
            )
        
        exam = result.data[0]
        
        # Valida acesso (médico só vê seus próprios exames)
        if exam["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado a este exame"
            )
        
        return ExamProcessingStatus(
            exam_id=exam_id,
            status=ExamStatus(exam["status"]),
            message=self._get_status_message(exam["status"]),
            processing_started_at=exam.get("processing_started_at"),
            processing_completed_at=exam.get("processing_completed_at")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.log_error(
            error=str(e),
            operation="get_exam_status",
            user_id=user_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter status do exame"
        )


@router.get("/{exam_id}/result")
async def get_exam_result(exam_id: str, user_id: str):
    """
    Obtém resultado completo de um exame.
    
    Args:
        exam_id: ID do exame
        user_id: ID do usuário para validação
        
    Returns:
        Resultado completo com OCR e biomarcadores
    """
    try:
        # Busca exame no banco
        result = supabase_client.get_table("exams").select("*").eq("id", exam_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exame não encontrado"
            )
        
        exam = result.data[0]
        
        # Valida acesso
        if exam["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado a este exame"
            )
        
        # Verifica se processamento foi concluído
        if exam["status"] != ExamStatus.COMPLETED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exame ainda não foi processado completamente"
            )
        
        # Busca biomarcadores relacionados
        biomarkers_result = supabase_client.get_table("biomarkers").select("*").eq("exam_id", exam_id).execute()
        biomarkers = biomarkers_result.data if biomarkers_result.data else []
        
        # Se não há biomarcadores mas o OCR foi concluído, processa novamente
        if not biomarkers and exam.get("ocr_text"):
            biomarker_result = await biomarker_service.process_exam_biomarkers(
                exam_id, 
                exam["ocr_text"]
            )
            
            if biomarker_result["success"]:
                biomarkers = biomarker_result["biomarkers"]
                # Atualiza o exame com o resumo
                if biomarker_result.get("summary"):
                    supabase_client.get_table("exams").update({
                        "biomarker_summary": biomarker_result["summary"]["summary_text"],
                        "updated_at": datetime.now().isoformat()
                    }).eq("id", exam_id).execute()
        
        # Busca informações do arquivo
        storage_service = StorageService(supabase_client)
        file_info = await storage_service.get_file_info(exam["file_path"])
        
        # Gera link assinado atualizado
        signed_url = await storage_service._generate_signed_url(exam["file_path"])
        
        # Monta resposta
        file_info_model = ExamFileInfo(
            file_name=exam["file_name"],
            file_path=exam["file_path"],
            file_size=exam["file_size"],
            mime_type=exam["mime_type"],
            uploaded_at=datetime.fromisoformat(exam["created_at"]),
            signed_url=signed_url,
            expires_at=datetime.now() + timedelta(seconds=storage_service.signed_url_expiry)
        )
        
        return {
            "exam_id": exam_id,
            "patient_id": exam["patient_id"],
            "user_id": exam["user_id"],
            "file_info": file_info_model,
            "status": ExamStatus(exam["status"]),
            "ocr_text": exam.get("ocr_text"),
            "ocr_confidence": exam.get("ocr_confidence"),
            "biomarkers": biomarkers,
            "processing_started_at": exam.get("processing_started_at"),
            "processing_completed_at": exam.get("processing_completed_at"),
            "created_at": datetime.fromisoformat(exam["created_at"]),
            "updated_at": datetime.fromisoformat(exam["updated_at"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.log_error(
            error=str(e),
            operation="get_exam_result",
            user_id=user_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter resultado do exame"
        )


async def process_exam_background(exam_id: str, file_content: bytes, mime_type: str, file_name: str):
    """
    Processa exame em background (OCR + parsing).
    
    Args:
        exam_id: ID do exame
        file_content: Conteúdo do arquivo
        mime_type: Tipo MIME
        file_name: Nome do arquivo
    """
    try:
        # Atualiza status para PROCESSING
        supabase_client.get_table("exams").update({
            "status": ExamStatus.PROCESSING.value,
            "processing_started_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }).eq("id", exam_id).execute()
        
        # Inicializa serviços
        ocr_service = OCRService()
        
        # Processa OCR
        ocr_result = await ocr_service.process_file_from_bytes(
            file_content=file_content,
            file_type=mime_type,
            file_name=file_name
        )
        
        if not ocr_result["success"]:
            # Falha no OCR
            supabase_client.get_table("exams").update({
                "status": ExamStatus.FAILED.value,
                "updated_at": datetime.now().isoformat()
            }).eq("id", exam_id).execute()
            
            api_logger.log_error(
                error=f"OCR falhou: {ocr_result['error']}",
                operation="exam_processing",
                details={"exam_id": exam_id}
            )
            return
        
        # Processa biomarcadores com análise completa
        biomarker_result = await biomarker_service.process_exam_biomarkers(
            exam_id, 
            ocr_result["ocr_text"]
        )
        
        # Atualiza exame com resultados
        update_data = {
            "status": ExamStatus.COMPLETED.value,
            "ocr_text": ocr_result["ocr_text"],
            "ocr_confidence": ocr_result["confidence"],
            "processing_completed_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Adiciona resumo de biomarcadores se disponível
        if biomarker_result["success"] and biomarker_result.get("summary"):
            update_data["biomarker_summary"] = biomarker_result["summary"]["summary_text"]
        
        supabase_client.get_table("exams").update(update_data).eq("id", exam_id).execute()
        
        # Log de sucesso
        api_logger.log_operation(
            operation="exam_processing_completed",
            details={
                "exam_id": exam_id,
                "ocr_confidence": ocr_result["confidence"],
                "biomarkers_found": biomarker_result.get("total_found", 0) if biomarker_result["success"] else 0,
                "abnormal_biomarkers": len([b for b in biomarker_result.get("biomarkers", []) if b.get("status") != "normal"]) if biomarker_result["success"] else 0
            }
        )
        
    except Exception as e:
        # Falha no processamento
        supabase_client.get_table("exams").update({
            "status": ExamStatus.FAILED.value,
            "updated_at": datetime.now().isoformat()
        }).eq("id", exam_id).execute()
        
        api_logger.log_error(
            error=str(e),
            operation="exam_processing",
            details={"exam_id": exam_id}
        )
    
    finally:
        # Limpa recursos do OCR
        ocr_service.cleanup()


def _get_status_message(status: str) -> str:
    """Retorna mensagem descritiva para cada status."""
    messages = {
        ExamStatus.PENDING.value: "Exame aguardando processamento",
        ExamStatus.PROCESSING.value: "Exame sendo processado (OCR em andamento)",
        ExamStatus.COMPLETED.value: "Processamento concluído com sucesso",
        ExamStatus.FAILED.value: "Falha no processamento"
    }
    return messages.get(status, "Status desconhecido")


# Import necessário para asyncio.create_task
import asyncio
from datetime import timedelta
