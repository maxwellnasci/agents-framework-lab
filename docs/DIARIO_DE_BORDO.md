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

**Commit:** (preencher após push)

**Próximo passo:** Max roda `python 01-pydantic-ai/hello_pydantic.py` manualmente e reporta o output. Depois seguimos pro Dia 2 (weather_agent.py com tool use real).
