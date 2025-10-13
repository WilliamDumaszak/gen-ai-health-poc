#import
import pandas as pd
import requests
from datetime import datetime, timedelta

class ETL:
    #responsável por buscar os dados referentes aos casos na API do opendatasus
    def __init__(self):
        self.columns=('NU_NOTIFIC','DT_NOTIFIC','EVOLUCAO','UTI','VACINA_COV')
        self.today = datetime.now()

    def extract_api_latest(self) -> pd.DataFrame:

        df_salvo= pd.read_parquet("data/processed/srag_clean.parquet", engine="pyarrow")
        df_salvo["DT_NOTIFIC"] = pd.to_datetime(df_salvo["DT_NOTIFIC"], errors="coerce")
        if (df_salvo["DT_NOTIFIC"].dt.strftime("%Y-%m-%d") == (self.today - timedelta(days=1)).strftime("%Y-%m-%d")).any():
            return df_salvo
        else:
            base_url = "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG/2025/INFLUD25-{date}.csv"
            
            # testa os últimos 30 dias
            for i in range(30):
                dt = self.today - timedelta(days=i)
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

                    df_filter = pd.concat([df_salvo, df_filter], ignore_index=True).drop_duplicates(subset=self.columns)
                    df_filter.drop_duplicates(inplace=True)
                    df_filter["DT_NOTIFIC"] = pd.to_datetime(df_filter["DT_NOTIFIC"], errors="coerce")
                    df_filter.to_parquet("data/processed/srag_clean.parquet", engine="pyarrow", index=False)
                    df_final=df_filter
                    return df_final
        