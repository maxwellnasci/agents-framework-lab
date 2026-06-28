# 🧪 agents-framework-lab

> Lab público: 4 frameworks IA × 2 LLMs pela lente da **cibersegurança aplicada a agentes autônomos**.

**Status:** 🚧 Em construção (Semana 1 — Pydantic AI)
**Autor:** Maxwell do Nascimento ([@maxwellnasci](https://github.com/maxwellnasci))
**Início:** Junho 2026

---

## 🎯 Tese

A discussão sobre agentes IA no Brasil hoje gira em torno de 3 modelos americanos (GPT, Claude, Gemini) e 1 framework (LangChain). Isso cria 3 problemas:

1. **Soberania de dados**: empresas BR sob LGPD não podem mandar dados sensíveis pra APIs proprietárias americanas
2. **Dependência de vendor**: stack inteiro travado em um ecossistema de um país
3. **Pensamento de manada**: a maioria dos devs IA BR só conhece um framework

Este lab compara **4 frameworks** rodando com **2 LLMs de filosofias opostas** (open-weights soberano vs. proprietário Anthropic), documentando trade-offs reais com foco em cibersegurança.

## 🏗️ Stack

| Framework | LLM | Pasta | Status |
|---|---|---|---|
| Pydantic AI | GLM-5.2 (Z.ai) | `01-pydantic-ai/` | 🚧 Semana 1 |
| LangChain | GLM-5.2 (Z.ai) | `02-langchain/` | ⏳ Semana 2 |
| LangGraph | GLM-5.2 (Z.ai) | `03-langgraph/` | ⏳ Semana 3 |
| Claude Agent SDK | Claude Haiku 4.5 | `04-claude-agent-sdk/` | ⏳ Semana 4 |

**Por que essas escolhas:**

- **GLM-5.2 (Z.ai)**: open-weights sob licença MIT, 754B parâmetros MoE (40B ativos), contexto 1M tokens. Pode rodar on-prem = história de soberania LGPD viável.
- **Claude Haiku 4.5**: proprietário Anthropic mas tier econômico (~$1/$5 por 1M tokens). Realista pra PME brasileira.
- **Acesso unificado**: ambos via OpenRouter (API OpenAI-compatible).

## 📋 Metodologia

Para cada framework, **o mesmo caso de uso**:
> "Agente que responde dúvidas sobre clima usando ferramenta de busca em API real."

Cada framework é avaliado em:

- Tempo de instalação + curva de aprendizado
- Linhas de código pro mesmo agente
- Suporte a tool use / function calling
- Observabilidade e debug
- Postura de segurança (sandboxing, validação de inputs, logging)
- Custo por execução (real, medido via OpenRouter)
- Latência média

Comparação final: framework × LLM × **MXOS OpenClaw** (referência de produção do autor, em outro repositório).

## 📂 Estrutura
agents-framework-lab/

├── 01-pydantic-ai/          # Semana 1

├── 02-langchain/            # Semana 2

├── 03-langgraph/            # Semana 3

├── 04-claude-agent-sdk/     # Semana 4

├── shared/                  # Código compartilhado (chamadas OpenRouter, base do agente)

├── docs/                    # Documentação técnica

│   └── posts/               # Rascunhos LinkedIn / Medium

├── .env.example

├── .gitignore

├── LICENSE

└── README.md

## 🔒 Postura de segurança

Sendo um projeto sob ângulo de cibersegurança, práticas obrigatórias:

- ❌ **Nunca** commitar `.env`, chaves de API, ou dados de cliente real (protegido via `.gitignore`)
- ✅ Usar `.env.example` como template público
- ✅ Validar inputs antes de passar pra LLMs (prevenção de prompt injection)
- ✅ Logar tool calls separadamente do conteúdo das mensagens
- ✅ Documentar cada decisão de segurança em `docs/`

## 🚀 Como rodar (em construção)

```bash
git clone https://github.com/maxwellnasci/agents-framework-lab.git
cd agents-framework-lab
cp .env.example .env
# Edita .env com sua chave OpenRouter
# Entra na pasta do framework desejado
```

Instruções específicas em cada subpasta de framework conforme forem publicadas.

## 📚 Roadmap

- [ ] **Semana 1**: Pydantic AI + GLM-5.2
- [ ] **Semana 2**: LangChain + GLM-5.2
- [ ] **Semana 3**: LangGraph + GLM-5.2
- [ ] **Semana 4**: Claude Agent SDK + Claude Haiku 4.5
- [ ] **Semana 5**: Matriz comparativa final + post longo no Medium
- [ ] **Fase 2 (futura)**: Expansão com Kimi K2.6 ou outro LLM open-weights

## 🤝 Sobre o autor

Maxwell do Nascimento — consultor em IA e automação, fundador da MXOS (funcionários digitais pra PMEs), estudante de Cibersegurança (Uninter 2026-2028). Curitiba/BR.

Outros projetos: [meu-agente](https://github.com/maxwellnasci/meu-agente) (agente em produção com 9 camadas de segurança defense-in-depth).

## 📜 Licença

MIT — veja [LICENSE](./LICENSE).
