# 01 — Pydantic AI

> Semana 1 do framework-lab — testando Pydantic AI v2.0.0 com GLM-5.2 via OpenRouter.

## Por que começar por Pydantic AI

- **Sintaxe limpa**: type hints estilo FastAPI, ideal pra aprender Python estruturado
- **Validação automática**: outputs do LLM passam por Pydantic = barreira contra dados malformados
- **Human-in-the-Loop nativo**: tool approval pré-built (relevante pro ângulo cibersec)
- **Mantenedores fortes**: Pydantic Services Inc, time por trás da Pydantic Validation usada por OpenAI/Anthropic/LangChain

## Plano da semana

| Dia | Arquivo | O que faz |
|---|---|---|
| 1 | `hello_pydantic.py` | Hello world Pydantic AI + GLM-5.2 (comparação com `shared/hello_openrouter.py`) |
| 2 | `weather_agent.py` | Agente com tool use real (Open-Meteo API) |
| 3 | `secure_agent.py` | Mesmo agente + Human-in-the-Loop tool approval |
| 4 | (análise) | Doc honesto em `docs/01-pydantic-ai.md` |
| 5 | (post) | Rascunho LinkedIn em `docs/posts/semana-1-pydantic-ai.md` |

## Como rodar

```bash
cd /caminho/agents-framework-lab
source venv/bin/activate
python 01-pydantic-ai/hello_pydantic.py
```

Pré-requisitos: `.env` com `OPENROUTER_API_KEY` (ver `.env.example` na raiz).

