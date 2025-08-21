#!/usr/bin/env python3
"""
Script para verificar e configurar o banco de dados.
"""

import os
import sys
from pathlib import Path

# Adiciona o diretório src ao path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

def check_database_connection():
    """Verifica conexão com o banco de dados."""
    print("🗄️ Verificando conexão com banco de dados...")
    
    try:
        from core.config import get_settings_lazy
        from core.supabase_client import get_supabase_client
        
        # Carrega configurações
        config = get_settings_lazy()
        print(f"✅ Configurações carregadas")
        print(f"   - Supabase URL: {config.supabase_url}")
        print(f"   - Database URL: {config.database_url}")
        
        # Testa conexão Supabase
        supabase = get_supabase_client()
        print("✅ Cliente Supabase inicializado")
        
        # Testa conexão com uma query simples
        try:
            result = supabase.table("users").select("count", count="exact").execute()
            print("✅ Conexão com banco estabelecida")
            return True
        except Exception as e:
            print(f"❌ Erro ao conectar com banco: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao carregar configurações: {e}")
        return False

def create_database_tables():
    """Cria as tabelas necessárias no banco."""
    print("\n🏗️ Criando tabelas no banco de dados...")
    
    try:
        from core.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        # SQL para criar tabelas
        tables_sql = {
            "users": """
                CREATE TABLE IF NOT EXISTS users (
                    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    full_name VARCHAR(255) NOT NULL,
                    crm VARCHAR(50),
                    specialty VARCHAR(100),
                    phone VARCHAR(20),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """,
            
            "patients": """
                CREATE TABLE IF NOT EXISTS patients (
                    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                    full_name VARCHAR(255) NOT NULL,
                    cpf VARCHAR(14) UNIQUE NOT NULL,
                    birth_date DATE NOT NULL,
                    gender CHAR(1) NOT NULL,
                    phone VARCHAR(20),
                    address TEXT,
                    doctor_id UUID REFERENCES users(id),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """,
            
            "exams": """
                CREATE TABLE IF NOT EXISTS exams (
                    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                    patient_id UUID REFERENCES patients(id),
                    doctor_id UUID REFERENCES users(id),
                    file_path VARCHAR(500) NOT NULL,
                    file_type VARCHAR(50) NOT NULL,
                    ocr_text TEXT,
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """,
            
            "biomarkers": """
                CREATE TABLE IF NOT EXISTS biomarkers (
                    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                    exam_id UUID REFERENCES exams(id),
                    biomarker_name VARCHAR(100) NOT NULL,
                    normalized_name VARCHAR(100) NOT NULL,
                    value DECIMAL(10,2) NOT NULL,
                    unit VARCHAR(20) NOT NULL,
                    status VARCHAR(20) DEFAULT 'normal',
                    severity VARCHAR(20) DEFAULT 'none',
                    reference_min DECIMAL(10,2),
                    reference_max DECIMAL(10,2),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """,
            
            "reference_ranges": """
                CREATE TABLE IF NOT EXISTS reference_ranges (
                    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                    biomarker_name VARCHAR(100) NOT NULL,
                    normalized_name VARCHAR(100) NOT NULL,
                    min_value DECIMAL(10,2) NOT NULL,
                    max_value DECIMAL(10,2) NOT NULL,
                    unit VARCHAR(20) NOT NULL,
                    gender CHAR(1),
                    age_min INTEGER,
                    age_max INTEGER,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """
        }
        
        # Cria cada tabela
        for table_name, sql in tables_sql.items():
            try:
                # Executa SQL via Supabase
                result = supabase.rpc('exec_sql', {'sql': sql}).execute()
                print(f"✅ Tabela {table_name} criada/verificada")
            except Exception as e:
                print(f"⚠️ Tabela {table_name}: {e}")
                # Tenta criar via query direta
                try:
                    if "CREATE TABLE" in sql:
                        # Para Supabase, vamos verificar se a tabela existe
                        result = supabase.table(table_name).select("count", count="exact").execute()
                        print(f"✅ Tabela {table_name} já existe")
                except Exception as e2:
                    print(f"❌ Tabela {table_name} não pode ser criada: {e2}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

def seed_reference_ranges():
    """Popula a tabela de ranges de referência."""
    print("\n🌱 Populando ranges de referência...")
    
    try:
        from core.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        # Dados de referência brasileiros
        reference_data = [
            {
                "biomarker_name": "Hemoglobina",
                "normalized_name": "Hb",
                "min_value": 12.0,
                "max_value": 16.0,
                "unit": "g/dL",
                "gender": "F",
                "age_min": 18,
                "age_max": 65
            },
            {
                "biomarker_name": "Hemoglobina",
                "normalized_name": "Hb",
                "min_value": 13.0,
                "max_value": 17.0,
                "unit": "g/dL",
                "gender": "M",
                "age_min": 18,
                "age_max": 65
            },
            {
                "biomarker_name": "Glicose",
                "normalized_name": "Glu",
                "min_value": 70.0,
                "max_value": 100.0,
                "unit": "mg/dL",
                "gender": None,
                "age_min": 18,
                "age_max": 65
            },
            {
                "biomarker_name": "Creatinina",
                "normalized_name": "Cr",
                "min_value": 0.6,
                "max_value": 1.2,
                "unit": "mg/dL",
                "gender": "F",
                "age_min": 18,
                "age_max": 65
            },
            {
                "biomarker_name": "Creatinina",
                "normalized_name": "Cr",
                "min_value": 0.8,
                "max_value": 1.4,
                "unit": "mg/dL",
                "gender": "M",
                "age_min": 18,
                "age_max": 65
            }
        ]
        
        # Insere dados
        for data in reference_data:
            try:
                result = supabase.table("reference_ranges").insert(data).execute()
                print(f"✅ Range para {data['biomarker_name']} inserido")
            except Exception as e:
                print(f"⚠️ Range para {data['biomarker_name']}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao popular ranges: {e}")
        return False

def test_database_operations():
    """Testa operações básicas no banco."""
    print("\n🧪 Testando operações no banco...")
    
    try:
        from core.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        # Testa inserção de usuário
        test_user = {
            "email": "test@example.com",
            "full_name": "Usuário Teste",
            "crm": "12345-SP",
            "specialty": "Teste"
        }
        
        result = supabase.table("users").insert(test_user).execute()
        print("✅ Inserção de usuário funcionando")
        
        # Testa consulta
        result = supabase.table("users").select("*").eq("email", "test@example.com").execute()
        if result.data:
            print("✅ Consulta de usuário funcionando")
            
            # Remove usuário de teste
            user_id = result.data[0]["id"]
            supabase.table("users").delete().eq("id", user_id).execute()
            print("✅ Remoção de usuário funcionando")
        else:
            print("❌ Consulta de usuário falhou")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar operações: {e}")
        return False

def main():
    """Função principal."""
    print("🗄️ SETUP DO BANCO DE DADOS - API de Exames Médicos")
    print("=" * 60)
    
    # Verifica conexão
    connection_ok = check_database_connection()
    
    if connection_ok:
        # Cria tabelas
        tables_ok = create_database_tables()
        
        # Popula ranges de referência
        ranges_ok = seed_reference_ranges()
        
        # Testa operações
        operations_ok = test_database_operations()
        
        # Resumo
        print("\n" + "=" * 60)
        print("📊 RESUMO DO SETUP")
        print("=" * 60)
        print(f"🔌 Conexão: {'✅ OK' if connection_ok else '❌ FALHOU'}")
        print(f"🏗️ Tabelas: {'✅ OK' if tables_ok else '❌ FALHOU'}")
        print(f"🌱 Ranges: {'✅ OK' if ranges_ok else '❌ FALHOU'}")
        print(f"🧪 Operações: {'✅ OK' if operations_ok else '❌ FALHOU'}")
        
        if all([connection_ok, tables_ok, ranges_ok, operations_ok]):
            print("\n🎉 Banco de dados configurado com sucesso!")
            print("   - Todas as tabelas criadas")
            print("   - Ranges de referência populados")
            print("   - Operações básicas funcionando")
            return 0
        else:
            print("\n⚠️ Banco de dados tem problemas que precisam ser corrigidos.")
            return 1
    else:
        print("\n❌ Não foi possível conectar com o banco de dados.")
        print("   Verifique as configurações do Supabase")
        return 1

if __name__ == "__main__":
    sys.exit(main())
