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

**Commit do fechamento:** `9ffe83d`

---

### Dia 2 — 09/07/2026 — Tool use + backend local (Ollama/Nemotron)

#### Parte A — Infraestrutura local: Ollama + Nemotron-3-Nano 4B

**O que foi feito:**
- Instalado **Ollama 0.31.2** no Kali Linux via script oficial. Instalador detectou GPU NVIDIA, mas inferência roda 100% CPU (GTX de 4GB não utilizada pelo runtime).
- Baixado modelo **`nemotron-3-nano:4b`** (NVIDIA Nemotron 3 Nano, 3.97B parâmetros, quantização Q4_K_M, 2,8 GB de download, licença NVIDIA Open Model License).
- ⚠️ **Pegadinha de registry:** `ollama pull nemotron-nano` retorna "file does not exist". Nome correto: `nemotron-3-nano:4b`. A tag `latest` puxaria a versão 30B (24 GB) — sempre especificar `:4b`.

**Medições via `ollama ps`:**
- RAM em uso: ~3,1 GB
- CPU: 100% durante inferência
- Contexto padrão: 4096 tokens (suporta 256K, mas Ollama limita por padrão)
- O modelo é de **reasoning**: exibe cadeia de pensamento antes da resposta (em inglês), mas responde em português correto.

**Motivação estratégica:** validar que agentes rodam em hardware corporativo comum (alvo: notebook i5 12ª gen, 16 GB RAM, sem GPU útil) — pilar da tese de soberania de dados e LGPD do lab.

---

#### Parte B — `weather_agent.py` (Dia 2 do plano original)

**Arquivo criado:** `01-pydantic-ai/weather_agent.py` (~2,3 KB)

**O que faz:** agente Pydantic AI com tool use via API Open-Meteo (geocoding + forecast, sem API key). Recurso central: **dual-backend por variável de ambiente** — `AGENT_BACKEND=openrouter` (padrão, GLM-5.2 na nuvem) ou `AGENT_BACKEND=local` (Nemotron via Ollama em `http://localhost:11434/v1`, usando `OpenAIProvider` com `base_url` custom). **Zero mudança de código entre backends.**

**Frase-tese validada:**
> "Mesmo código, mesmo agente — trocando uma variável de ambiente, o cérebro sai da nuvem e roda dentro da máquina."
> (pilar central do argumento de soberania de dados/LGPD do lab)

**Detalhes de implementação (aplicando lições do Dia 1):**
- `model_settings={"max_tokens": 2048}` — modelos de reasoning consomem tokens pensando; limite baixo mata a resposta (lição do Dia 1 com GLM-5.2).
- `result.usage` SEM parênteses — Pydantic AI 2.0 mudou de método para property (fix documentado no Dia 1).
- Ferramenta registrada com `@agent.tool_plain`; system prompt força uso da ferramenta e resposta em pt-BR.

**Commit:** `5013d0a`

---

#### Parte C — Resultados dos testes

Ambos funcionaram de primeira.

**Teste 1 — nuvem (GLM-5.2 via OpenRouter):**
```
Pergunta: "Qual o clima agora em Curitiba?"
Resposta: correta, dados reais (12,2°C, vento 5,9 km/h, umidade 61%), estilo florido com emojis
RunUsage(input_tokens=546, cache_read_tokens=419, output_tokens=131,
         reasoning_tokens=41, requests=2, tool_calls=1)
```

**Teste 2 — local (Nemotron 4B via Ollama, 100% CPU):**
```
Comando: AGENT_BACKEND=local python weather_agent.py "Qual o clima agora em Curitiba?"
Resposta: correta, mesmos dados (12°C, 5,9 km/h, 61%), estilo seco e direto
RunUsage(input_tokens=871, output_tokens=109, requests=2, tool_calls=1)
```

**Tabela comparativa nuvem vs. local:**

| Métrica | GLM-5.2 (nuvem) | Nemotron 4B (local/CPU) |
|---|---|---|
| `tool_calls` | 1 ✓ | 1 ✓ |
| `requests` | 2 | 2 |
| `input_tokens` | 546 (+419 de cache) | 871 (sem cache no Ollama) |
| `output_tokens` | 131 | 109 |
| Custo | centavos (USD) | R$ 0,00 |
| Localização dos dados | nuvem exterior | máquina local |

**Observações técnicas:**
- `requests=2` expõe a anatomia do tool calling: 1ª requisição decide chamar a ferramenta, 2ª formula a resposta com o resultado.
- Os campos do `RunUsage` variam por provedor: OpenRouter expõe `cache_read_tokens` e `reasoning_tokens`, Ollama não. Insight relevante para observabilidade multi-provedor.
- O "offline" vale para o **cérebro (LLM)**; a ferramenta Open-Meteo ainda usa internet. Teste 100% offline com tool local fica como experimento futuro.

---

#### Parte D — Bugs e lições do dia

1. **Lição conceitual central:** "modelo ≠ agente — inteligência é o cérebro, ferramentas são as mãos." Descoberta na prática: comandos de shell foram digitados por engano dentro do chat do `ollama run` e o modelo respondeu corretamente que não executa nada. A frustração inicial ("queria um agente mais inteligente") diagnosticava errado — faltavam ferramentas, não inteligência. O `weather_agent` provou isso: mesmo modelo, com tool, executa.
2. **Bug de ambiente:** `ModuleNotFoundError: pydantic_ai` — `venv` não estava ativado. Agravante: o venv se chama `venv` (sem ponto) e a primeira tentativa de ativação usou `.venv` (com ponto). Fix: `source ../venv/bin/activate`.
3. **Bug de caminho:** o repositório fica em pasta com espaços no nome (`Documentos/Kali Linux/Multi-Agentes/`), exigindo aspas em todos os comandos de shell. Anotado como melhoria futura: mover para caminho sem espaços.
4. **Pegadinha de registry do Ollama:** `ollama pull nemotron-nano` falha (file does not exist); nome correto é `nemotron-3-nano:4b`, e a tag default puxaria 24 GB.

---

#### Status geral atualizado

- ✅ Dia 1 — Hello world Pydantic AI (FECHADO)
- ✅ Dia 2 — `weather_agent.py` com tool use dual-backend (FECHADO)
- ⏳ Dia 3 — `secure_agent.py` com Human-in-the-Loop tool approval
- ⏳ Dia 4 — Análise comparativa + repetição estatística do experimento de tokens
- ⏳ Dia 5 — Rascunho do post LinkedIn

**Commit Dia 2:** `5013d0a`

---

### Dia 3 — `secure_agent.py` — Human-in-the-Loop

**O que foi feito:**
Implementado o `secure_agent.py`, demonstrando o padrão de "Human-in-the-Loop" para controle de segurança em agentes de IA.

**Detalhes da implementação:**
- **Ferramentas seguras:** `listar_arquivos` e `ler_arquivo`. Executam diretamente sem interrupções.
- **Ferramentas sensíveis:** `criar_arquivo` e `apagar_arquivo`. Pausam a execução e pedem aprovação via `input()` no terminal antes de prosseguir.

**Testes realizados:**
1. Ação segura (`listar_arquivos`): Executou diretamente com sucesso sem pedir aprovação.
2. Ação sensível APROVADA: Pedido para criar arquivo (`criar_arquivo`). O agente pausou, pediu aprovação. O usuário digitou "s". O arquivo foi criado com sucesso.
3. Ação sensível NEGADA: Pedido para apagar arquivo (`apagar_arquivo`). O agente pausou. O usuário digitou "n". A recusa foi respeitada pelo agente, e o arquivo **não** foi apagado. Isso confirma que o controle humano funciona efetivamente como um guardrail.

**Status geral atualizado:**

- ✅ Dia 1 — Hello world Pydantic AI (FECHADO)
- ✅ Dia 2 — `weather_agent.py` com tool use dual-backend (FECHADO)
- ✅ Dia 3 — `secure_agent.py` com Human-in-the-Loop tool approval (FECHADO)
- ⏳ Dia 4 — Análise comparativa + repetição estatística do experimento de tokens
- ⏳ Dia 5 — Rascunho do post LinkedIn

**Commit Dia 3:** `f34b87f`
