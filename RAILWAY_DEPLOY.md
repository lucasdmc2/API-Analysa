# 🚀 Deploy no Railway - API de Exames Médicos

## 📋 Pré-requisitos

- Conta no Railway (https://railway.app)
- Docker instalado localmente (para testes)
- Git configurado

## 🔧 Configurações Corrigidas

### Problema Identificado
O deploy estava falhando porque a variável `$PORT` não estava sendo interpretada corretamente no comando uvicorn.

### Soluções Implementadas

1. **Dockerfile Atualizado**
   - Criado script de entrada que interpreta a variável `PORT`
   - Fallback para porta 8000 se `PORT` não estiver definida
   - Comando CMD simplificado

2. **railway.json Simplificado**
   - Removido `startCommand` personalizado
   - Deixado o Dockerfile gerenciar a inicialização
   - Mantidas configurações de health check e restart

3. **Arquivos de Otimização**
   - `.dockerignore` para build mais rápido
   - Script de teste local

## 🧪 Teste Local

Antes do deploy, teste localmente:

```bash
# Executar testes do Docker
python scripts/test_docker_build.py

# Ou testar manualmente
docker build -t api-analysa-test .
docker run -d --name api-test -p 8000:8000 -e PORT=8000 api-analysa-test
curl http://localhost:8000/health
```

## 🚀 Deploy no Railway

### 1. Conectar Repositório
- Faça login no Railway
- Clique em "New Project"
- Selecione "Deploy from GitHub repo"
- Conecte seu repositório

### 2. Configurações do Projeto
- **Builder**: Dockerfile
- **Dockerfile Path**: `Dockerfile`
- **Health Check Path**: `/health`
- **Health Check Timeout**: 300s

### 3. Variáveis de Ambiente
Configure as seguintes variáveis no Railway:

#### Produção
```
DEBUG=false
LOG_LEVEL=INFO
SUPABASE_URL=sua_url_do_supabase
SUPABASE_ANON_KEY=sua_chave_anonima
SUPABASE_SERVICE_KEY=sua_chave_de_servico
SECRET_KEY=sua_chave_secreta
MAX_FILE_SIZE=5242880
TESSERACT_CMD=/usr/bin/tesseract
```

#### Staging (opcional)
```
DEBUG=true
LOG_LEVEL=DEBUG
SUPABASE_URL=sua_url_do_supabase
SUPABASE_ANON_KEY=sua_chave_anonima
SUPABASE_SERVICE_KEY=sua_chave_de_servico
SECRET_KEY=sua_chave_secreta
MAX_FILE_SIZE=5242880
TESSERACT_CMD=/usr/bin/tesseract
```

### 4. Deploy
- Clique em "Deploy"
- Aguarde o build e deploy
- Verifique os logs para confirmar sucesso

## 🔍 Verificação do Deploy

### 1. Health Check
```bash
curl https://seu-app.railway.app/health
```

### 2. Endpoint Raiz
```bash
curl https://seu-app.railway.app/
```

### 3. Swagger UI
```
https://seu-app.railway.app/docs
```

## 🐛 Troubleshooting

### Erro: "Invalid value for '--port': '$PORT' is not a valid integer"
- ✅ **Resolvido**: Dockerfile atualizado com script de entrada
- ✅ **Resolvido**: railway.json simplificado

### Erro: "Container failed to start"
- Verifique os logs do Railway
- Confirme que as variáveis de ambiente estão configuradas
- Teste localmente primeiro

### Erro: "Health check failed"
- Verifique se o endpoint `/health` está funcionando
- Confirme que a aplicação está respondendo na porta correta
- Aumente o timeout se necessário

## 📊 Monitoramento

### Logs do Railway
- Acesse a aba "Deployments"
- Clique no deployment mais recente
- Verifique os logs para debugging

### Métricas
- Uptime da aplicação
- Tempo de resposta
- Uso de recursos

## 🔄 Atualizações

Para atualizar a aplicação:
1. Faça push para o branch principal
2. Railway fará deploy automático
3. Monitore os logs do novo deployment

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs do Railway
2. Teste localmente com o script de teste
3. Confirme as variáveis de ambiente
4. Verifique se o Dockerfile está correto

---

**🎯 Status**: ✅ Problema do deploy resolvido
**📅 Última Atualização**: Janeiro 2025
**🔧 Versão**: 1.0.0
