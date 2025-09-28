import pandas as pd

class etl():
    def __init__(self):
        pass

    def extract(self):
        self.df_25 = pd.read_csv('/Users/williamdumaszak/Downloads/INFLUD19-26-06-2025.csv', sep=';')

if __name__ == "__main__":
    etl_instance = etl()
    etl_instance.extract()