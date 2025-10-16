#imports
import sys
import os
from pathlib import Path
from langchain.tools import tool

# Ajusta o path para importar módulos de níveis superiores
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Projetos internos
from src.etl import ETL
from src.metrics import METRICS
from src.viz import VIZ

class TOOLS():
    def __init__(self):
        # --- Configuração ---
        self.OUTPUT_DIR = Path(__file__).parent.parent / "reports"

        self.etl=ETL()
        self.df=self.etl.extract_api_latest()

    #passa base de dados e extrai as metricas
    def tool_metrics(self) -> dict:
        growth = METRICS.growth_rate(self.df)
        mortality = METRICS.mortality_rate(self.df)
        uti = METRICS.uti_rate(self.df)
        vacc = METRICS.vaccination_rate(self.df)
        
        return (
            f"- Taxa de crescimento em relação à última semana: {growth:.2f}%\n"
            f"- Taxa de mortalidade no último mês: {mortality:.2f}%\n"
            f"- Ocupação de UTI no último mês: {uti:.2f}%\n"
            f"- Taxa de vacinação no último mês: {vacc:.2f}%\n"
        )

    #extrai series diaria a mensal e plota os graficos
    def tool_charts(self) -> dict:
        self.OUTPUT_DIR.mkdir(exist_ok=True)
        charts = VIZ(output_dir=self.OUTPUT_DIR)
        daily_path = charts.plot_daily_cases(self.df)
        monthly_path = charts.plot_monthly_cases(self.df)
        
        return  daily_path, monthly_path