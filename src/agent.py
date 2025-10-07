#imports
import sys
import os
from pathlib import Path
from datetime import datetime
from phi.agent import Agent
from phi.model.groq import Groq
import re
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from phi.tools.duckduckgo import DuckDuckGo
from dotenv import load_dotenv
from PIL import Image

# Ajusta o path para importar módulos de níveis superiores
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Projetos internos
from src.etl import ETL
from src.metrics import METRICS
from src.viz import VIZ

# Carrega o arquivo de variáveis de ambiente
load_dotenv()

# --- Configuração ---
OUTPUT_DIR = Path(__file__).parent.parent / "reports"
OUTPUT_DIR.mkdir(exist_ok=True)

# --- Inicializa modelo Groq (gpt-oss) ---
llm = Groq(
    id="openai/gpt-oss-20b",
    api_key=os.environ.get("GROQ_TOKEN")
)

#estancia o ETL e extrai os dados mais recentes
etl=ETL().extract_api_latest()

# --- Funções utilitárias ---

#passa base de dados e extrai as metricas
def tool_metrics() -> dict:
    df = etl
    growth = METRICS.growth_rate(df)
    mortality = METRICS.mortality_rate(df)
    uti = METRICS.uti_rate(df)
    vacc = METRICS.vaccination_rate(df)
    
    return (
        f"- Taxa de crescimento em relação à última semana: {growth:.2f}%\n"
        f"- Taxa de mortalidade no último mês: {mortality:.2f}%\n"
        f"- Ocupação de UTI no último mês: {uti:.2f}%\n"
        f"- Taxa de vacinação no último mês: {vacc:.2f}%\n"
    )

#extrai series diaria a mensal e plota os graficos
def tool_charts() -> dict:
    df = etl
    charts = VIZ(output_dir=OUTPUT_DIR)
    daily_path = charts.plot_daily_cases(df)
    monthly_path = charts.plot_monthly_cases(df)
    
    return  daily_path, monthly_path

agent_search = Agent(name="SearchAgent",
                              role="Buscar dados e noticias atualizadas sobre Síndrome Respiratória Aguda Grave (SRAG)",
                              model=llm,
                              tools=[DuckDuckGo()],
                              instructions=["Forneça apenas resumo e noticias principais, sempre inclua as fontes."],
                              show_tool_calls=True, markdown=True)

# --- Execução direta ---
if __name__ == "__main__":

    ########## App Web ##########

    # Configuração da página do Streamlit
    st.set_page_config(page_title="Agente de saúde", page_icon="⚕️", layout="wide")

    # Título principal
    st.title("Agente de Saúde com foco em SRAG ⚕️")

    # Interface principal
    st.header("Atualização Epidemiológica em Tempo Real sobre Síndrome Respiratória Aguda Grave (SRAG)")

    # Se o usuário pressionar o botão, entramos neste bloco
    if st.button("Gerar Relatório"):

        # Inicia o processamento
        with st.spinner("Buscando os Dados em Tempo Real. Aguarde..."):
            
            # Renderiza um subtítulo
            st.subheader("Análise Gerada Por IA")
            
            # Executa o Agente de IA

            ai_response = agent_search.run(f"Gerar relatório atualizado sobre Síndrome Respiratória Aguda Grave (SRAG) com métricas e notícias recentes")

            # Remove linhas que começam com "Running:"
            # Remove o bloco "Running:" e também linhas "transfer_task_to_finance_ai_agent"
            clean_response = re.sub(r"(Running:[\s\S]*?\n\n)|(^transfer_task_to_finance_ai_agent.*\n?)","", ai_response.content, flags=re.MULTILINE).strip()

            # Imprime a resposta
            st.markdown(clean_response)

            # Imprime as metricas extraidas da API
            st.subheader("Métricas Principais da Base de Dados do OpenDataSUS (Atualizada Diariamente)")

            metrics=tool_metrics()

            st.markdown(metrics)

            # Renderiza os gráficos
            st.subheader("Visualização dos Dados, histórico dos Últimos 30 Dias e 12 Meses")
            daily_path, monthly_path = tool_charts()
            image1 = Image.open(daily_path)
            image2 = Image.open(monthly_path)
            st.image(image1, caption="Gráfico diário dos últimos 30 dias", use_column_width=True)
            st.image(image2, caption="Gráfico mensal dos últimos 12 meses", use_column_width=True)
    