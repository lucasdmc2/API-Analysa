"""
Testes para o serviço de biomarcadores.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.services.biomarker_service import BiomarkerService


class TestBiomarkerService:
    """Testes para BiomarkerService."""
    
    @pytest.fixture
    def biomarker_service(self):
        """Instância do BiomarkerService."""
        return BiomarkerService()
    
    @pytest.fixture
    def mock_reference_ranges(self):
        """Ranges de referência mockados."""
        return [
            {
                "id": "ref-1",
                "biomarker_name": "Hemoglobina",
                "normalized_name": "Hb",
                "min_value": 12.0,
                "max_value": 16.0,
                "unit": "g/dL",
                "gender": "F",
                "age_min": 18,
                "age_max": 65,
                "is_active": True
            },
            {
                "id": "ref-2",
                "biomarker_name": "Glicose",
                "normalized_name": "Glu",
                "min_value": 70.0,
                "max_value": 100.0,
                "unit": "mg/dL",
                "gender": None,
                "age_min": 18,
                "age_max": 65,
                "is_active": True
            }
        ]
    
    @pytest.mark.asyncio
    async def test_process_exam_biomarkers_success(self, biomarker_service, mock_reference_ranges):
        """Testa processamento bem-sucedido de biomarcadores."""
        # Arrange
        exam_id = "test-exam-123"
        ocr_text = "Hemoglobina: 14.5 g/dL\nGlicose: 95 mg/dL"
        
        # Mock do parser
        with patch.object(biomarker_service.parser, 'parse_text') as mock_parse:
            mock_parse.return_value = {
                "success": True,
                "biomarkers": [
                    {
                        "type": "hemoglobina",
                        "normalized_name": "Hb",
                        "raw_name": "Hemoglobina",
                        "value": 14.5,
                        "unit": "g/dL",
                        "raw_text": "Hemoglobina: 14.5 g/dL",
                        "confidence": 90.0
                    },
                    {
                        "type": "glicose",
                        "normalized_name": "Glu",
                        "raw_name": "Glicose",
                        "value": 95.0,
                        "unit": "mg/dL",
                        "raw_text": "Glicose: 95 mg/dL",
                        "confidence": 85.0
                    }
                ],
                "total_found": 2,
                "parsing_confidence": 87.5
            }
        
        # Mock do banco de dados
        with patch.object(biomarker_service, '_get_reference_ranges') as mock_get_refs:
            mock_get_refs.return_value = mock_reference_ranges
        
        with patch.object(biomarker_service, '_save_biomarkers') as mock_save:
            mock_save.return_value = True
        
        # Act
        result = await biomarker_service.process_exam_biomarkers(exam_id, ocr_text)
        
        # Assert
        assert result["success"] is True
        assert result["total_found"] == 2
        assert len(result["biomarkers"]) == 2
        assert result["analysis_confidence"] == 87.5
        assert "summary" in result
    
    @pytest.mark.asyncio
    async def test_process_exam_biomarkers_parser_failure(self, biomarker_service):
        """Testa falha no parsing de biomarcadores."""
        # Arrange
        exam_id = "test-exam-123"
        ocr_text = "Texto sem biomarcadores"
        
        # Mock do parser falhando
        with patch.object(biomarker_service.parser, 'parse_text') as mock_parse:
            mock_parse.return_value = {
                "success": False,
                "error": "Falha no parsing"
            }
        
        # Act
        result = await biomarker_service.process_exam_biomarkers(exam_id, ocr_text)
        
        # Assert
        assert result["success"] is False
        assert "Falha no parsing" in result["error"]
    
    def test_find_matching_reference_success(self, biomarker_service, mock_reference_ranges):
        """Testa busca bem-sucedida de range de referência."""
        # Arrange
        biomarker = {
            "normalized_name": "Hb",
            "unit": "g/dL"
        }
        
        # Act
        result = biomarker_service._find_matching_reference(biomarker, mock_reference_ranges)
        
        # Assert
        assert result is not None
        assert result["normalized_name"] == "Hb"
        assert result["min_value"] == 12.0
        assert result["max_value"] == 16.0
    
    def test_find_matching_reference_not_found(self, biomarker_service, mock_reference_ranges):
        """Testa busca de range de referência não encontrado."""
        # Arrange
        biomarker = {
            "normalized_name": "Unknown",
            "unit": "mg/dL"
        }
        
        # Act
        result = biomarker_service._find_matching_reference(biomarker, mock_reference_ranges)
        
        # Assert
        assert result is None
    
    def test_units_are_compatible_same_unit(self, biomarker_service):
        """Testa compatibilidade de unidades iguais."""
        # Act & Assert
        assert biomarker_service._units_are_compatible("g/dL", "g/dL") is True
        assert biomarker_service._units_are_compatible("mg/dL", "mg/dL") is True
        assert biomarker_service._units_are_compatible("mEq/L", "mEq/L") is True
    
    def test_units_are_compatible_equivalent_units(self, biomarker_service):
        """Testa compatibilidade de unidades equivalentes."""
        # Act & Assert
        assert biomarker_service._units_are_compatible("g/dL", "g/L") is True
        assert biomarker_service._units_are_compatible("mg/dL", "mg/L") is True
        assert biomarker_service._units_are_compatible("mEq/L", "mmol/L") is True
        assert biomarker_service._units_are_compatible("U/L", "UI/L") is True
    
    def test_units_are_compatible_different_units(self, biomarker_service):
        """Testa incompatibilidade de unidades diferentes."""
        # Act & Assert
        assert biomarker_service._units_are_compatible("g/dL", "mg/dL") is False
        assert biomarker_service._units_are_compatible("mEq/L", "mg/dL") is False
    
    def test_analyze_value_normal(self, biomarker_service):
        """Testa análise de valor normal."""
        # Arrange
        value = 14.5
        unit = "g/dL"
        reference_range = {
            "min_value": 12.0,
            "max_value": 16.0,
            "unit": "g/dL"
        }
        
        # Act
        result = biomarker_service._analyze_value(value, unit, reference_range)
        
        # Assert
        assert result["status"] == "normal"
        assert result["severity"] == "normal"
        assert "dentro do normal" in result["interpretation"]
    
    def test_analyze_value_low(self, biomarker_service):
        """Testa análise de valor baixo."""
        # Arrange
        value = 10.0
        unit = "g/dL"
        reference_range = {
            "min_value": 12.0,
            "max_value": 16.0,
            "unit": "g/dL"
        }
        
        # Act
        result = biomarker_service._analyze_value(value, unit, reference_range)
        
        # Assert
        assert result["status"] == "low"
        assert result["severity"] == "moderate"
        assert "abaixo do normal" in result["interpretation"]
    
    def test_analyze_value_high(self, biomarker_service):
        """Testa análise de valor alto."""
        # Arrange
        value = 18.0
        unit = "g/dL"
        reference_range = {
            "min_value": 12.0,
            "max_value": 16.0,
            "unit": "g/dL"
        }
        
        # Act
        result = biomarker_service._analyze_value(value, unit, reference_range)
        
        # Assert
        assert result["status"] == "high"
        assert result["severity"] == "mild"
        assert "acima do normal" in result["interpretation"]
    
    def test_analyze_value_no_reference(self, biomarker_service):
        """Testa análise sem range de referência."""
        # Arrange
        value = 14.5
        unit = "g/dL"
        reference_range = None
        
        # Act
        result = biomarker_service._analyze_value(value, unit, reference_range)
        
        # Assert
        assert result["status"] == "unknown"
        assert result["severity"] == "unknown"
        assert "não encontrado" in result["interpretation"]
    
    def test_calculate_severity_mild(self, biomarker_service):
        """Testa cálculo de severidade leve."""
        # Act
        result = biomarker_service._calculate_severity(95.0, 100.0, "low")
        
        # Assert
        assert result == "mild"
    
    def test_calculate_severity_moderate(self, biomarker_service):
        """Testa cálculo de severidade moderada."""
        # Act
        result = biomarker_service._calculate_severity(75.0, 100.0, "low")
        
        # Assert
        assert result == "moderate"
    
    def test_calculate_severity_severe(self, biomarker_service):
        """Testa cálculo de severidade grave."""
        # Act
        result = biomarker_service._calculate_severity(50.0, 100.0, "low")
        
        # Assert
        assert result == "severe"
    
    def test_calculate_severity_critical(self, biomarker_service):
        """Testa cálculo de severidade crítica."""
        # Act
        result = biomarker_service._calculate_severity(25.0, 100.0, "low")
        
        # Assert
        assert result == "critical"
    
    def test_generate_summary_success(self, biomarker_service):
        """Testa geração de resumo bem-sucedida."""
        # Arrange
        biomarkers = [
            {"status": "normal", "severity": "normal"},
            {"status": "high", "severity": "mild"},
            {"status": "low", "severity": "moderate"},
            {"status": "high", "severity": "critical"}
        ]
        
        # Act
        result = biomarker_service._generate_summary(biomarkers)
        
        # Assert
        assert result["total_biomarkers"] == 4
        assert result["normal_count"] == 1
        assert result["abnormal_count"] == 3
        assert result["critical_count"] == 1
        assert "summary_text" in result
    
    def test_generate_summary_empty(self, biomarker_service):
        """Testa geração de resumo com lista vazia."""
        # Act
        result = biomarker_service._generate_summary([])
        
        # Assert
        assert result["total_biomarkers"] == 0
        assert result["normal_count"] == 0
        assert result["abnormal_count"] == 0
        assert result["critical_count"] == 0
    
    def test_generate_summary_text_normal_only(self, biomarker_service):
        """Testa geração de texto de resumo apenas com valores normais."""
        # Arrange
        total = 3
        normal = 3
        abnormal = 0
        severity_counts = {"normal": 3}
        critical_biomarkers = []
        
        # Act
        result = biomarker_service._generate_summary_text(
            total, normal, abnormal, severity_counts, critical_biomarkers
        )
        
        # Assert
        assert "3 valores normais" in result
        assert "0 valores alterados" in result
        assert "Biomarcadores críticos:" not in result
    
    def test_generate_summary_text_with_critical(self, biomarker_service):
        """Testa geração de texto de resumo com biomarcadores críticos."""
        # Arrange
        total = 3
        normal = 1
        abnormal = 2
        severity_counts = {"normal": 1, "critical": 2}
        critical_biomarkers = [
            {"normalized_name": "Hb", "value": 8.0, "unit": "g/dL", "interpretation": "Muito baixo"},
            {"normalized_name": "Glu", "value": 300.0, "unit": "mg/dL", "interpretation": "Muito alto"}
        ]
        
        # Act
        result = biomarker_service._generate_summary_text(
            total, normal, abnormal, severity_counts, critical_biomarkers
        )
        
        # Assert
        assert "1 valores normais" in result
        assert "2 valores alterados" in result
        assert "Biomarcadores críticos:" in result
        assert "Hb: 8.0 g/dL" in result
        assert "Glu: 300.0 mg/dL" in result


class TestBiomarkerServiceIntegration:
    """Testes de integração para BiomarkerService."""
    
    @pytest.fixture
    def biomarker_service(self):
        """Instância do BiomarkerService para testes de integração."""
        return BiomarkerService()
    
    @pytest.mark.asyncio
    async def test_full_biomarker_analysis_workflow(self, biomarker_service):
        """Testa workflow completo de análise de biomarcadores."""
        # Arrange
        exam_id = "test-exam-456"
        ocr_text = """
        Hemograma:
        Hemoglobina: 14.5 g/dL
        Hematócrito: 42%
        Leucócitos: 7500 cel/μL
        
        Bioquímica:
        Glicose: 95 mg/dL
        Creatinina: 1.2 mg/dL
        """
        
        # Mock do parser
        with patch.object(biomarker_service.parser, 'parse_text') as mock_parse:
            mock_parse.return_value = {
                "success": True,
                "biomarkers": [
                    {
                        "type": "hemoglobina",
                        "normalized_name": "Hb",
                        "raw_name": "Hemoglobina",
                        "value": 14.5,
                        "unit": "g/dL",
                        "raw_text": "Hemoglobina: 14.5 g/dL",
                        "confidence": 90.0
                    },
                    {
                        "type": "glicose",
                        "normalized_name": "Glu",
                        "raw_name": "Glicose",
                        "value": 95.0,
                        "unit": "mg/dL",
                        "raw_text": "Glicose: 95 mg/dL",
                        "confidence": 85.0
                    }
                ],
                "total_found": 2,
                "parsing_confidence": 87.5
            }
        
        # Mock do banco de dados
        with patch.object(biomarker_service, '_get_reference_ranges') as mock_get_refs:
            mock_get_refs.return_value = [
                {
                    "id": "ref-1",
                    "normalized_name": "Hb",
                    "min_value": 12.0,
                    "max_value": 16.0,
                    "unit": "g/dL"
                },
                {
                    "id": "ref-2",
                    "normalized_name": "Glu",
                    "min_value": 70.0,
                    "max_value": 100.0,
                    "unit": "mg/dL"
                }
            ]
        
        with patch.object(biomarker_service, '_save_biomarkers') as mock_save:
            mock_save.return_value = True
        
        # Act
        result = await biomarker_service.process_exam_biomarkers(exam_id, ocr_text)
        
        # Assert
        assert result["success"] is True
        assert result["total_found"] == 2
        assert len(result["biomarkers"]) == 2
        
        # Verifica análise dos biomarcadores
        hb_biomarker = next(b for b in result["biomarkers"] if b["normalized_name"] == "Hb")
        glu_biomarker = next(b for b in result["biomarkers"] if b["normalized_name"] == "Glu")
        
        assert hb_biomarker["status"] == "normal"
        assert glu_biomarker["status"] == "normal"
        assert hb_biomarker["min_reference"] == 12.0
        assert hb_biomarker["max_reference"] == 16.0
        
        # Verifica resumo
        assert "summary" in result
        assert result["summary"]["total_biomarkers"] == 2
        assert result["summary"]["normal_count"] == 2
        assert result["summary"]["abnormal_count"] == 0
