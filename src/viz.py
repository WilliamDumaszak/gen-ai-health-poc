import matplotlib.pyplot as plt
from pathlib import Path
from src.metrics import METRICS

class VIZ:
    def __init__(self, output_dir: str = "outputs"):
        """
        output_dir: pasta onde os gráficos serão salvos.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_daily_cases(self, df):
        """
        Gera e salva o gráfico diário dos últimos 30 dias.
        """
        daily = METRICS.daily_cases(df)
        plt.figure(figsize=(10, 5))
        plt.plot(daily.index, daily.values, marker="o", linewidth=2)
        plt.title("Casos diários - últimos 30 dias")
        plt.xlabel("Data")
        plt.ylabel("Número de casos")
        plt.xticks(rotation=45)
        plt.tight_layout()

        file_path = self.output_dir / "daily_cases_last_30_days.png"
        plt.savefig(file_path)
        plt.close()
        return file_path

    def plot_monthly_cases(self, df):
        """
        Gera e salva o gráfico mensal dos últimos 12 meses.
        """
        monthly = METRICS.monthly_cases(df)
        plt.figure(figsize=(10, 5))
        plt.bar(monthly.index.strftime("%Y-%m"), monthly.values)
        plt.title("Casos mensais - últimos 12 meses")
        plt.xlabel("Mês")
        plt.ylabel("Número de casos")
        plt.xticks(rotation=45)
        plt.tight_layout()

        file_path = self.output_dir / "monthly_cases_last_12_months.png"
        plt.savefig(file_path)
        plt.close()
        return file_path