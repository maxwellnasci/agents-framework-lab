"""
hello_pydantic.py — Primeira chamada usando Pydantic AI.

OBJETIVO: fazer a MESMA pergunta que shared/hello_openrouter.py faz,
mas usando o framework Pydantic AI em vez da chamada OpenAI crua.
Serve como comparação didática: o que Pydantic AI adiciona ao código?

COMPARAÇÃO ESPERADA (vs hello_openrouter.py):
  - Não precisamos montar dicionário {"role": "user", "content": ...}
  - O Agent encapsula modelo + instruções + tools em um objeto único
  - O retorno é objeto tipado (result.output), não dicionário JSON
  - Tudo passa por validação Pydantic automaticamente

POSTURA DE SEGURANÇA (mesma de hello_openrouter.py):
  - Chave NUNCA hardcoded; lida do .env
  - Fail-fast: encerra se a chave está faltando
  - Mensagem genérica, sem dado sensível
  - Tratamento de exceções sem vazar credenciais em stack trace

ABORDAGEM OPENROUTER USADA: A (OpenRouterProvider nativo)
  Confirmada em runtime com pydantic-ai==2.0.0
  Abordagem B (OpenAIProvider com base_url) mantida como fallback
"""

import os
import sys
from dotenv import load_dotenv

# === 1. CARREGA VARIÁVEIS DO .env (igual ao hello_openrouter.py) ===
load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = os.getenv("MODEL_GLM", "z-ai/glm-5.2")

# === 2. FAIL-FAST (igual ao hello_openrouter.py) ===
if not API_KEY or API_KEY.startswith("sk-or-v1-COLE"):
    print("❌ ERRO: OPENROUTER_API_KEY não configurada no .env")
    sys.exit(1)

# === 3. IMPORTAÇÃO DO PYDANTIC AI ===
# Aqui está a primeira diferença vs hello_openrouter.py:
# Em vez de criar um cliente OpenAI direto, montamos um "modelo"
# que encapsula PROVIDER (quem hospeda) + MODEL_ID (qual modelo).
# Isso é o que permite trocar provider sem mudar o resto do código.
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel

# TENTA ABORDAGEM A (provider nativo OpenRouter). Se falhar, cai pra B.
try:
    from pydantic_ai.providers.openrouter import OpenRouterProvider
    model = OpenAIChatModel(
        MODEL_NAME,
        provider=OpenRouterProvider(api_key=API_KEY),
    )
    ABORDAGEM = "A (OpenRouterProvider nativo)"
except ImportError:
    from pydantic_ai.providers.openai import OpenAIProvider
    model = OpenAIChatModel(
        MODEL_NAME,
        provider=OpenAIProvider(
            api_key=API_KEY,
            base_url="https://openrouter.ai/api/v1",
        ),
    )
    ABORDAGEM = "B (OpenAIProvider com base_url customizada)"

# === 4. CRIA O AGENT ===
# Agent é o objeto central do Pydantic AI. Aqui ele recebe:
#   - model: qual LLM usar (já configurado acima)
#   - instructions: prompt de sistema fixo (equivalente ao "system message")
# Conforme avançamos, vamos adicionar deps_type, output_type e tools.
agent = Agent(
    model,
    instructions="Você é um assistente IA. Responda sempre em português brasileiro, de forma direta e em uma frase.",
)

print(f"🔗 Framework:  Pydantic AI")
print(f"🛰️  Abordagem: {ABORDAGEM}")
print(f"🤖 Modelo:     {MODEL_NAME}")
print(f"💬 Pergunta:   'Olá! Em uma frase, quem é você?'\n")

# === 5. EXECUTA O AGENT ===
# run_sync = roda síncrono (bloqueante). Existe também run() (async) e
# run_stream() (streaming). Pra hello world, síncrono basta.
# IMPORTANTE: GLM-5.2 é modelo de raciocínio — pode usar muitos tokens
# pensando antes de responder. Aprendemos isso no hello_openrouter.py.
try:
    result = agent.run_sync("Olá! Em uma frase, quem é você?")

    # result.output é a saída tipada (no nosso caso, string, porque não
    # definimos output_type ainda — então é o tipo padrão str).
    print("✅ Resposta:")
    print(f"   {result.output}\n")

    # result.usage() retorna estatísticas de uso (tokens, custo).
    # Diferente do hello_openrouter.py, o Pydantic AI já agrega isso
    # automaticamente em um objeto Usage.
    # Pydantic AI 2.0 mudou usage de método pra propriedade
    # (antes era result.usage(), agora result.usage). Breaking change da v2.0.
    usage = result.usage
    print(f"📊 Tokens — input: {usage.input_tokens} | output: {usage.output_tokens} | total: {usage.total_tokens}")

    # Estimativa de custo (GLM-5.2 no OpenRouter):
    # Input: $1.40/M tokens | Output: $4.40/M tokens
    if usage.input_tokens and usage.output_tokens:
        cost = (usage.input_tokens * 1.40 + usage.output_tokens * 4.40) / 1_000_000
        print(f"💰 Custo estimado: ${cost:.6f} USD")

except Exception as e:
    print(f"❌ Falha na chamada: {type(e).__name__}")
    print(f"   Mensagem: {e}")
    sys.exit(1)
