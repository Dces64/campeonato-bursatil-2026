import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Campeonato Bursátil 2026", layout="wide")

# --- 1. CONFIGURACIÓN DE RONDAS Y FECHAS ---
# Aquí definimos cuándo empieza y termina cada mes oficialmente
RONDAS = {
    "Ronda 1 (Feb/Mar)": {"inicio": "2026-02-17", "fin": "2026-03-31"},
    "Ronda 2 (Abril)": {"inicio": "2026-04-01", "fin": "2026-04-30"},
}

TICKERS = [
    "MSFT", "NVDA", "GOOGL", "META", "TSM", "V", "BRK-B", "JPM", "ASML", "INTC", 
    "AMD", "COST", "WMT", "PG", "GE", "DE", "RTX", "JNJ", "UNH", "LLY", 
    "AMZN", "TSLA", "KO", "AAPL", "AVGO", "SPY", "QQQ", "VTI", "ACWI", "XLE", 
    "GLD", "IBIT", "ARKK", "COPX"
]

# --- 2. PREDICCIONES POR RONDA (Base de Datos) ---
# Aquí iremos agregando los bloques de cada mes.
DATOS_IA = {
    "GPT FRICAS": {
        "Ronda 1": {"estrella": "XLE", "top15": ["NVDA", "META", "TSM", "ASML", "MSFT", "AMZN", "GOOGL", "LLY", "COST", "V", "QQQ", "GE", "DE", "SPY", "XLE"]},
        "Anual": ["NVDA", "AMZN", "MSFT", "GOOGL", "META", "TSM", "LLY", "AVGO", "COST", "GE", "XLE", "IBIT"]
    },
    "GEMI AG": {
        "Ronda 1": {"estrella": "NVDA", "top15": ["NVDA", "MSFT", "TSM", "LLY", "COPX", "AMZN", "META", "ASML", "GOOGL", "AMD", "JPM", "GE", "SPY", "QQQ", "VTI"]},
        "Anual": ["NVDA", "COPX", "LLY", "GLD", "JPM", "AVGO", "TSM", "MSFT", "GOOGL", "META", "AMZN", "V"]
    },
    "CLAUDE ANALISTA": {
        "Ronda 1": {"estrella": "DE", "top15": ["DE", "NVDA", "LLY", "GE", "AMD", "META", "TSM", "GOOGL", "AMZN", "ASML", "MSFT", "RTX", "JPM", "COST", "V"]},
        "Anual": ["NVDA", "LLY", "TSM", "AMZN", "META", "ASML", "MSFT", "GOOGL", "AVGO", "GE", "DE", "V"]
    }
}

# --- 3. MOTOR DE CÁLCULO ---
@st.cache_data
def traer_datos(inicio, fin):
    data = yf.download(TICKERS, start=inicio, end=fin, auto_adjust=True)['Close']
    res = []
    for t in TICKERS:
        try:
            v_ini = data[t].dropna().iloc[0]
            v_fin = data[t].dropna().iloc[-1]
            var = ((v_fin / v_ini) - 1) * 100
            res.append({"Ticker": t, "Variacion": var})
        except: pass
    df = pd.DataFrame(res).sort_values("Variacion", ascending=False).reset_index(drop=True)
    df.index += 1
    return df

# --- 4. INTERFAZ ---
st.title("🏆 Gran Campeonato Bursátil 2026")

tab1, tab2 = st.tabs(["📊 Ranking Acumulado", "📅 Detalle por Ronda"])

with tab2:
    st.header("Análisis Mensual")
    ronda_sel = st.selectbox("Selecciona la Ronda a visualizar:", list(RONDAS.keys()))
    
    # Calculamos datos de la ronda seleccionada
    df_mkt = traer_datos(RONDAS[ronda_sel]["inicio"], RONDAS[ronda_sel]["fin"])
    ranking_mkt = df_mkt["Ticker"].tolist()
    
    # Calculamos puntos de la ronda
    resultados_ronda = []
    for nombre, predicciones in DATOS_IA.items():
        if "Ronda 1" in predicciones: # Por ahora solo evaluamos R1
            puntos = 0
            # Regla 1 (Top 15)
            aciertos = len(set(predicciones["Ronda 1"]["top15"]) & set(ranking_mkt[:15]))
            puntos += aciertos * 10
            # Regla 4 (Estrella)
            pos_est = ranking_mkt.index(predicciones["Ronda 1"]["estrella"]) + 1
            pts_est = 40 if pos_est == 1 else 20 if pos_est <= 3 else -40 if pos_est >= 25 else 0
            puntos += pts_est
            
            resultados_ronda.append({"IA": nombre, "Puntos Ronda": puntos, "Aciertos T15": aciertos, "Pos. Estrella": pos_est})

    res_df = pd.DataFrame(resultados_ronda).sort_values("Puntos Ronda", ascending=False)
    st.table(res_df)

with tab1:
    st.header("🏆 Clasificación General del Año")
    # Aquí sumaremos los puntos de todas las rondas
    # Por ahora simulamos el acumulado con la Ronda 1
    st.bar_chart(res_df.set_index("IA")["Puntos Ronda"])
    st.write("Esta tabla sumará automáticamente los puntos de cada mes a medida que los completemos.")
