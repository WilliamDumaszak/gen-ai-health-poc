import pandas as pd
from pathlib import Path
import requests
from datetime import datetime, timedelta

class ETL:
    #responsável por buscar os dados referentes aos casos na API do opendatasus
    def __init__(self):
        self.raw_dir = Path(__file__).parent.parent / "data" / "raw"
        self.columns=('NU_NOTIFIC','DT_NOTIFIC','EVOLUCAO','UTI','VACINA_COV')

    def extract_api_latest(self) -> pd.DataFrame:

        try:
            df_final= pd.read_parquet("data/processed/srag_clean.parquet", engine="pyarrow")
        except:
            base_url = "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG/2025/INFLUD25-{date}.csv"
            today = datetime.now()
            # testa os últimos 30 dias
            for i in range(30):
                dt = today - timedelta(days=i)
                print(dt)
                date_str = dt.strftime("%d-%m-%Y")
                url = base_url.format(date=date_str)
                r = requests.head(url)
                if r.status_code == 200:
                    df = pd.read_csv(
                        url,
                        sep=";",
                        encoding="latin1",
                        on_bad_lines="skip"
                    )
                    #filtra e deixa apenas colunas relevantes
                    df_filter = df.filter(self.columns)
                    df_filter.drop_duplicates(inplace=True)
                    print(f"Volume para a data {date_str}: {df_filter.shape}")
                    df_filter.to_parquet("data/processed/srag_clean.parquet", engine="pyarrow", index=False)
                    df_final=df_filter
        return df_final