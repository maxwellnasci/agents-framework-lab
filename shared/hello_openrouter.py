"""
hello_openrouter.py — Primeiro teste de conectividade do framework-lab.

OBJETIVO: enviar uma mensagem simples ao GLM-5.2 via OpenRouter e
imprimir resposta + custo. Serve como validação de:
  1. Credenciais carregando do .env
  2. Conectividade com OpenRouter
  3. Modelo GLM-5.2 respondendo

POSTURA DE SEGURANÇA:
  - Chave NUNCA hardcoded; lida do .env via python-dotenv
  - Fail-fast: se a chave está faltando, encerra antes de tentar conectar
  - Mensagem de teste é genérica, sem dado sensível
  - Stack traces não imprimem o conteúdo da chave
"""

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# === 1. CARREGA AS VARIÁVEIS DO .env ===
# A função load_dotenv() lê o arquivo .env (na raiz do projeto) e
# injeta cada par CHAVE=VALOR em os.environ. A partir daqui, podemos
# ler as variáveis com os.getenv("NOME"). O arquivo .env NUNCA vai
# pro Git porque está listado no .gitignore.
load_dotenv()

# === 2. LÊ AS VARIÁVEIS NECESSÁRIAS ===
# os.getenv() retorna None se a variável não existir. O segundo
# argumento é um valor padrão usado quando a variável não está definida.
API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.getenv("MODEL_GLM", "z-ai/glm-5.2")

# === 3. FAIL-FAST — VALIDA A CHAVE ANTES DE TENTAR CONECTAR ===
# Se a chave não foi definida OU ainda contém o placeholder do template,
# encerra imediatamente com mensagem clara. Princípio: falhar cedo, com
# mensagem útil, em vez de tentar conectar e dar erro confuso depois.
if not API_KEY or API_KEY.startswith("sk-or-v1-COLE"):
    print("❌ ERRO: OPENROUTER_API_KEY não configurada no .env")
    print("   Passos:")
    print("   1. cp .env.example .env")
    print("   2. Edita .env e cola sua chave real do OpenRouter")
    print("   3. Roda o script de novo")
    sys.exit(1)

# === 4. CRIA O CLIENTE OPENAI-COMPATIBLE APONTADO PRO OPENROUTER ===
# O SDK oficial da OpenAI funciona com qualquer endpoint que respeite
# o mesmo formato de API. OpenRouter respeita. Resultado: trocamos só
# a base_url e ganhamos acesso a 300+ modelos com o mesmo código.
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

print(f"🔗 Endpoint: {BASE_URL}")
print(f"🤖 Modelo:   {MODEL}")
print(f"💬 Pergunta: 'Olá! Em uma frase, quem é você?'\n")

# === 5. FAZ A CHAMADA, CAPTURA ERROS SEM VAZAR A CHAVE ===
try:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": "Olá! Em uma frase, quem é você?"}
        ],
        max_tokens=150,  # limita resposta pra não estourar conta em teste
    )

    # response.choices é uma lista (pode ter múltiplas respostas, mas
    # por padrão tem só uma). [0] pega a primeira. .message.content
    # é o texto que o modelo gerou.
    answer = response.choices[0].message.content
    usage = response.usage  # objeto com contagem de tokens

    print("✅ Resposta:")
    print(f"   {answer}\n")
    print(f"📊 Tokens — input: {usage.prompt_tokens} | output: {usage.completion_tokens} | total: {usage.total_tokens}")

    # === 6. ESTIMATIVA DE CUSTO (preço público GLM-5.2 no OpenRouter) ===
    # Input: $1.40 por 1M tokens. Output: $4.40 por 1M tokens.
    # Fórmula: (tokens * preço) / 1_000_000
    cost_input = (usage.prompt_tokens * 1.40) / 1_000_000
    cost_output = (usage.completion_tokens * 4.40) / 1_000_000
    cost_total = cost_input + cost_output
    print(f"💰 Custo estimado: ${cost_total:.6f} USD")

except Exception as e:
    # IMPORTANTE: imprimimos o TIPO do erro e a mensagem padrão, mas
    # nunca printamos o objeto cliente nem variáveis de ambiente.
    # Algumas bibliotecas incluem headers (com a chave!) em stack trace
    # verbose — evitamos isso aqui.
    print(f"❌ Falha na chamada: {type(e).__name__}")
    print(f"   Mensagem: {e}")
    sys.exit(1)
