"""
Script para popular tabelas com dados iniciais.
"""

from typing import List, Dict, Any
from ..core.supabase_client import supabase_client
from ..core.logging import api_logger


class DatabaseSeeder:
    """Classe para popular o banco com dados iniciais."""
    
    def __init__(self):
        self.supabase = supabase_client
    
    async def seed_reference_ranges(self) -> bool:
        """
        Popula a tabela reference_ranges com dados brasileiros.
        
        Returns:
            True se populou com sucesso
        """
        try:
            # Dados de ranges de referência brasileiros
            reference_ranges = [
                # Hemograma
                {
                    "biomarker_name": "Hemoglobina",
                    "normalized_name": "Hb",
                    "min_value": 12.0,
                    "max_value": 16.0,
                    "unit": "g/dL",
                    "gender": "F",
                    "age_min": 18,
                    "age_max": 65,
                    "source": "Sociedade Brasileira de Patologia Clínica"
                },
                {
                    "biomarker_name": "Hemoglobina",
                    "normalized_name": "Hb",
                    "min_value": 13.0,
                    "max_value": 17.0,
                    "unit": "g/dL",
                    "gender": "M",
                    "age_min": 18,
                    "age_max": 65,
                    "source": "Sociedade Brasileira de Patologia Clínica"
                },
                {
                    "biomarker_name": "Hematócrito",
                    "normalized_name": "Ht",
                    "min_value": 36.0,
                    "max_value": 46.0,
                    "unit": "%",
                    "gender": "F",
                    "age_min": 18,
                    "age_max": 65,
                    "source": "Sociedade Brasileira de Patologia Clínica"
                },
                {
                    "biomarker_name": "Hematócrito",
                    "normalized_name": "Ht",
                    "min_value": 41.0,
                    "max_value": 50.0,
                    "unit": "%",
                    "gender": "M",
                    "age_min": 18,
                    "age_max": 65,
                    "source": "Sociedade Brasileira de Patologia Clínica"
                },
                {
                    "biomarker_name": "Leucócitos",
                    "normalized_name": "WBC",
                    "min_value": 4000,
                    "max_value": 11000,
                    "unit": "cel/μL",
                    "gender": None,
                    "age_min": 18,
                    "age_max": 65,
                    "source": "Sociedade Brasileira de Patologia Clínica"
                },
                {
                    "biomarker_name": "Plaquetas",
                    "normalized_name": "Plt",
                    "min_value": 150000,
                    "max_value": 450000,
                    "unit": "cel/μL",
                    "gender": None,
                    "age_min": 18,
                    "age_max": 65,
                    "source": "Sociedade Brasileira de Patologia Clínica"
                },
                
                # Bioquímica
                {
                    "biomarker_name": "Glicose",
                    "normalized_name": "Glu",
                    "min_value": 70.0,
                    "max_value": 100.0,
                    "unit": "mg/dL",
                    "gender": None,
                    "age_min": 18,
                    "age_max": 65,
                    "source": "Sociedade Brasileira de Diabetes"
                },
                {
                    "biomarker_name": "Creatinina",
                    "normalized_name": "Cr",
                    "min_value": 0.6,
                    "max_value": 1.1,
                    "unit": "mg/dL",
                    "gender": "F",
                    "age_min": 18,
                    "age_max": 65,
                    "source": "Sociedade Brasileira de Nefrologia"
                },
                {
                    "biomarker_name": "Creatinina",
                    "normalized_name": "Cr",
                    "min_value": 0.7,
                    "max_value": 1.3,
                    "unit": "mg/dL",
                    "gender": "M",
                    "age_min": 18,
                    "age_max": 65,
                    "source": "Sociedade Brasileira de Nefrologia"
                },
                {
                    "biomarker_name": "Ureia",
                    "normalized_name": "Ureia",
                    "min_value": 10.0,
                    "max_value": 50.0,
                    "unit": "mg/dL",
                    "gender": None,
                    "age_min": 18,
                    "age_max": 65,
                    "source": "Sociedade Brasileira de Nefrologia"
                },
                {
                    "biomarker_name": "Colesterol Total",
                    "normalized_name": "CT",
                    "min_value": 0.0,
                    "max_value": 200.0,
                    "unit": "mg/dL",
                    "gender": None,
                    "age_min": 18,
                    "age_max": 65,
                    "source": "Sociedade Brasileira de Cardiologia"
                },
                {
                    "biomarker_name": "HDL",
                    "normalized_name": "HDL",
                    "min_value": 40.0,
                    "max_value": 60.0,
                    "unit": "mg/dL",
                    "gender": None,
                    "age_min": 18,
                    "age_max": 65,
                    "source": "Sociedade Brasileira de Cardiologia"
                },
                {
                    "biomarker_name": "LDL",
                    "normalized_name": "LDL",
                    "min_value": 0.0,
                    "max_value": 130.0,
                    "unit": "mg/dL",
                    "gender": None,
                    "age_min": 18,
                    "age_max": 65,
                    "source": "Sociedade Brasileira de Cardiologia"
                },
                {
                    "biomarker_name": "Triglicerídeos",
                    "normalized_name": "TG",
                    "min_value": 0.0,
                    "max_value": 150.0,
                    "unit": "mg/dL",
                    "gender": None,
                    "age_min": 18,
                    "age_max": 65,
                    "source": "Sociedade Brasileira de Cardiologia"
                },
                
                # Eletrólitos
                {
                    "biomarker_name": "Sódio",
                    "normalized_name": "Na",
                    "min_value": 135.0,
                    "max_value": 145.0,
                    "unit": "mEq/L",
                    "gender": None,
                    "age_min": 18,
                    "age_max": 65,
                    "source": "Sociedade Brasileira de Nefrologia"
                },
                {
                    "biomarker_name": "Potássio",
                    "normalized_name": "K",
                    "min_value": 3.5,
                    "max_value": 5.0,
                    "unit": "mEq/L",
                    "gender": None,
                    "age_min": 18,
                    "age_max": 65,
                    "source": "Sociedade Brasileira de Nefrologia"
                },
                {
                    "biomarker_name": "Cloro",
                    "normalized_name": "Cl",
                    "min_value": 96.0,
                    "max_value": 106.0,
                    "unit": "mEq/L",
                    "gender": None,
                    "age_min": 18,
                    "age_max": 65,
                    "source": "Sociedade Brasileira de Nefrologia"
                },
                
                # Função hepática
                {
                    "biomarker_name": "TGO",
                    "normalized_name": "TGO",
                    "min_value": 5.0,
                    "max_value": 40.0,
                    "unit": "U/L",
                    "gender": None,
                    "age_min": 18,
                    "age_max": 65,
                    "source": "Sociedade Brasileira de Hepatologia"
                },
                {
                    "biomarker_name": "TGP",
                    "normalized_name": "TGP",
                    "min_value": 7.0,
                    "max_value": 56.0,
                    "unit": "U/L",
                    "gender": None,
                    "age_min": 18,
                    "age_max": 65,
                    "source": "Sociedade Brasileira de Hepatologia"
                },
                {
                    "biomarker_name": "Fosfatase Alcalina",
                    "normalized_name": "FA",
                    "min_value": 44.0,
                    "max_value": 147.0,
                    "unit": "U/L",
                    "gender": None,
                    "age_min": 18,
                    "age_max": 65,
                    "source": "Sociedade Brasileira de Hepatologia"
                },
                {
                    "biomarker_name": "Bilirrubina Total",
                    "normalized_name": "BT",
                    "min_value": 0.3,
                    "max_value": 1.2,
                    "unit": "mg/dL",
                    "gender": None,
                    "age_min": 18,
                    "age_max": 65,
                    "source": "Sociedade Brasileira de Hepatologia"
                }
            ]
            
            # Insere cada range de referência
            for ref_range in reference_ranges:
                try:
                    result = self.supabase.get_table("reference_ranges").insert(ref_range).execute()
                    
                    if not result.data:
                        api_logger.log_error(
                            error="Falha ao inserir range de referência",
                            operation="seed_reference_ranges",
                            details={"biomarker": ref_range["normalized_name"]}
                        )
                        
                except Exception as e:
                    api_logger.log_error(
                        error=str(e),
                        operation="seed_reference_ranges",
                        details={"biomarker": ref_range["normalized_name"]}
                    )
            
            api_logger.log_operation(
                operation="seed_reference_ranges",
                details={"total_inserted": len(reference_ranges)}
            )
            
            return True
            
        except Exception as e:
            api_logger.log_error(
                error=str(e),
                operation="seed_reference_ranges"
            )
            return False
    
    async def seed_sample_patients(self) -> bool:
        """
        Popula a tabela patients com pacientes de exemplo.
        
        Returns:
            True se populou com sucesso
        """
        try:
            # Dados de pacientes de exemplo (dados fictícios para teste)
            sample_patients = [
                {
                    "full_name": "João Silva Santos",
                    "cpf": "12345678901",
                    "birth_date": "1985-03-15",
                    "gender": "M",
                    "phone": "(11) 99999-9999",
                    "address": "Rua das Flores, 123 - São Paulo/SP"
                },
                {
                    "full_name": "Maria Oliveira Costa",
                    "cpf": "98765432109",
                    "birth_date": "1990-07-22",
                    "gender": "F",
                    "phone": "(11) 88888-8888",
                    "address": "Av. Paulista, 456 - São Paulo/SP"
                },
                {
                    "full_name": "Carlos Ferreira Lima",
                    "cpf": "45678912345",
                    "birth_date": "1978-11-08",
                    "gender": "M",
                    "phone": "(11) 77777-7777",
                    "address": "Rua Augusta, 789 - São Paulo/SP"
                }
            ]
            
            # Insere cada paciente
            for patient in sample_patients:
                try:
                    result = self.supabase.get_table("patients").insert(patient).execute()
                    
                    if not result.data:
                        api_logger.log_error(
                            error="Falha ao inserir paciente",
                            operation="seed_sample_patients",
                            details={"name": patient["full_name"]}
                        )
                        
                except Exception as e:
                    api_logger.log_error(
                        error=str(e),
                        operation="seed_sample_patients",
                        details={"name": patient["full_name"]}
                    )
            
            api_logger.log_operation(
                operation="seed_sample_patients",
                details={"total_inserted": len(sample_patients)}
            )
            
            return True
            
        except Exception as e:
            api_logger.log_error(
                error=str(e),
                operation="seed_sample_patients"
            )
            return False
    
    async def seed_all(self) -> Dict[str, bool]:
        """
        Executa todos os seeds.
        
        Returns:
            Dict com status de cada seed
        """
        results = {}
        
        # Seed reference ranges
        results["reference_ranges"] = await self.seed_reference_ranges()
        
        # Seed sample patients
        results["sample_patients"] = await self.seed_sample_patients()
        
        # Log geral
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        api_logger.log_operation(
            operation="database_seeding",
            details={
                "total_seeds": total_count,
                "successful_seeds": success_count,
                "failed_seeds": total_count - success_count
            }
        )
        
        return results


# Instância global do seeder
database_seeder = DatabaseSeeder()


async def run_seeds():
    """Função para executar todos os seeds."""
    print("Iniciando população do banco de dados...")
    
    results = await database_seeder.seed_all()
    
    print("\nResultados dos seeds:")
    for seed_name, success in results.items():
        status = "✅ Sucesso" if success else "❌ Falha"
        print(f"- {seed_name}: {status}")
    
    success_count = sum(1 for success in results.values() if success)
    total_count = len(results)
    
    print(f"\nResumo: {success_count}/{total_count} seeds executados com sucesso")
    
    if success_count == total_count:
        print("🎉 Todos os seeds foram executados com sucesso!")
    else:
        print("⚠️  Alguns seeds falharam. Verifique os logs para mais detalhes.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_seeds())
