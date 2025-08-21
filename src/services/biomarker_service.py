"""
Serviço para processamento e análise de biomarcadores médicos.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import asyncio

from core.supabase_client import supabase_client
from services.parser_service import biomarker_parser
from core.logging import api_logger


class BiomarkerService:
    """Serviço para análise e comparação de biomarcadores."""
    
    def __init__(self):
        self.parser = biomarker_parser
    
    async def process_exam_biomarkers(self, exam_id: str, ocr_text: str) -> Dict[str, Any]:
        """
        Processa biomarcadores de um exame completo.
        
        Args:
            exam_id: ID do exame
            ocr_text: Texto extraído via OCR
            
        Returns:
            Dict com biomarcadores processados e analisados
        """
        try:
            # Extrai biomarcadores do texto
            parsing_result = await self.parser.parse_text(ocr_text)
            
            if not parsing_result["success"]:
                return {
                    "success": False,
                    "error": f"Falha no parsing: {parsing_result.get('error', 'Erro desconhecido')}"
                }
            
            # Busca ranges de referência
            reference_ranges = await self._get_reference_ranges()
            
            # Analisa cada biomarcador
            analyzed_biomarkers = []
            for biomarker in parsing_result["biomarkers"]:
                analyzed = await self._analyze_biomarker(
                    biomarker, 
                    reference_ranges,
                    exam_id
                )
                analyzed_biomarkers.append(analyzed)
            
            # Gera resumo
            summary = self._generate_summary(analyzed_biomarkers)
            
            # Salva biomarcadores no banco
            await self._save_biomarkers(exam_id, analyzed_biomarkers)
            
            # Log da operação
            api_logger.log_operation(
                operation="biomarker_analysis",
                details={
                    "exam_id": exam_id,
                    "total_biomarkers": len(analyzed_biomarkers),
                    "abnormal_count": len([b for b in analyzed_biomarkers if b["status"] != "normal"])
                }
            )
            
            return {
                "success": True,
                "biomarkers": analyzed_biomarkers,
                "summary": summary,
                "total_found": len(analyzed_biomarkers),
                "analysis_confidence": parsing_result.get("parsing_confidence", 0)
            }
            
        except Exception as e:
            api_logger.log_error(
                error=str(e),
                operation="biomarker_analysis",
                details={"exam_id": exam_id}
            )
            return {"success": False, "error": str(e)}
    
    async def _get_reference_ranges(self) -> List[Dict[str, Any]]:
        """
        Obtém ranges de referência do banco.
        
        Returns:
            Lista de ranges de referência
        """
        try:
            result = supabase_client.get_table("reference_ranges").select("*").eq("is_active", True).execute()
            return result.data if result.data else []
        except Exception as e:
            api_logger.log_error(
                error=str(e),
                operation="get_reference_ranges"
            )
            return []
    
    async def _analyze_biomarker(
        self, 
        biomarker: Dict[str, Any], 
        reference_ranges: List[Dict[str, Any]],
        exam_id: str
    ) -> Dict[str, Any]:
        """
        Analisa um biomarcador individual.
        
        Args:
            biomarker: Dados do biomarcador
            reference_ranges: Ranges de referência
            exam_id: ID do exame
            
        Returns:
            Biomarcador analisado com status e interpretação
        """
        try:
            # Busca range de referência apropriado
            reference_range = self._find_matching_reference(biomarker, reference_ranges)
            
            # Analisa o valor
            analysis = self._analyze_value(
                biomarker["value"], 
                biomarker["unit"], 
                reference_range
            )
            
            # Monta resultado completo
            analyzed_biomarker = {
                "exam_id": exam_id,
                "name": biomarker["raw_name"],
                "normalized_name": biomarker["normalized_name"],
                "value": biomarker["value"],
                "unit": biomarker["unit"],
                "reference_range_id": reference_range["id"] if reference_range else None,
                "status": analysis["status"],
                "confidence_score": biomarker["confidence"],
                "raw_text": biomarker["raw_text"],
                "min_reference": reference_range["min_value"] if reference_range else None,
                "max_reference": reference_range["max_value"] if reference_range else None,
                "interpretation": analysis["interpretation"],
                "severity": analysis["severity"],
                "created_at": datetime.now().isoformat()
            }
            
            return analyzed_biomarker
            
        except Exception as e:
            api_logger.log_error(
                error=str(e),
                operation="analyze_biomarker",
                details={"biomarker": biomarker.get("normalized_name", "unknown")}
            )
            
            # Retorna biomarcador com status de erro
            return {
                "exam_id": exam_id,
                "name": biomarker.get("raw_name", ""),
                "normalized_name": biomarker.get("normalized_name", ""),
                "value": biomarker.get("value", 0),
                "unit": biomarker.get("unit", ""),
                "status": "error",
                "confidence_score": 0,
                "raw_text": biomarker.get("raw_text", ""),
                "interpretation": f"Erro na análise: {str(e)}",
                "severity": "unknown",
                "created_at": datetime.now().isoformat()
            }
    
    def _find_matching_reference(
        self, 
        biomarker: Dict[str, Any], 
        reference_ranges: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Encontra range de referência para um biomarcador.
        
        Args:
            biomarker: Dados do biomarcador
            reference_ranges: Lista de ranges de referência
            
        Returns:
            Range de referência encontrado ou None
        """
        try:
            normalized_name = biomarker["normalized_name"].lower()
            
            for ref_range in reference_ranges:
                if ref_range["normalized_name"].lower() == normalized_name:
                    # Verifica se a unidade é compatível
                    if self._units_are_compatible(biomarker["unit"], ref_range["unit"]):
                        return ref_range
            
            return None
            
        except Exception as e:
            api_logger.log_error(
                error=str(e),
                operation="find_matching_reference",
                details={"biomarker_name": biomarker.get("normalized_name", "unknown")}
            )
            return None
    
    def _units_are_compatible(self, unit1: str, unit2: str) -> bool:
        """
        Verifica se duas unidades são compatíveis.
        
        Args:
            unit1: Primeira unidade
            unit2: Segunda unidade
            
        Returns:
            True se compatíveis
        """
        # Normaliza unidades
        unit1_norm = unit1.lower().replace(" ", "")
        unit2_norm = unit2.lower().replace(" ", "")
        
        # Mapeamento de unidades equivalentes
        equivalent_units = {
            "g/dl": ["g/dl", "g/dl", "g/l", "g/l"],
            "mg/dl": ["mg/dl", "mg/dl", "mg/l", "mg/l"],
            "meq/l": ["meq/l", "meq/l", "mmol/l", "mmol/l"],
            "u/l": ["u/l", "u/l", "ui/l", "ui/l"],
            "cel/μl": ["cel/μl", "cel/ul", "cel/mm³", "cel/mm3"],
            "%": ["%", "percentual", "percent"]
        }
        
        # Verifica equivalência
        for base_unit, equivalents in equivalent_units.items():
            if unit1_norm in equivalents and unit2_norm in equivalents:
                return True
        
        # Verifica correspondência direta
        return unit1_norm == unit2_norm
    
    def _analyze_value(
        self, 
        value: float, 
        unit: str, 
        reference_range: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analisa valor do biomarcador contra range de referência.
        
        Args:
            value: Valor do biomarcador
            unit: Unidade do valor
            reference_range: Range de referência
            
        Returns:
            Análise com status e interpretação
        """
        try:
            if not reference_range:
                return {
                    "status": "unknown",
                    "interpretation": "Range de referência não encontrado",
                    "severity": "unknown"
                }
            
            min_ref = reference_range.get("min_value")
            max_ref = reference_range.get("max_value")
            
            if min_ref is None or max_ref is None:
                return {
                    "status": "unknown",
                    "interpretation": "Range de referência incompleto",
                    "severity": "unknown"
                }
            
            # Converte unidades se necessário
            converted_value = self._convert_unit(value, unit, reference_range["unit"])
            
            # Analisa o valor
            if converted_value < min_ref:
                status = "low"
                severity = self._calculate_severity(converted_value, min_ref, "low")
                interpretation = f"Valor abaixo do normal ({converted_value} {reference_range['unit']} < {min_ref} {reference_range['unit']})"
            elif converted_value > max_ref:
                status = "high"
                severity = self._calculate_severity(converted_value, max_ref, "high")
                interpretation = f"Valor acima do normal ({converted_value} {reference_range['unit']} > {max_ref} {reference_range['unit']})"
            else:
                status = "normal"
                severity = "normal"
                interpretation = f"Valor dentro do normal ({converted_value} {reference_range['unit']})"
            
            return {
                "status": status,
                "interpretation": interpretation,
                "severity": severity
            }
            
        except Exception as e:
            return {
                "status": "error",
                "interpretation": f"Erro na análise: {str(e)}",
                "severity": "unknown"
            }
    
    def _convert_unit(self, value: float, from_unit: str, to_unit: str) -> float:
        """
        Converte valor entre unidades compatíveis.
        
        Args:
            value: Valor a converter
            from_unit: Unidade de origem
            to_unit: Unidade de destino
            
        Returns:
            Valor convertido
        """
        # Por enquanto, retorna o valor original
        # Implementar conversões específicas conforme necessário
        return value
    
    def _calculate_severity(self, value: float, reference: float, direction: str) -> str:
        """
        Calcula severidade da alteração.
        
        Args:
            value: Valor atual
            reference: Valor de referência
            direction: Direção da alteração ('low' ou 'high')
            
        Returns:
            Nível de severidade
        """
        try:
            if direction == "low":
                deviation = (reference - value) / reference * 100
            else:  # high
                deviation = (value - reference) / reference * 100
            
            if deviation < 10:
                return "mild"
            elif deviation < 25:
                return "moderate"
            elif deviation < 50:
                return "severe"
            else:
                return "critical"
                
        except Exception:
            return "unknown"
    
    def _generate_summary(self, biomarkers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Gera resumo dos biomarcadores analisados.
        
        Args:
            biomarkers: Lista de biomarcadores analisados
            
        Returns:
            Resumo estruturado
        """
        try:
            total_count = len(biomarkers)
            normal_count = len([b for b in biomarkers if b["status"] == "normal"])
            abnormal_count = total_count - normal_count
            
            # Agrupa por severidade
            severity_counts = {}
            for biomarker in biomarkers:
                severity = biomarker.get("severity", "unknown")
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Identifica biomarcadores críticos
            critical_biomarkers = [
                b for b in biomarkers 
                if b.get("severity") == "critical"
            ]
            
            # Gera texto do resumo
            summary_text = self._generate_summary_text(
                total_count, normal_count, abnormal_count, 
                severity_counts, critical_biomarkers
            )
            
            return {
                "total_biomarkers": total_count,
                "normal_count": normal_count,
                "abnormal_count": abnormal_count,
                "severity_breakdown": severity_counts,
                "critical_count": len(critical_biomarkers),
                "summary_text": summary_text,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "error": f"Erro ao gerar resumo: {str(e)}",
                "generated_at": datetime.now().isoformat()
            }
    
    def _generate_summary_text(
        self, 
        total: int, 
        normal: int, 
        abnormal: int, 
        severity_counts: Dict[str, int],
        critical_biomarkers: List[Dict[str, Any]]
    ) -> str:
        """
        Gera texto descritivo do resumo.
        
        Args:
            total: Total de biomarcadores
            normal: Quantidade normal
            abnormal: Quantidade alterada
            severity_counts: Contagem por severidade
            critical_biomarkers: Biomarcadores críticos
            
        Returns:
            Texto do resumo
        """
        try:
            summary_parts = []
            
            # Resumo geral
            summary_parts.append(f"Análise de {total} biomarcadores:")
            summary_parts.append(f"- {normal} valores normais")
            summary_parts.append(f"- {abnormal} valores alterados")
            
            # Detalhes por severidade
            if severity_counts.get("mild", 0) > 0:
                summary_parts.append(f"- {severity_counts['mild']} alterações leves")
            
            if severity_counts.get("moderate", 0) > 0:
                summary_parts.append(f"- {severity_counts['moderate']} alterações moderadas")
            
            if severity_counts.get("severe", 0) > 0:
                summary_parts.append(f"- {severity_counts['severe']} alterações graves")
            
            if severity_counts.get("critical", 0) > 0:
                summary_parts.append(f"- {severity_counts['critical']} alterações críticas")
            
            # Biomarcadores críticos específicos
            if critical_biomarkers:
                summary_parts.append("\nBiomarcadores críticos:")
                for biomarker in critical_biomarkers[:3]:  # Limita a 3 para não ficar muito longo
                    summary_parts.append(
                        f"- {biomarker['normalized_name']}: {biomarker['value']} {biomarker['unit']} "
                        f"({biomarker['interpretation']})"
                    )
                
                if len(critical_biomarkers) > 3:
                    summary_parts.append(f"... e mais {len(critical_biomarkers) - 3} biomarcadores críticos")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            return f"Erro ao gerar resumo: {str(e)}"
    
    async def _save_biomarkers(self, exam_id: str, biomarkers: List[Dict[str, Any]]) -> bool:
        """
        Salva biomarcadores no banco de dados.
        
        Args:
            exam_id: ID do exame
            biomarkers: Lista de biomarcadores para salvar
            
        Returns:
            True se salvou com sucesso
        """
        try:
            for biomarker in biomarkers:
                # Remove campos que não são da tabela
                db_biomarker = {k: v for k, v in biomarker.items() 
                               if k in ["exam_id", "name", "normalized_name", "value", "unit", 
                                       "reference_range_id", "status", "confidence_score", "raw_text"]}
                
                supabase_client.get_table("biomarkers").insert(db_biomarker).execute()
            
            return True
            
        except Exception as e:
            api_logger.log_error(
                error=str(e),
                operation="save_biomarkers",
                details={"exam_id": exam_id, "count": len(biomarkers)}
            )
            return False


# Instância global do serviço
biomarker_service = BiomarkerService()
