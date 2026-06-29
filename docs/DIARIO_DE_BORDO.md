# 📓 Diário de Bordo — Agents Framework Lab

Este arquivo documenta o progresso, aprendizados e decisões técnicas do laboratório. Serve como contexto principal (catch-up) para outros agentes de IA e colaboradores do projeto.

## 📅 Sessão Atual: Setup Inicial e Fase 1 (Hello World OpenRouter)

### O que foi feito até agora:

**1. Bootstrap do Repositório (Fase 0)**
- Repositório `agents-framework-lab` criado no GitHub (público) e clonado localmente.
- Estrutura de diretórios inicializada (`01-pydantic-ai/`, `02-langchain/`, `03-langgraph/`, `04-claude-agent-sdk/`, `shared/`, `docs/`).
- Postura de cibersegurança aplicada:
  - Arquivo `.gitignore` configurado rigorosamente para bloquear `.env`, `venv/`, logs, caches e chaves/certificados acidentais.
  - Arquivo template `.env.example` criado, sem as credenciais reais. O `.env` real é mantido apenas na máquina local.
  - Adicionada a Licença MIT e o `README.md` raiz detalhando a tese do projeto (cibersegurança aplicada + soberania de dados usando modelos open-weights).

**2. Integração com LLM (Fase 1)**
- Ambiente virtual Python (`venv/`) inicializado.
- Dependências base instaladas (`openai>=1.50.0`, `python-dotenv>=1.0.0`) e salvas em `shared/requirements.txt`.
- Script base de conectividade criado (`shared/hello_openrouter.py`).
  - O script faz o carregamento seguro da API key.
  - Contém lógica "Fail-Fast": encerra o programa com instruções claras caso a chave não esteja configurada corretamente.
  - Conecta à API do OpenRouter via SDK compatível da OpenAI.

**3. Fix de Raciocínio (Deep Dive no Modelo GLM-5.2)**
- **Incidente:** O primeiro teste com a pergunta "Em uma frase, quem é você?" retornou texto vazio (`None`), mas consumiu tokens.
- **Diagnóstico Analítico:** O modelo `z-ai/glm-5.2` opera como um **modelo de raciocínio avançado** (assim como DeepSeek-R1 e o1). Ele "pensa em voz alta" usando o payload de `reasoning` do provedor antes de escrever a resposta final (`content`). Com `max_tokens=150`, ele gastava todo o limite no raciocínio e o texto da resposta era abortado (finish_reason = length).
- **Correções Aplicadas:**
  - `max_tokens` aumentado para 1024, dando margem confortável ao raciocínio + saída.
  - Refatoração do script para capturar e ler condicionalmente o campo oculto `.reasoning` do payload do OpenRouter.
  - O script agora imprime na tela as métricas precisas: cálculo real de custo (via campo `usage.cost`) e separação de quantos tokens foram usados para raciocínio interno invisível e quantos foram da resposta final.

### Próximos Passos (Para a próxima sessão)
- Iniciar a **Semana 1 — Pydantic AI**: O objetivo será construir o primeiro framework utilizando o modelo GLM-5.2 (reaproveitando o cliente criado na Fase 1) para desenvolver o agente climático integrado à API.

---

## Fase 2 — Semana 1: Pydantic AI

### Dia 1 — Hello World (data: 2026-06-29)

**Objetivo:** primeira chamada via Pydantic AI, comparável ao `shared/hello_openrouter.py`.

**Entregue:**
- `01-pydantic-ai/hello_pydantic.py` — hello world com comentários didáticos
- `01-pydantic-ai/README.md` — atualizado com plano da semana
- `shared/requirements.txt` — atualizado com `pydantic-ai>=1.0.0`

**Versão instalada:** pydantic-ai `2.0.0`

**Abordagem OpenRouter usada:** Tenta A (OpenRouterProvider nativo) com fallback automático pra B (OpenAIProvider + base_url). Qual funcionou será confirmado pelo Max após rodar o script.

**O que o Pydantic AI adiciona vs hello_openrouter.py:**
- Não é preciso montar dicionário `{"role": "user", "content": ...}` manualmente
- O `Agent` encapsula modelo + instruções + tools em um objeto único e reutilizável
- Retorno tipado (`result.output`) em vez de dicionário JSON cru
- Validação Pydantic automática em background

**Commit:** `e1dc42a`

**Próximo passo:** Max roda `python 01-pydantic-ai/hello_pydantic.py` manualmente e reporta o output. Depois seguimos pro Dia 2 (weather_agent.py com tool use real).

### Bug encontrado e fix aplicado (Dia 1)

**Sintoma:** após GLM-5.2 responder corretamente, o script quebrava com:
```
❌ Falha na chamada: TypeError
   Mensagem: 'RunUsage' object is not callable
```

**Causa raiz:** Pydantic AI 2.0 mudou `result.usage` de método para propriedade (breaking change vs v1.85). O código original chamava com parênteses (`result.usage()`) como se fosse função.

**Fix:** remover os parênteses — `usage = result.usage`.

**API verificada via `help(RunUsage)` — atributos confirmados na v2.0.0:**
- `input_tokens` ✅ (mesmo nome)
- `output_tokens` ✅ (mesmo nome)
- `total_tokens` ✅ (propriedade calculada: input + output)
- Bônus descoberto: também tem `cache_read_tokens`, `requests`, `tool_calls`

**Aprendizado pro lab:**
1. Sempre verificar versão exata da biblioteca antes de seguir tutorial antigo
2. `TypeError: X object is not callable` = tentamos chamar como função algo que não é
3. Major releases (1.x → 2.0) frequentemente movem métodos pra propriedades. Ler CHANGELOG é parte do trabalho de cibersec (mudança de API pode esconder mudança de comportamento de segurança)

**Versão confirmada:** pydantic-ai 2.0.0
**Abordagem OpenRouter confirmada:** A (OpenRouterProvider nativo) — suporte maduro
**Commit do fix:** `87f9936`

### Run final pós-fix (Dia 1 fechado)

**Comando executado:**
```bash
source venv/bin/activate
python 01-pydantic-ai/hello_pydantic.py
```

**Output:**
```
🔗 Framework:  Pydantic AI
🛰️  Abordagem: A (OpenRouterProvider nativo)
🤖 Modelo:     z-ai/glm-5.2
💬 Pergunta:   'Olá! Em uma frase, quem é você?'

✅ Resposta:
   Sou um assistente de inteligência artificial criado para responder
   às suas perguntas e ajudar em suas tarefas do dia a dia.

📊 Tokens — input: 50 | output: 282 | total: 332
💰 Custo estimado: $0.001311 USD
```

**Status:** ✅ Dia 1 oficialmente fechado.

### Observação técnica (material pro post da Semana 1)

Comparando os dois hello worlds rodando o MESMO modelo (GLM-5.2) com a MESMA pergunta:

| Métrica | `shared/hello_openrouter.py` (raw API) | `01-pydantic-ai/hello_pydantic.py` (framework) | Delta |
|---|---|---|---|
| Tokens input | 23 | 50 | +27 (instructions mais estruturadas) |
| Tokens output (inclui reasoning) | 394 | 282 | -112 (~28% menor) |
| Custo total | $0.001682 | $0.001311 | -$0.000371 (~22% menor) |

**Hipótese inicial (a verificar nos próximos dias):** Pydantic AI estrutura o system prompt de forma que reduz tokens de raciocínio em modelos reasoning como GLM-5.2. Pode ser por: (a) instructions mais claras, (b) framing mais determinístico do output esperado, (c) random run-to-run variance.

**Próximo passo:** repetir o experimento N=10 cada lado no Dia 4 (análise) pra ver se a economia é estatisticamente consistente ou ruído. Se for consistente, vira gráfico do post LinkedIn da Semana 1.

### Status geral

- ✅ Dia 1 — Hello world Pydantic AI (FECHADO)
- ⏳ Dia 2 — `weather_agent.py` com tool use (Open-Meteo API)
- ⏳ Dia 3 — `secure_agent.py` com Human-in-the-Loop tool approval
- ⏳ Dia 4 — Análise comparativa + repetição estatística do experimento de tokens
- ⏳ Dia 5 — Rascunho do post LinkedIn

**Commit do fechamento:** (preencher após push)
