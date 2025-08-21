"""
Testes para o serviço de parser de biomarcadores.
"""

import pytest
from unittest.mock import Mock, patch
from src.services.parser_service import BiomarkerParser


class TestBiomarkerParser:
    """Testes para BiomarkerParser."""
    
    @pytest.fixture
    def parser(self):
        """Instância do BiomarkerParser."""
        return BiomarkerParser()
    
    @pytest.mark.asyncio
    async def test_parse_text_hemoglobina(self, parser):
        """Testa parsing de hemoglobina."""
        # Arrange
        text = "Hemoglobina: 14.5 g/dL"
        
        # Act
        result = await parser.parse_text(text)
        
        # Assert
        assert result["success"] is True
        assert result["total_found"] == 1
        assert len(result["biomarkers"]) == 1
        
        biomarker = result["biomarkers"][0]
        assert biomarker["type"] == "hemoglobina"
        assert biomarker["normalized_name"] == "Hb"
        assert biomarker["value"] == 14.5
        assert biomarker["unit"] == "g/dL"
    
    @pytest.mark.asyncio
    async def test_parse_text_multiple_biomarkers(self, parser):
        """Testa parsing de múltiplos biomarcadores."""
        # Arrange
        text = """
        Hemoglobina: 14.5 g/dL
        Glicose: 95 mg/dL
        Creatinina: 1.2 mg/dL
        """
        
        # Act
        result = await parser.parse_text(text)
        
        # Assert
        assert result["success"] is True
        assert result["total_found"] == 3
        
        # Verifica se todos os tipos foram encontrados
        types_found = [b["type"] for b in result["biomarkers"]]
        assert "hemoglobina" in types_found
        assert "glicose" in types_found
        assert "creatinina" in types_found
    
    @pytest.mark.asyncio
    async def test_parse_text_with_abbreviations(self, parser):
        """Testa parsing com abreviações."""
        # Arrange
        text = "Hb: 14.5 g/dL, Glu: 95 mg/dL"
        
        # Act
        result = await parser.parse_text(text)
        
        # Assert
        assert result["success"] is True
        assert result["total_found"] == 2
        
        # Verifica se as abreviações foram reconhecidas
        types_found = [b["type"] for b in result["biomarkers"]]
        assert "hemoglobina" in types_found
        assert "glicose" in types_found
    
    @pytest.mark.asyncio
    async def test_parse_text_no_biomarkers(self, parser):
        """Testa parsing de texto sem biomarcadores."""
        # Arrange
        text = "Este é um texto sem biomarcadores médicos."
        
        # Act
        result = await parser.parse_text(text)
        
        # Assert
        assert result["success"] is True
        assert result["total_found"] == 0
        assert len(result["biomarkers"]) == 0
    
    @pytest.mark.asyncio
    async def test_parse_text_with_different_formats(self, parser):
        """Testa parsing com diferentes formatos."""
        # Arrange
        text = """
        Hemoglobina = 14.5 g/dL
        Glicose: 95 mg/dL
        Creatinina 1.2 mg/dL
        """
        
        # Act
        result = await parser.parse_text(text)
        
        # Assert
        assert result["success"] is True
        assert result["total_found"] == 3
    
    def test_normalize_value_with_comma(self, parser):
        """Testa normalização de valor com vírgula."""
        # Arrange
        value_str = "14,5"
        
        # Act
        result = parser._normalize_value(value_str)
        
        # Assert
        assert result == 14.5
    
    def test_normalize_value_with_dot(self, parser):
        """Testa normalização de valor com ponto."""
        # Arrange
        value_str = "14.5"
        
        # Act
        result = parser._normalize_value(value_str)
        
        # Assert
        assert result == 14.5
    
    def test_normalize_value_with_extra_chars(self, parser):
        """Testa normalização de valor com caracteres extras."""
        # Arrange
        value_str = "14,5 mg/dL"
        
        # Act
        result = parser._normalize_value(value_str)
        
        # Assert
        assert result == 14.5
    
    def test_normalize_value_invalid(self, parser):
        """Testa normalização de valor inválido."""
        # Arrange
        value_str = "invalid"
        
        # Act
        result = parser._normalize_value(value_str)
        
        # Assert
        assert result == 0.0
    
    def test_infer_unit_hemoglobina(self, parser):
        """Testa inferência de unidade para hemoglobina."""
        # Act
        unit = parser._infer_unit("hemoglobina")
        
        # Assert
        assert unit == "g/dL"
    
    def test_infer_unit_hematocrito(self, parser):
        """Testa inferência de unidade para hematócrito."""
        # Act
        unit = parser._infer_unit("hematocrito")
        
        # Assert
        assert unit == "%"
    
    def test_infer_unit_unknown(self, parser):
        """Testa inferência de unidade para tipo desconhecido."""
        # Act
        unit = parser._infer_unit("unknown_type")
        
        # Assert
        assert unit == ""
    
    def test_calculate_parsing_confidence_high(self, parser):
        """Testa cálculo de confiança alta."""
        # Arrange
        raw_name = "Hemoglobina"
        value = 14.5
        
        # Act
        confidence = parser._calculate_parsing_confidence(raw_name, value)
        
        # Assert
        assert confidence == 100.0  # Máxima confiança
    
    def test_calculate_parsing_confidence_low(self, parser):
        """Testa cálculo de confiança baixa."""
        # Arrange
        raw_name = ""
        value = 0.0
        
        # Act
        confidence = parser._calculate_parsing_confidence(raw_name, value)
        
        # Assert
        assert confidence == 0.0  # Mínima confiança
    
    def test_calculate_overall_confidence(self, parser):
        """Testa cálculo de confiança geral."""
        # Arrange
        biomarkers = [
            {"confidence": 80.0},
            {"confidence": 90.0},
            {"confidence": 70.0}
        ]
        
        # Act
        overall_confidence = parser._calculate_overall_confidence(biomarkers)
        
        # Assert
        assert overall_confidence == 80.0  # Média: (80+90+70)/3
    
    def test_calculate_overall_confidence_empty(self, parser):
        """Testa cálculo de confiança geral com lista vazia."""
        # Act
        overall_confidence = parser._calculate_overall_confidence([])
        
        # Assert
        assert overall_confidence == 0.0
    
    def test_get_supported_biomarkers(self, parser):
        """Testa obtenção de biomarcadores suportados."""
        # Act
        supported = parser.get_supported_biomarkers()
        
        # Assert
        assert "hemoglobina" in supported
        assert "glicose" in supported
        assert "creatinina" in supported
        assert len(supported) > 10  # Deve ter vários tipos
    
    def test_get_normalized_names(self, parser):
        """Testa obtenção de nomes normalizados."""
        # Act
        normalized = parser.get_normalized_names()
        
        # Assert
        assert normalized["hemoglobina"] == "Hb"
        assert normalized["glicose"] == "Glu"
        assert normalized["creatinina"] == "Cr"
    
    @pytest.mark.asyncio
    async def test_parse_text_with_edge_cases(self, parser):
        """Testa parsing com casos extremos."""
        # Arrange
        text = """
        Hb: 14,5 g/dL
        Glu: 95.0 mg/dL
        Cr: 1,2 mg/dL
        Na: 140 mEq/L
        K: 4,0 mEq/L
        """
        
        # Act
        result = await parser.parse_text(text)
        
        # Assert
        assert result["success"] is True
        assert result["total_found"] == 5
        
        # Verifica valores normalizados
        for biomarker in result["biomarkers"]:
            assert isinstance(biomarker["value"], float)
            assert biomarker["value"] > 0
            assert biomarker["confidence"] > 0
    
    @pytest.mark.asyncio
    async def test_parse_text_with_mixed_units(self, parser):
        """Testa parsing com unidades mistas."""
        # Arrange
        text = """
        Hemoglobina: 14.5 g/dL
        Leucócitos: 7500 cel/μL
        Plaquetas: 250000 cel/mm³
        """
        
        # Act
        result = await parser.parse_text(text)
        
        # Assert
        assert result["success"] is True
        assert result["total_found"] == 3
        
        # Verifica unidades específicas
        units_found = [b["unit"] for b in result["biomarkers"]]
        assert "g/dL" in units_found
        assert "cel/μL" in units_found
        assert "cel/mm³" in units_found


class TestBiomarkerParserPatterns:
    """Testes específicos para padrões regex."""
    
    @pytest.fixture
    def parser(self):
        """Instância do BiomarkerParser."""
        return BiomarkerParser()
    
    @pytest.mark.asyncio
    async def test_hemograma_patterns(self, parser):
        """Testa padrões de hemograma."""
        # Arrange
        text = """
        Hemoglobina: 14.5 g/dL
        Hematócrito: 42%
        Leucócitos: 7500 cel/μL
        Plaquetas: 250000 cel/mm³
        """
        
        # Act
        result = await parser.parse_text(text)
        
        # Assert
        assert result["success"] is True
        assert result["total_found"] == 4
        
        types_found = [b["type"] for b in result["biomarkers"]]
        assert "hemoglobina" in types_found
        assert "hematocrito" in types_found
        assert "leucocitos" in types_found
        assert "plaquetas" in types_found
    
    @pytest.mark.asyncio
    async def test_bioquimica_patterns(self, parser):
        """Testa padrões de bioquímica."""
        # Arrange
        text = """
        Glicose: 95 mg/dL
        Creatinina: 1.2 mg/dL
        Ureia: 25 mg/dL
        Colesterol Total: 180 mg/dL
        HDL: 45 mg/dL
        LDL: 110 mg/dL
        Triglicerídeos: 150 mg/dL
        """
        
        # Act
        result = await parser.parse_text(text)
        
        # Assert
        assert result["success"] is True
        assert result["total_found"] == 7
        
        types_found = [b["type"] for b in result["biomarkers"]]
        assert "glicose" in types_found
        assert "creatinina" in types_found
        assert "ureia" in types_found
        assert "colesterol_total" in types_found
        assert "hdl" in types_found
        assert "ldl" in types_found
        assert "triglicerides" in types_found
    
    @pytest.mark.asyncio
    async def test_eletrolitos_patterns(self, parser):
        """Testa padrões de eletrólitos."""
        # Arrange
        text = """
        Sódio: 140 mEq/L
        Potássio: 4.0 mEq/L
        Cloro: 102 mEq/L
        """
        
        # Act
        result = await parser.parse_text(text)
        
        # Assert
        assert result["success"] is True
        assert result["total_found"] == 3
        
        types_found = [b["type"] for b in result["biomarkers"]]
        assert "sodio" in types_found
        assert "potassio" in types_found
        assert "cloro" in types_found
    
    @pytest.mark.asyncio
    async def test_funcao_hepatica_patterns(self, parser):
        """Testa padrões de função hepática."""
        # Arrange
        text = """
        TGO: 25 U/L
        TGP: 30 U/L
        Fosfatase Alcalina: 70 U/L
        Bilirrubina Total: 0.8 mg/dL
        """
        
        # Act
        result = await parser.parse_text(text)
        
        # Assert
        assert result["success"] is True
        assert result["total_found"] == 4
        
        types_found = [b["type"] for b in result["biomarkers"]]
        assert "tgo" in types_found
        assert "tgp" in types_found
        assert "fosfatase_alcalina" in types_found
        assert "bilirrubina_total" in types_found
