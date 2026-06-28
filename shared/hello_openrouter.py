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
        # === ATENÇÃO: GLM-5.2 É UM MODELO DE RACIOCÍNIO ===
        # Modelos de raciocínio (como GLM-5.2, DeepSeek-R1, o1) «pensam» em voz
        # alta antes de responder. Esse «pensamento» fica no campo `reasoning` e
        # consome tokens. Com max_tokens baixo demais, o modelo esgota o limite
        # pensando e nunca chega a preencher o `content`. Por isso usamos 1024.
        max_tokens=1024,
    )

    message = response.choices[0].message
    usage = response.usage  # objeto com contagem de tokens

    # === LEITURA DO CONTEÚDO — SUPORTE A MODELOS DE RACIOCÍNIO ===
    # Modelos de raciocínio separam o «pensamento» (reasoning) da «resposta» (content).
    # Se o content vier None, lemos o reasoning — que é o próprio raciocínio do modelo.
    # reasoning_tokens indica quantos tokens foram usados só para «pensar».
    answer = message.content
    reasoning = getattr(message, "reasoning", None)  # campo extra do OpenRouter

    if answer is None and reasoning:
        # O modelo pensou mas não gerou content separado — exibimos o raciocínio.
        answer = f"[raciocínio do modelo]:\n{reasoning}"
    elif answer is None:
        answer = "(sem resposta — verifique finish_reason)"

    print("✅ Resposta:")
    print(f"   {answer}\n")

    # === TOKENS: breakdown de reasoning vs completion ===
    # O OpenRouter reporta reasoning_tokens em completion_tokens_details.
    # Para GLM-5.2, os tokens de raciocínio = total_tokens - prompt - completion.
    # Exibimos só se houver raciocínio real (> 0).
    raw_reasoning = 0
    if usage.completion_tokens_details:
        raw_reasoning = getattr(usage.completion_tokens_details, "reasoning_tokens", 0) or 0
    # Garante que não ultrapassa os completion_tokens (proteção contra campo errado)
    reasoning_tokens = min(raw_reasoning, usage.completion_tokens)

    print(f"📊 Tokens — input: {usage.prompt_tokens} | output: {usage.completion_tokens} | total: {usage.total_tokens}")
    if reasoning_tokens and reasoning_tokens < usage.completion_tokens:
        visible_tokens = usage.completion_tokens - reasoning_tokens
        print(f"   └─ raciocínio interno: {reasoning_tokens} tokens | resposta visível: {visible_tokens} tokens")

    # === 6. CUSTO REAL — lido diretamente do campo `cost` do OpenRouter ===
    # O OpenRouter retorna o custo exato em `usage.cost` (em USD).
    # Usamos esse valor quando disponível; caso contrário, calculamos manualmente.
    real_cost = getattr(usage, "cost", None)
    if real_cost is not None:
        print(f"💰 Custo real (OpenRouter): ${real_cost:.6f} USD")
    else:
        # Fallback: preço público GLM-5.2 — Input $1.20/1M | Output $4.20/1M tokens
        cost_input = (usage.prompt_tokens * 1.20) / 1_000_000
        cost_output = (usage.completion_tokens * 4.20) / 1_000_000
        print(f"💰 Custo estimado: ${cost_input + cost_output:.6f} USD")

except Exception as e:
    # IMPORTANTE: imprimimos o TIPO do erro e a mensagem padrão, mas
    # nunca printamos o objeto cliente nem variáveis de ambiente.
    # Algumas bibliotecas incluem headers (com a chave!) em stack trace
    # verbose — evitamos isso aqui.
    print(f"❌ Falha na chamada: {type(e).__name__}")
    print(f"   Mensagem: {e}")
    sys.exit(1)
