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
