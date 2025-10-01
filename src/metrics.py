import pandas as pd
import numpy as np

class METRICS:

    @staticmethod
    def daily_cases(df: pd.DataFrame, days=30) -> pd.Series:
        df['DT_NOTIFIC'] = pd.to_datetime(df['DT_NOTIFIC'], errors='coerce')
        today = pd.Timestamp.now().normalize()
        start = today - pd.Timedelta(days=days)
        df_f = df[(df['DT_NOTIFIC'] >= start) & (df['DT_NOTIFIC'] <= today)]
        daily = df_f.groupby(df_f['DT_NOTIFIC'].dt.date).size().rename("cases").sort_index()
        return daily

    @staticmethod
    def monthly_cases(df: pd.DataFrame, months: int = 12) -> pd.Series:
        df['DT_NOTIFIC'] = pd.to_datetime(df['DT_NOTIFIC'], errors='coerce')
        today = pd.Timestamp.now().normalize()
        start = (today - pd.DateOffset(months=months)).replace(day=1)
        df_f = df[(df['DT_NOTIFIC'] >= start) & (df['DT_NOTIFIC'] <= today)]
        monthly = df_f.groupby(pd.Grouper(key='DT_NOTIFIC', freq='M')).size().rename("cases")
        return monthly

    @staticmethod
    def growth_rate(df: pd.DataFrame, lookback_days: int = 7) -> float:
        df['DT_NOTIFIC'] = pd.to_datetime(df['DT_NOTIFIC'], errors='coerce')
        today = pd.Timestamp.now().normalize()
        cur_start = today - pd.Timedelta(days=lookback_days)
        prev_start = cur_start - pd.Timedelta(days=lookback_days)
        cur = df[(df['DT_NOTIFIC'] >= cur_start) & (df['DT_NOTIFIC'] < today)].shape[0]
        prev = df[(df['DT_NOTIFIC'] >= prev_start) & (df['DT_NOTIFIC'] < cur_start)].shape[0]
        return (cur - prev) / prev if prev > 0 else np.nan

    @staticmethod
    def mortality_rate(df: pd.DataFrame, days: int = 30) -> float:
        df['DT_NOTIFIC'] = pd.to_datetime(df['DT_NOTIFIC'], errors='coerce')
        today = pd.Timestamp.now().normalize()
        start = today - pd.Timedelta(days=days)
        df_f = df[(df['DT_NOTIFIC'] >= start) & (df['DT_NOTIFIC'] <= today)]
        deaths = df_f['EVOLUCAO'].isin([2,3]).sum()
        cases = df_f.shape[0]
        return deaths / cases if cases > 0 else np.nan

    @staticmethod
    def uti_rate(df: pd.DataFrame, days: int = 30) -> float:
        df['DT_NOTIFIC'] = pd.to_datetime(df['DT_NOTIFIC'], errors='coerce')
        today = pd.Timestamp.now().normalize()
        start = today - pd.Timedelta(days=days)
        df_f = df[(df['DT_NOTIFIC'] >= start) & (df['DT_NOTIFIC'] <= today)]
        uti = (df_f['UTI'] == 1).sum()
        cases = df_f.shape[0]
        return uti / cases if cases > 0 else np.nan

    @staticmethod
    def vaccination_rate(df: pd.DataFrame) -> float:
        df['VACINA_COV'] = df['VACINA_COV'].fillna(2)
        vaccinated = (df['VACINA_COV'] == 1).sum()
        cases = df.shape[0]
        return vaccinated / cases if cases > 0 else np.nan