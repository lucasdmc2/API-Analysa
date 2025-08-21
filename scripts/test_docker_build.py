#!/usr/bin/env python3
"""
Script para testar o build e execução do Docker localmente.
"""

import subprocess
import time
import requests
import sys
from pathlib import Path

def run_command(command, check=True):
    """Executa um comando e retorna o resultado."""
    print(f"🔄 Executando: {command}")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ Saída: {result.stdout.strip()}")
        if result.stderr:
            print(f"⚠️  Erro: {result.stderr.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar comando: {e}")
        if check:
            raise
        return e

def test_docker_build():
    """Testa o build do Docker."""
    print("🐳 Testando build do Docker...")
    
    # Parar e remover containers existentes
    run_command("docker stop api-analysa-test 2>/dev/null || true", check=False)
    run_command("docker rm api-analysa-test 2>/dev/null || true", check=False)
    
    # Remover imagem existente
    run_command("docker rmi api-analysa-test 2>/dev/null || true", check=False)
    
    # Build da imagem
    result = run_command("docker build -t api-analysa-test .")
    if result.returncode != 0:
        print("❌ Falha no build do Docker")
        return False
    
    print("✅ Build do Docker concluído com sucesso")
    return True

def test_docker_run():
    """Testa a execução do container Docker."""
    print("🚀 Testando execução do container...")
    
    # Executar container
    run_command(
        "docker run -d --name api-analysa-test -p 8000:8000 "
        "-e PORT=8000 -e DEBUG=false -e LOG_LEVEL=INFO "
        "api-analysa-test"
    )
    
    # Aguardar inicialização
    print("⏳ Aguardando inicialização da aplicação...")
    time.sleep(10)
    
    # Verificar se o container está rodando
    result = run_command("docker ps --filter name=api-analysa-test --format '{{.Status}}'")
    if "Up" not in result.stdout:
        print("❌ Container não está rodando")
        return False
    
    print("✅ Container está rodando")
    return True

def test_health_endpoint():
    """Testa o endpoint de health check."""
    print("🏥 Testando endpoint de health check...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            print("✅ Endpoint /health funcionando")
            print(f"📊 Resposta: {response.json()}")
            return True
        else:
            print(f"❌ Endpoint /health retornou status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao acessar endpoint /health: {e}")
        return False

def test_root_endpoint():
    """Testa o endpoint raiz."""
    print("🏠 Testando endpoint raiz...")
    
    try:
        response = requests.get("http://localhost:8000/", timeout=10)
        if response.status_code == 200:
            print("✅ Endpoint raiz funcionando")
            print(f"📊 Resposta: {response.json()}")
            return True
        else:
            print(f"❌ Endpoint raiz retornou status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao acessar endpoint raiz: {e}")
        return False

def cleanup():
    """Limpa recursos de teste."""
    print("🧹 Limpando recursos de teste...")
    run_command("docker stop api-analysa-test 2>/dev/null || true", check=False)
    run_command("docker rm api-analysa-test 2>/dev/null || true", check=False)
    run_command("docker rmi api-analysa-test 2>/dev/null || true", check=False)

def main():
    """Função principal."""
    print("🧪 Iniciando testes do Docker para Railway...")
    print("=" * 60)
    
    try:
        # Teste 1: Build do Docker
        if not test_docker_build():
            return 1
        
        # Teste 2: Execução do container
        if not test_docker_run():
            return 1
        
        # Teste 3: Health endpoint
        if not test_health_endpoint():
            return 1
        
        # Teste 4: Root endpoint
        if not test_root_endpoint():
            return 1
        
        print("\n🎉 Todos os testes passaram! O Docker está pronto para o Railway.")
        print("💡 Você pode fazer o deploy agora.")
        
    except KeyboardInterrupt:
        print("\n🛑 Testes interrompidos pelo usuário")
        return 1
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        return 1
    finally:
        cleanup()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
