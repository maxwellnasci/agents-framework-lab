"""
Dia 2 - weather_agent.py
Tool use com Pydantic AI + Open-Meteo (sem API key).
Backends: GLM-5.2 via OpenRouter (padrao) ou Nemotron via Ollama (local).
Uso:
  python weather_agent.py "Qual o clima em Curitiba?"
  AGENT_BACKEND=local python weather_agent.py "Qual o clima em Curitiba?"
"""
import os
import sys
import requests
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
        "Voce e um assistente de clima. SEMPRE use a ferramenta get_weather "
        "para obter dados reais antes de responder. Responda em portugues, curto."
    ),
    model_settings={"max_tokens": 2048},
)

@agent.tool_plain
def get_weather(city: str) -> dict:
    """Retorna o clima atual de uma cidade: temperatura (C), vento (km/h), umidade (%)."""
    geo = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1, "language": "pt"},
        timeout=10,
    ).json()
    if not geo.get("results"):
        return {"erro": f"cidade '{city}' nao encontrada"}
    place = geo["results"][0]
    clima = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "current": "temperature_2m,wind_speed_10m,relative_humidity_2m",
        },
        timeout=10,
    ).json()
    return {"cidade": place["name"], "pais": place.get("country"), **clima.get("current", {})}

if __name__ == "__main__":
    pergunta = " ".join(sys.argv[1:]) or "Qual o clima agora em Curitiba?"
    result = agent.run_sync(pergunta)
    print(result.output)
    print("\n--- usage ---")
    print(result.usage)
