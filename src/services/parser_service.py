"""
Serviço de parser para extração de biomarcadores de exames médicos.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from src.core.logging import api_logger


class BiomarkerParser:
    """Parser para extrair biomarcadores de texto de exames."""
    
    def __init__(self):
        # Padrões regex para biomarcadores comuns
        self.biomarker_patterns = {
            # Hemograma
            'hemoglobina': [
                r'(?i)(hemoglobina|hb)\s*[:=]?\s*(\d+[.,]?\d*)\s*(g/dl|g/dL|g/l|g/L)',
                r'(?i)(hb)\s*[:=]?\s*(\d+[.,]?\d*)\s*(g/dl|g/dL|g/l|g/L)'
            ],
            'hematocrito': [
                r'(?i)(hematócrito|hematocrito|ht|hct)\s*[:=]?\s*(\d+[.,]?\d*)\s*(%|percentual)',
                r'(?i)(ht|hct)\s*[:=]?\s*(\d+[.,]?\d*)\s*(%|percentual)'
            ],
            'leucocitos': [
                r'(?i)(leucócitos|leucocitos|wbc|gb)\s*[:=]?\s*(\d+[.,]?\d*)\s*(cel/μl|cel/ul|cel/mm³|cel/mm3)',
                r'(?i)(wbc|gb)\s*[:=]?\s*(\d+[.,]?\d*)\s*(cel/μl|cel/ul|cel/mm³|cel/mm3)'
            ],
            'plaquetas': [
                r'(?i)(plaquetas|plt|plq)\s*[:=]?\s*(\d+[.,]?\d*)\s*(cel/μl|cel/ul|cel/mm³|cel/mm3)',
                r'(?i)(plt|plq)\s*[:=]?\s*(\d+[.,]?\d*)\s*(cel/μl|cel/ul|cel/mm³|cel/mm3)'
            ],
            
            # Bioquímica
            'glicose': [
                r'(?i)(glicose|glucose|glu)\s*[:=]?\s*(\d+[.,]?\d*)\s*(mg/dl|mg/dL|mg/l|mg/L|mmol/l|mmol/L)',
                r'(?i)(glu)\s*[:=]?\s*(\d+[.,]?\d*)\s*(mg/dl|mg/dL|mg/l|mg/L|mmol/l|mmol/L)'
            ],
            'creatinina': [
                r'(?i)(creatinina|cr)\s*[:=]?\s*(\d+[.,]?\d*)\s*(mg/dl|mg/dL|mg/l|mg/L|μmol/l|umol/l)',
                r'(?i)(cr)\s*[:=]?\s*(\d+[.,]?\d*)\s*(mg/dl|mg/dL|mg/l|mg/L|μmol/l|umol/l)'
            ],
            'ureia': [
                r'(?i)(ureia|bun)\s*[:=]?\s*(\d+[.,]?\d*)\s*(mg/dl|mg/dL|mg/l|mg/L|mmol/l|mmol/L)',
                r'(?i)(bun)\s*[:=]?\s*(\d+[.,]?\d*)\s*(mg/dl|mg/dL|mg/l|mg/L|mmol/l|mmol/L)'
            ],
            'colesterol_total': [
                r'(?i)(colesterol total|colesterol|ct|tc)\s*[:=]?\s*(\d+[.,]?\d*)\s*(mg/dl|mg/dL|mg/l|mg/L|mmol/l|mmol/L)',
                r'(?i)(ct|tc)\s*[:=]?\s*(\d+[.,]?\d*)\s*(mg/dl|mg/dL|mg/l|mg/L|mmol/l|mmol/L)'
            ],
            'hdl': [
                r'(?i)(hdl|colesterol hdl)\s*[:=]?\s*(\d+[.,]?\d*)\s*(mg/dl|mg/dL|mg/l|mg/L|mmol/l|mmol/L)',
                r'(?i)(hdl)\s*[:=]?\s*(\d+[.,]?\d*)\s*(mg/dl|mg/dL|mg/l|mg/L|mmol/l|mmol/L)'
            ],
            'ldl': [
                r'(?i)(ldl|colesterol ldl)\s*[:=]?\s*(\d+[.,]?\d*)\s*(mg/dl|mg/dL|mg/l|mg/L|mmol/l|mmol/L)',
                r'(?i)(ldl)\s*[:=]?\s*(\d+[.,]?\d*)\s*(mg/dl|mg/dL|mg/l|mg/L|mmol/l|mmol/L)'
            ],
            'triglicerides': [
                r'(?i)(triglicerídeos|triglicerides|tg)\s*[:=]?\s*(\d+[.,]?\d*)\s*(mg/dl|mg/dL|mg/l|mg/L|mmol/l|mmol/L)',
                r'(?i)(tg)\s*[:=]?\s*(\d+[.,]?\d*)\s*(mg/dl|mg/dL|mg/l|mg/L|mmol/l|mmol/L)'
            ],
            
            # Eletrólitos
            'sodio': [
                r'(?i)(sódio|sodio|na)\s*[:=]?\s*(\d+[.,]?\d*)\s*(mEq/l|meq/l|mmol/l|mmol/L)',
                r'(?i)(na)\s*[:=]?\s*(\d+[.,]?\d*)\s*(mEq/l|meq/l|mmol/l|mmol/L)'
            ],
            'potassio': [
                r'(?i)(potássio|potassio|k)\s*[:=]?\s*(\d+[.,]?\d*)\s*(mEq/l|meq/l|mmol/l|mmol/L)',
                r'(?i)(k)\s*[:=]?\s*(\d+[.,]?\d*)\s*(mEq/l|meq/l|mmol/l|mmol/L)'
            ],
            'cloro': [
                r'(?i)(cloro|cl)\s*[:=]?\s*(\d+[.,]?\d*)\s*(mEq/l|meq/l|mmol/l|mmol/L)',
                r'(?i)(cl)\s*[:=]?\s*(\d+[.,]?\d*)\s*(mEq/l|meq/l|mmol/l|mmol/L)'
            ],
            
            # Função hepática
            'tgo': [
                r'(?i)(tgo|ast|asat)\s*[:=]?\s*(\d+[.,]?\d*)\s*(U/l|u/l|UI/l|ui/l)',
                r'(?i)(ast|asat)\s*[:=]?\s*(\d+[.,]?\d*)\s*(U/l|u/l|UI/l|ui/l)'
            ],
            'tgp': [
                r'(?i)(tgp|alt|alat)\s*[:=]?\s*(\d+[.,]?\d*)\s*(U/l|u/l|UI/l|ui/l)',
                r'(?i)(alt|alat)\s*[:=]?\s*(\d+[.,]?\d*)\s*(U/l|u/l|UI/l|ui/l)'
            ],
            'fosfatase_alcalina': [
                r'(?i)(fosfatase alcalina|fa|alp)\s*[:=]?\s*(\d+[.,]?\d*)\s*(U/l|u/l|UI/l|ui/l)',
                r'(?i)(fa|alp)\s*[:=]?\s*(\d+[.,]?\d*)\s*(U/l|u/l|UI/l|ui/l)'
            ],
            'bilirrubina_total': [
                r'(?i)(bilirrubina total|bilirrubina|bt)\s*[:=]?\s*(\d+[.,]?\d*)\s*(mg/dl|mg/dL|mg/l|mg/L|μmol/l|umol/l)',
                r'(?i)(bt)\s*[:=]?\s*(\d+[.,]?\d*)\s*(mg/dl|mg/dL|mg/l|mg/L|μmol/l|umol/l)'
            ]
        }
        
        # Mapeamento de nomes normalizados
        self.normalized_names = {
            'hemoglobina': 'Hb',
            'hematocrito': 'Ht',
            'leucocitos': 'WBC',
            'plaquetas': 'Plt',
            'glicose': 'Glu',
            'creatinina': 'Cr',
            'ureia': 'Ureia',
            'colesterol_total': 'CT',
            'hdl': 'HDL',
            'ldl': 'LDL',
            'triglicerides': 'TG',
            'sodio': 'Na',
            'potassio': 'K',
            'cloro': 'Cl',
            'tgo': 'TGO',
            'tgp': 'TGP',
            'fosfatase_alcalina': 'FA',
            'bilirrubina_total': 'BT'
        }
    
    async def parse_text(self, text: str) -> Dict[str, Any]:
        """
        Extrai biomarcadores do texto do exame.
        
        Args:
            text: Texto extraído via OCR
            
        Returns:
            Dict com biomarcadores encontrados
        """
        try:
            biomarkers = []
            total_found = 0
            
            # Processa cada tipo de biomarcador
            for biomarker_type, patterns in self.biomarker_patterns.items():
                found_this_type = False
                
                for pattern in patterns:
                    if found_this_type:
                        break  # Já encontrou este tipo, pula para o próximo
                        
                    matches = re.findall(pattern, text)
                    
                    for match in matches:
                        if len(match) >= 2:
                            # match[0] é o nome encontrado, match[1] é o valor
                            value = self._normalize_value(match[1])
                            unit = match[2] if len(match) > 2 else self._infer_unit(biomarker_type)
                            
                            biomarker = {
                                "type": biomarker_type,
                                "normalized_name": self.normalized_names.get(biomarker_type, biomarker_type.upper()),
                                "raw_name": match[0].strip(),
                                "value": value,
                                "unit": unit,
                                "raw_text": match[0].strip(),
                                "confidence": self._calculate_parsing_confidence(match[0], value)
                            }
                            
                            biomarkers.append(biomarker)
                            total_found += 1
                            found_this_type = True
                            break  # Evita duplicatas do mesmo tipo
            
            # Log da operação
            api_logger.log_operation(
                operation="biomarker_parsing",
                details={
                    "total_found": total_found,
                    "biomarker_types": list(set([b["type"] for b in biomarkers]))
                }
            )
            
            return {
                "success": True,
                "biomarkers": biomarkers,
                "total_found": total_found,
                "parsing_confidence": self._calculate_overall_confidence(biomarkers)
            }
            
        except Exception as e:
            api_logger.log_error(
                error=str(e),
                operation="biomarker_parsing"
            )
            return {"success": False, "error": str(e)}
    
    def _normalize_value(self, value_str: str) -> float:
        """
        Normaliza valor numérico.
        
        Args:
            value_str: String com o valor
            
        Returns:
            Valor numérico normalizado
        """
        try:
            # Remove caracteres não numéricos exceto ponto e vírgula
            clean_value = re.sub(r'[^\d.,]', '', value_str)
            
            # Substitui vírgula por ponto
            clean_value = clean_value.replace(',', '.')
            
            return float(clean_value)
        except (ValueError, TypeError):
            return 0.0
    
    def _infer_unit(self, biomarker_type: str) -> str:
        """
        Infere unidade baseada no tipo de biomarcador.
        
        Args:
            biomarker_type: Tipo do biomarcador
            
        Returns:
            Unidade inferida
        """
        unit_map = {
            'hemoglobina': 'g/dL',
            'hematocrito': '%',
            'leucocitos': 'cel/μL',
            'plaquetas': 'cel/μL',
            'glicose': 'mg/dL',
            'creatinina': 'mg/dL',
            'ureia': 'mg/dL',
            'colesterol_total': 'mg/dL',
            'hdl': 'mg/dL',
            'ldl': 'mg/dL',
            'triglicerides': 'mg/dL',
            'sodio': 'mEq/L',
            'potassio': 'mEq/L',
            'cloro': 'mEq/L',
            'tgo': 'U/L',
            'tgp': 'U/L',
            'fosfatase_alcalina': 'U/L',
            'bilirrubina_total': 'mg/dL'
        }
        
        return unit_map.get(biomarker_type, '')
    
    def _calculate_parsing_confidence(self, raw_name: str, value: float) -> float:
        """
        Calcula confiança do parsing de um biomarcador.
        
        Args:
            raw_name: Nome encontrado no texto
            value: Valor extraído
            
        Returns:
            Score de confiança (0-100)
        """
        confidence = 0.0
        
        # Confiança baseada no nome
        if len(raw_name.strip()) > 0:
            confidence += 30
        
        # Confiança baseada no valor
        if value > 0:
            confidence += 40
        
        # Confiança baseada na qualidade do nome
        if any(keyword in raw_name.lower() for keyword in ['hemoglobina', 'glicose', 'creatinina']):
            confidence += 30
        
        return min(confidence, 100.0)
    
    def _calculate_overall_confidence(self, biomarkers: List[Dict[str, Any]]) -> float:
        """
        Calcula confiança geral do parsing.
        
        Args:
            biomarkers: Lista de biomarcadores encontrados
            
        Returns:
            Confiança média
        """
        if not biomarkers:
            return 0.0
        
        total_confidence = sum(b.get('confidence', 0) for b in biomarkers)
        return total_confidence / len(biomarkers)
    
    def get_supported_biomarkers(self) -> List[str]:
        """
        Retorna lista de biomarcadores suportados.
        
        Returns:
            Lista de tipos de biomarcadores
        """
        return list(self.biomarker_patterns.keys())
    
    def get_normalized_names(self) -> Dict[str, str]:
        """
        Retorna mapeamento de nomes normalizados.
        
        Returns:
            Dict com mapeamento nome -> nome normalizado
        """
        return self.normalized_names.copy()


# Instância global do parser
biomarker_parser = BiomarkerParser()
