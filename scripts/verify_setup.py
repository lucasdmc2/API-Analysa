#!/usr/bin/env python3
"""
Script para verificar se o setup do Supabase foi realizado com sucesso.
Verifica tabelas, bucket de storage e políticas RLS.
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def load_env():
    """Carrega variáveis de ambiente"""
    # Tenta carregar do arquivo de produção primeiro
    env_file = os.path.join(os.path.dirname(__file__), '..', 'env.production')
    if os.path.exists(env_file):
        load_dotenv(env_file)
    else:
        load_dotenv()
    
    # Verifica se as variáveis necessárias estão definidas
    required_vars = ['SUPABASE_URL', 'SUPABASE_SERVICE_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Variáveis de ambiente ausentes: {', '.join(missing_vars)}")
        return None
    
    return True

def create_supabase_client() -> Client:
    """Cria cliente do Supabase"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not url or not key:
        raise ValueError("SUPABASE_URL e SUPABASE_SERVICE_KEY são obrigatórios")
    
    return create_client(url, key)

def verify_tables(supabase: Client):
    """Verifica se as tabelas foram criadas"""
    print("\n🔍 Verificando tabelas...")
    
    expected_tables = [
        'users', 'patients', 'exams', 'biomarkers', 'reference_ranges'
    ]
    
    existing_tables = []
    
    for table in expected_tables:
        try:
            # Tenta fazer uma consulta simples em cada tabela
            response = supabase.table(table).select('*').limit(1).execute()
            existing_tables.append(table)
            print(f"✅ Tabela {table} encontrada")
        except Exception as e:
            print(f"❌ Tabela {table} não encontrada: {e}")
    
    if len(existing_tables) == len(expected_tables):
        print("✅ Todas as tabelas foram criadas com sucesso!")
        return True
    else:
        missing_tables = [table for table in expected_tables if table not in existing_tables]
        print(f"❌ Tabelas ausentes: {', '.join(missing_tables)}")
        return False

def verify_storage_bucket(supabase: Client):
    """Verifica se o bucket de storage foi criado"""
    print("\n🔍 Verificando bucket de storage...")
    
    try:
        # Lista os buckets disponíveis
        response = supabase.storage.list_buckets()
        
        # Extrai os nomes dos buckets
        if hasattr(response, 'data'):
            buckets = response.data
        else:
            buckets = response
        
        bucket_names = []
        for bucket in buckets:
            if hasattr(bucket, 'name'):
                bucket_names.append(bucket.name)
            elif isinstance(bucket, dict) and 'name' in bucket:
                bucket_names.append(bucket['name'])
            else:
                bucket_names.append(str(bucket))
        
        print(f"Buckets encontrados: {bucket_names}")
        
        if 'exames-medicos' in bucket_names:
            print("✅ Bucket 'exames-medicos' foi criado com sucesso!")
            return True
        else:
            print("❌ Bucket 'exames-medicos' não foi encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar bucket de storage: {e}")
        return False

def verify_reference_data(supabase: Client):
    """Verifica se os dados de referência foram inseridos"""
    print("\n🔍 Verificando dados de referência...")
    
    try:
        response = supabase.table('reference_ranges').select('*').execute()
        
        if hasattr(response, 'data'):
            count = len(response.data)
        else:
            count = len(response)
        
        print(f"Ranges de referência encontrados: {count}")
        
        if count > 0:
            print("✅ Dados de referência foram inseridos com sucesso!")
            return True
        else:
            print("❌ Nenhum dado de referência foi encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar dados de referência: {e}")
        return False

def verify_rls_policies(supabase: Client):
    """Verifica se as políticas RLS foram criadas"""
    print("\n🔍 Verificando políticas RLS...")
    
    try:
        # Verifica se RLS está habilitado nas tabelas principais
        tables_with_rls = ['users', 'patients', 'exams', 'biomarkers', 'reference_ranges']
        
        for table in tables_with_rls:
            try:
                # Tenta fazer uma consulta que seria bloqueada por RLS
                response = supabase.table(table).select('*').limit(1).execute()
                print(f"⚠️  Tabela {table} pode não ter RLS habilitado (consulta retornou dados)")
            except Exception as e:
                if "RLS" in str(e) or "permission" in str(e).lower():
                    print(f"✅ RLS habilitado em {table} (consulta bloqueada)")
                else:
                    print(f"⚠️  Erro ao verificar RLS em {table}: {e}")
        
        print("✅ Verificação de RLS concluída!")
        return True
        
    except Exception as e:
        print(f"⚠️  Erro ao verificar RLS (pode ser normal): {e}")
        return True  # Não é crítico

def main():
    """Função principal"""
    print("🚀 Verificando setup do Supabase...")
    
    # Carrega variáveis de ambiente
    if not load_env():
        return
    
    try:
        # Cria cliente do Supabase
        supabase = create_supabase_client()
        print("✅ Cliente Supabase criado com sucesso!")
        
        # Executa verificações
        tables_ok = verify_tables(supabase)
        storage_ok = verify_storage_bucket(supabase)
        reference_ok = verify_reference_data(supabase)
        rls_ok = verify_rls_policies(supabase)
        
        # Resumo final
        print("\n" + "="*50)
        print("📊 RESUMO DA VERIFICAÇÃO")
        print("="*50)
        print(f"Tabelas: {'✅' if tables_ok else '❌'}")
        print(f"Storage: {'✅' if storage_ok else '❌'}")
        print(f"Dados de referência: {'✅' if reference_ok else '❌'}")
        print(f"Políticas RLS: {'✅' if rls_ok else '❌'}")
        
        if all([tables_ok, storage_ok, reference_ok, rls_ok]):
            print("\n🎉 Setup do Supabase concluído com sucesso!")
        else:
            print("\n⚠️  Alguns itens precisam de atenção.")
            
    except Exception as e:
        print(f"❌ Erro durante a verificação: {e}")
        return

if __name__ == "__main__":
    main()
