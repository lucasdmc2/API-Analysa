#!/usr/bin/env python3
"""
Script para executar testes do Sprint 3 - Biomarcadores.
"""

import sys
import os
import subprocess
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def run_tests():
    """Executa todos os testes do Sprint 3."""
    print("🧪 Executando testes do Sprint 3 - Biomarcadores...")
    print("=" * 60)
    
    # Lista de testes para executar
    test_files = [
        "tests/test_biomarker_service.py",
        "tests/test_storage_service.py", 
        "tests/test_ocr_service.py",
        "tests/test_parser_service.py"
    ]
    
    results = {}
    total_tests = 0
    passed_tests = 0
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n📋 Executando: {test_file}")
            print("-" * 40)
            
            try:
                # Executa pytest no arquivo específico
                result = subprocess.run(
                    ["python3", "-m", "pytest", test_file, "-v", "--tb=short"],
                    capture_output=True,
                    text=True,
                    cwd=Path(__file__).parent.parent
                )
                
                # Analisa resultado
                if result.returncode == 0:
                    print("✅ PASSED")
                    results[test_file] = "PASSED"
                    passed_tests += 1
                else:
                    print("❌ FAILED")
                    print("Erro:")
                    print(result.stdout)
                    print(result.stderr)
                    results[test_file] = "FAILED"
                
                total_tests += 1
                
            except Exception as e:
                print(f"❌ ERROR: {e}")
                results[test_file] = "ERROR"
                total_tests += 1
        else:
            print(f"⚠️  Arquivo não encontrado: {test_file}")
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES - SPRINT 3")
    print("=" * 60)
    
    for test_file, status in results.items():
        icon = "✅" if status == "PASSED" else "❌"
        print(f"{icon} {test_file}: {status}")
    
    print(f"\n🎯 Resultado: {passed_tests}/{total_tests} testes passaram")
    
    if passed_tests == total_tests:
        print("🎉 Todos os testes do Sprint 3 passaram!")
        return True
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")
        return False

def run_coverage():
    """Executa testes com cobertura."""
    print("\n📈 Executando testes com cobertura...")
    print("=" * 60)
    
    try:
        # Executa pytest com cobertura
        result = subprocess.run(
            ["python3", "-m", "pytest", "tests/", "--cov=src", "--cov-report=term-missing"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        print(result.stdout)
        if result.stderr:
            print("Erros:")
            print(result.stderr)
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Erro ao executar cobertura: {e}")
        return False

if __name__ == "__main__":
    print("🚀 API de Exames Médicos - Testes Sprint 3")
    print("=" * 60)
    
    # Executa testes básicos
    tests_passed = run_tests()
    
    # Executa cobertura se os testes passaram
    if tests_passed:
        print("\n" + "=" * 60)
        coverage_passed = run_coverage()
        
        if coverage_passed:
            print("\n🎉 Sprint 3 está pronto para review!")
        else:
            print("\n⚠️  Cobertura falhou, mas testes básicos passaram.")
    else:
        print("\n❌ Sprint 3 precisa de correções antes do review.")
    
    print("\n" + "=" * 60)
    print("🏁 Execução concluída!")
