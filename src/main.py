import os
from pathlib import Path
from datetime import datetime
import json

from langchain import OpenAI
from langchain.agents import Tool, initialize_agent

from src.etl import etl
from src.metrics import METRICS
from src.viz import Charts
from src.news import fetch_news
from src.rag import index_latest_news, retrieve

# --- Configuração ---
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
OUTPUT_DIR = Path(__file__).parent.parent / "reports"
AUDIT_DIR = Path(__file__).parent.parent / "audit"
OUTPUT_DIR.mkdir(exist_ok=True)
AUDIT_DIR.mkdir(exist_ok=True)

# --- Inicializa LLM ---
llm = OpenAI(temperature=0.0, model_name=OPENAI_MODEL)

# --- Funções utilitárias para as tools ---
def tool_load_data(_input: str = "") -> str:
    """
    Carrega parquet ou roda ETL se não existir
    """
    etl_instance = etl()
    df = etl_instance.extract_api_latest()
    return f"DataFrame carregado com {len(df)} linhas e colunas: {list(df.columns)}"

def tool_metrics(_input: str = "") -> dict:
    df = etl().extract_api_latest()
    return {
        "growth_rate": METRICS.growth_rate(df),
        "mortality_rate": METRICS.mortality_rate(df),
        "uti_rate": METRICS.uti_rate(df),
        "vaccination_rate": METRICS.vaccination_rate(df)
    }

def tool_daily_series(_input: str = "") -> dict:
    df = etl().extract_api_latest()
    return METRICS.daily_cases(df).to_dict()

def tool_monthly_series(_input: str = "") -> dict:
    df = etl().extract_api_latest()
    return METRICS.monthly_cases(df).to_dict()

def tool_charts(_input: str = "") -> dict:
    df = etl().extract_api_latest()
    charts = Charts(output_dir=OUTPUT_DIR)
    daily_path = charts.plot_daily_cases(df)
    monthly_path = charts.plot_monthly_cases(df)
    return {"daily": str(daily_path), "monthly": str(monthly_path)}

def tool_fetch_news(query: str = "SRAG") -> list:
    articles = fetch_news(query=query, days=7)
    return articles

def tool_rag(query: str) -> list:
    return retrieve(query=query, k=5)

def log_audit(event: str, metadata: dict):
    """
    Salva log em audit_log.jsonl
    """
    metadata['event'] = event
    metadata['timestamp'] = datetime.utcnow().isoformat()
    path = AUDIT_DIR / "audit_log.jsonl"
    with open(path, "a") as f:
        f.write(json.dumps(metadata, default=str) + "\n")

# --- Define LangChain Tools ---
tools = [
    Tool(name="load_data", func=tool_load_data, description="Carrega os dados tratados."),
    Tool(name="metrics", func=tool_metrics, description="Retorna métricas chave do dataset."),
    Tool(name="daily_series", func=tool_daily_series, description="Retorna série diária de casos."),
    Tool(name="monthly_series", func=tool_monthly_series, description="Retorna série mensal de casos."),
    Tool(name="charts", func=tool_charts, description="Gera gráficos e retorna paths."),
    Tool(name="fetch_news", func=tool_fetch_news, description="Busca notícias recentes."),
    Tool(name="rag", func=tool_rag, description="Retorna snippets relevantes das notícias indexadas."),
]

# --- Inicializa agente zero-shot ---
agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)

# --- Função principal ---
def run_report(query: str = "SRAG") -> str:
    log_audit("start_run", {"query": query})
    
    # Atualiza RAG com notícias recentes
    n_articles = index_latest_news(days=7)
    log_audit("rag_index", {"n_articles": n_articles})
    
    prompt = (
        "Gere um relatório baseado nas ferramentas disponíveis. "
        "Inclua: métricas (growth, mortality, uti, vaccination), "
        "séries diárias e mensais, gráficos gerados, "
        "resumo das notícias mais relevantes e interpretação do cenário atual."
    )
    
    result = agent.run(prompt)
    log_audit("end_run", {"result_excerpt": result[:500]})
    
    # Salva relatório em arquivo
    report_path = OUTPUT_DIR / f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(result)
    
    print("Relatório salvo em:", report_path)
    return str(report_path)

# --- Execução direta ---
if __name__ == "__main__":
    run_report()