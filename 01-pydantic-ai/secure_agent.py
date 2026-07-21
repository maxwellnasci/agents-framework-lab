"""
Dia 3 - secure_agent.py
Agente com Human-in-the-Loop: ferramentas sensiveis exigem aprovacao humana.
Uso:
  python secure_agent.py "liste os arquivos da pasta atual"
  python secure_agent.py "crie um arquivo teste.txt com o conteudo 'ola'"
  AGENT_BACKEND=local python secure_agent.py "apague o arquivo teste.txt"
"""
import os
import sys
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from pydantic_ai.providers.openai import OpenAIProvider

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BACKEND = os.getenv("AGENT_BACKEND", "openrouter")

if BACKEND == "local":
    model = OpenAIChatModel(
        "nemotron-3-nano:4b",
        provider=OpenAIProvider(base_url="http://localhost:11434/v1", api_key="ollama"),
    )
else:
    model = OpenAIChatModel(
        os.getenv("MODEL_GLM", "z-ai/glm-5.2"),
        provider=OpenRouterProvider(api_key=os.environ["OPENROUTER_API_KEY"]),
    )

agent = Agent(
    model,
    system_prompt=(
        "Voce e um assistente de arquivos. Use as ferramentas disponiveis "
        "para cumprir o pedido do usuario. Responda em portugues, curto."
    ),
    model_settings={"max_tokens": 2048},
)

def pedir_aprovacao(acao: str) -> bool:
    """Pausa o agente e pede confirmacao humana antes de uma acao sensivel."""
    print(f"\n⚠️  AÇÃO SENSÍVEL PROPOSTA: {acao}")
    resposta = input("Aprovar? (s/n): ").strip().lower()
    return resposta == "s"

@agent.tool_plain
def listar_arquivos(pasta: str = ".") -> list[str]:
    """Lista os arquivos de uma pasta. Acao segura, nao precisa de aprovacao."""
    try:
        return os.listdir(pasta)
    except Exception as e:
        return [f"erro: {e}"]

@agent.tool_plain
def ler_arquivo(caminho: str) -> str:
    """Le o conteudo de um arquivo de texto. Acao segura, nao precisa de aprovacao."""
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return f.read()[:2000]
    except Exception as e:
        return f"erro: {e}"

@agent.tool_plain
def criar_arquivo(caminho: str, conteudo: str) -> str:
    """Cria ou sobrescreve um arquivo com o conteudo dado. Acao SENSIVEL, exige aprovacao humana."""
    acao = f"criar/sobrescrever o arquivo '{caminho}' com conteudo: {conteudo[:100]!r}"
    if not pedir_aprovacao(acao):
        return "Ação NEGADA pelo usuário. Arquivo não foi criado."
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo)
    return f"Arquivo '{caminho}' criado com sucesso (aprovado pelo usuário)."

@agent.tool_plain
def apagar_arquivo(caminho: str) -> str:
    """Apaga um arquivo do disco. Acao SENSIVEL, exige aprovacao humana."""
    acao = f"APAGAR permanentemente o arquivo '{caminho}'"
    if not pedir_aprovacao(acao):
        return "Ação NEGADA pelo usuário. Arquivo não foi apagado."
    try:
        os.remove(caminho)
        return f"Arquivo '{caminho}' apagado (aprovado pelo usuário)."
    except Exception as e:
        return f"erro ao apagar: {e}"

if __name__ == "__main__":
    pergunta = " ".join(sys.argv[1:]) or "Liste os arquivos da pasta atual."
    result = agent.run_sync(pergunta)
    print("\n--- resposta ---")
    print(result.output)
    print("\n--- usage ---")
    print(result.usage)
