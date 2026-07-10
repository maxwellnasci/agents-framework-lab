# Visão de Produto — Agente Local Offline-First
> Norte estratégico deste laboratório. Este documento descreve O QUE está sendo construído
> peça por peça através dos exercícios do lab. Não é escopo de curto prazo: é o destino.
> Registrado em 10/07/2026. Autor: Max (MXOS).

---

## 1. O produto em uma frase

Um **funcionário de IA instalado na máquina do usuário** — focado em segurança,
código e automações — que funciona 100% offline por padrão, sincroniza com a
nuvem quando há internet, e atende dois públicos com o mesmo motor: o
desenvolvedor (via terminal/CLI) e o trabalhador comum (via painel visual
que parece um chat normal).

## 2. Problema e público

**Dois usuários, um agente:**

| Persona | Contexto | Interface |
|---|---|---|
| **Dev / analista técnico** | Quer velocidade, scriptabilidade, integração no fluxo de trabalho | CLI no terminal |
| **Trabalhador de empresa comum** | Não sabe/não quer usar terminal; precisa fazer análises em viagem, sem internet, ou com dados que não podem sair da máquina | Painel web local (chat visual) |

**Dores que o produto resolve:**
- Profissional em viagem/campo sem internet confiável precisa de um assistente que funcione
- Empresas com dados sensíveis (LGPD, sigilo industrial, jurídico, saúde) não podem
  mandar dados para APIs de nuvem americanas
- Ferramentas de IA atuais assumem internet permanente e terminal — excluem o usuário comum
- Ninguém no mercado brasileiro entrega "IA local + interface simples + segurança auditável"

**Relação com o restante do portfólio MXOS:** este produto é o complemento
on-premises da agência de funcionários de IA (agentes em nuvem para
comércio/atendimento). Mesmo posicionamento — soberania de dados e segurança
nativa — em dois formatos: nuvem gerenciada para quem quer conveniência,
local instalado para quem tem dado sensível. Um alimenta o outro.

## 3. Princípios de arquitetura

1. **Offline-first:** tudo funciona local por padrão. Internet é upgrade, não requisito.
2. **Um motor, várias peles:** o agente é um serviço; CLI e painel são apenas clientes.
   Nunca manter duas implementações do agente.
3. **Degradação graciosa:** tarefas que exigem internet não falham — entram na fila
   e executam quando a conexão voltar. O usuário é informado com clareza.
4. **Human-in-the-Loop obrigatório:** nenhuma ação sensível (executar script, alterar
   arquivo de sistema, enviar dado para fora) sem aprovação humana explícita.
5. **Segurança auditável:** log imutável de toda ação executada. O usuário pode ver
   tudo que o agente fez, quando e por quê.
6. **Soberania de dados:** nada sai da máquina sem consentimento. Sync é opt-in e
   transparente sobre o que sobe.

## 4. Arquitetura de referência

┌─────────────────────────────────────────────────────────────┐
│  MÁQUINA DO USUÁRIO (funciona 100% offline)                 │
│                                                             │
│  ┌──────────────────┐        ┌──────────────────────────┐   │
│  │ CLI (terminal)   │        │ Painel web local          │   │
│  │ para o dev       │        │ chat em localhost:8080    │   │
│  └────────┬─────────┘        │ para o usuário comum      │   │
│           │                  └────────────┬─────────────┘   │
│           └──────────┬───────────────────┘                  │
│                      ▼                                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ MOTOR DO AGENTE (serviço local, sempre rodando)       │  │
│  │ FastAPI em localhost + orquestração (Pydantic AI →    │  │
│  │ futuramente LangGraph) + roteamento de ferramentas    │  │
│  │ + guardrails + Human-in-the-Loop                      │  │
│  └───────┬──────────────────┬──────────────────┬─────────┘  │
│          ▼                  ▼                  ▼            │
│  ┌──────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │ Ollama +     │  │ Ferramentas    │  │ Banco local    │   │
│  │ modelo local │  │ LOCAIS:        │  │ SQLite:        │   │
│  │ (cérebro,    │  │ análise de     │  │ memória do     │   │
│  │ ex: Nemotron │  │ código, scans, │  │ agente + fila  │   │
│  │ 4B, GPU/CPU) │  │ arquivos,      │  │ automações     │   │
│  │              │  │                │  │ log auditoria  │   │
│  └──────────────┘  └────────────────┘  └───────┬────────┘   │
│                                                ▼            │
│                              ┌──────────────────────────┐   │
│                              │ CAMADA DE SYNC           │   │
│                              │ detecta conectividade;   │   │
│                              │ despacha fila quando     │   │
│                              │ online                   │   │
│                              └───────────┬──────────────┘   │
└──────────────────────────────────────────┼──────────────────┘
(só quando há internet)
▼
┌──────────────────────────┐
│ NUVEM (opt-in)           │
│ backup criptografado,    │
│ atualizações de modelo/  │
│ app, tarefas que exigem  │
│ web (pesquisa, e-mail,   │
│ salvar em Drive)         │
└──────────────────────────┘


## 5. Componentes detalhados

### 5.1 Motor do agente (serviço local)
- Processo Python rodando como serviço do sistema (systemd no Linux; equivalentes
  em Windows/macOS no futuro), iniciando com a máquina.
- Expõe API REST/WebSocket em `localhost` (FastAPI). WebSocket para streaming
  de respostas no painel.
- Orquestração: começa com Pydantic AI (framework da semana 1 do lab);
  evolui para LangGraph quando precisar de grafos de estado, checkpoints
  e Human-in-the-Loop robusto (semana 3 do lab).
- Multi-backend de LLM por configuração (validado no Dia 2 do lab):
  local (Ollama) por padrão; nuvem (OpenRouter/Vertex) como opção explícita
  do usuário quando online e autorizado.

### 5.2 Cérebro local (Ollama)
- Ollama servindo modelo pequeno com bom tool calling.
- Modelo de referência validado: `nemotron-3-nano:4b` (2,8 GB, tool calling
  comprovado no lab em 09-10/07/2026, roda 100% GPU em GTX 1650 Ti 4GB a
  ~45 tok/s, ou 100% CPU em máquina sem GPU — perfil de notebook corporativo
  i5 12ª gen / 16 GB RAM).
- Lição registrada no lab: modelo pequeno sem system prompt deriva de idioma;
  o motor SEMPRE injeta system prompt com persona, idioma e contrato de
  comportamento. "O prompt é o contrato."

### 5.3 Ferramentas (as "mãos") — foco: segurança, código, automações
Categoria LOCAL (funcionam offline, são o coração do produto):
- Análise de código: linters, análise estática de segurança (ex.: bandit
  para Python, semgrep multi-linguagem — ambos rodam offline)
- Análise de arquivos e logs: parsing, busca de padrões suspeitos, hashes
- Automações aprovadas: scripts pré-cadastrados que o agente pode executar
  COM aprovação humana (renomear lotes, gerar relatórios, backups locais)
- Operações de arquivo: ler, resumir, organizar documentos locais

Categoria ONLINE (degradam graciosamente quando offline):
- Pesquisa web, consulta de CVEs atualizados
- Envio de e-mail/relatórios
- Salvar em nuvem (Drive etc.)
- Comportamento offline: tarefa entra na fila com aviso claro ao usuário
  ("sem internet agora — deixei agendado").

### 5.4 Banco local (SQLite)
- Escolha deliberada: SQLite em vez de Postgres — zero administração,
  um arquivo, embarcável, suficiente para single-user.
- Tabelas centrais: memória do agente (fatos, resumos de conversas),
  fila de sincronização (operações pendentes com timestamp e status),
  log de auditoria imutável (toda ação executada: o quê, quando, aprovada
  por quem), configurações.
- Criptografia do banco em repouso (ex.: SQLCipher) — dado sensível não
  fica em texto plano nem na máquina local.

### 5.5 Camada de sync (offline-first)
- Loop leve que verifica conectividade periodicamente.
- Quando online: despacha fila de pendências em ordem, baixa atualizações
  (modelo, regras de segurança, app), sobe backup criptografado (opt-in).
- Resolução de conflito simples no início: last-write-wins com log.
- Transparência: painel mostra "3 tarefas aguardando internet" e o que
  cada uma fará quando executar.

### 5.6 Interfaces (as "peles")
- **CLI:** comandos diretos (`agente analisa ./src`, `agente status`,
  `agente fila`). Cliente fino da API local.
- **Painel web local:** página servida pelo próprio motor em
  `localhost:8080`; abre via atalho na área de trabalho. Visual de chat
  simples (input de texto, histórico, botões de aprovar/negar ação).
  Sem build complexo no MVP: HTML + JS vanilla ou Streamlit para
  prototipagem rápida.
- Ambas as interfaces exibem o MESMO estado (fila, aprovações pendentes,
  log) porque consomem a mesma API.

### 5.7 Human-in-the-Loop (o coração cibersec do produto)
- Toda ferramenta é classificada: leitura (executa direto) vs. ação
  sensível (exige aprovação).
- Fluxo: agente propõe ação → descreve em linguagem clara o que fará →
  usuário aprova/nega no painel ou CLI → execução → registro no log
  de auditoria.
- Este mecanismo é EXATAMENTE o exercício do Dia 3 do lab
  (`secure_agent.py`) — o lab constrói a peça central do produto.

## 6. Mapa lab → produto

| Peça do produto | Onde o lab constrói |
|---|---|
| Cérebro local + dual-backend | Dia 2 ✅ (`weather_agent.py`, Ollama + Nemotron validados) |
| Human-in-the-Loop | Dia 3 (`secure_agent.py`) |
| Persona/system prompt como contrato | Lição registrada no Dia 2 (glitch de idioma) |
| Orquestração com estado e checkpoints | Semana 3 (LangGraph) |
| Comparação de frameworks p/ escolha final | Todo o lab (tese central) |
| Motor como serviço + API local | Pós-lab (fase de produto) |
| Painel web local | Pós-lab (fase de produto) |
| Camada de sync | Pós-lab (fase de produto) |

## 7. Fora de escopo (por enquanto, deliberadamente)

- Multi-usuário / multi-tenant local
- Instaladores Windows/macOS (Linux primeiro, dogfooding no Kali)
- Voz
- Marketplace de automações
- Qualquer construção antes do fim do lab e das prioridades atuais
  (ordem vigente: Arbo → faculdade → agência/produto)

## 8. Riscos técnicos conhecidos

- Modelos 4B são limitados em raciocínio longo: mitigar com ferramentas
  determinísticas fazendo o trabalho pesado e o LLM orquestrando
- Hardware do cliente varia: detectar GPU/RAM no install e escolher
  modelo/quantização adequados (lição GPU do lab em 10/07/2026:
  headers de kernel + DKMS no Linux)
- Prompt injection via arquivos analisados: conteúdo de arquivo é DADO,
  nunca instrução; sanitização e delimitação estrita no prompt
- Sync e conflitos: começar simples (last-write-wins + log), evoluir
  conforme uso real
