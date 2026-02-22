
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Tablero Campeonato 2026", layout="wide")

# --- 1. BASE DE DATOS DE TICKERS ---
TICKERS = [
    "MSFT", "NVDA", "GOOGL", "META", "TSM", "V", "BRK-B", "JPM", "ASML", "INTC", 
    "AMD", "COST", "WMT", "PG", "GE", "DE", "RTX", "JNJ", "UNH", "LLY", 
    "AMZN", "TSLA", "KO", "AAPL", "AVGO", "SPY", "QQQ", "VTI", "ACWI", "XLE", 
    "GLD", "IBIT", "ARKK", "COPX"
]

# --- 2. ENTRADA DE DATOS DE LAS IA (Aquí es donde pegarás las respuestas) ---
# He cargado un ejemplo basado en tus archivos para que veas la magia
PREDICCIONES = {
    "GPT FRICAS": {
        "pick_estrella": "XLE",
        "top_15": ["NVDA", "META", "TSM", "ASML", "MSFT", "AMZN", "GOOGL", "LLY", "COST", "V", "QQQ", "GE", "DE", "SPY", "XLE"],
        "top_3_ganadoras": ["XLE", "RTX", "GLD"],
        "top_3_perdedoras": ["ARKK", "TSLA", "INTC"]
    },
    "GEMI AG": {
        "pick_estrella": "NVDA",
        "top_15": ["NVDA", "MSFT", "TSM", "LLY", "COPX", "AMZN", "META", "ASML", "GOOGL", "AMD", "JPM", "GE", "SPY", "QQQ", "VTI"],
        "top_3_ganadoras": ["NVDA", "MSFT", "TSM"],
        "top_3_perdedoras": ["IBIT", "ARKK", "INTC"]
    }
}

# --- 3. MOTOR DE CÁLCULO ---
@st.cache_data
def obtener_datos(start, end):
    end_adj = end + timedelta(days=1)
    data = yf.download(TICKERS, start=start, end=end_adj, auto_adjust=True)['Close']
    
    res = []
    for t in TICKERS:
        try:
            val_inicio = data[t].dropna().iloc[0]
            val_fin = data[t].dropna().iloc[-1]
            var = ((val_fin / val_inicio) - 1) * 100
            res.append({"Ticker": t, "Variacion": var})
        except: pass
    
    df = pd.DataFrame(res).sort_values("Variacion", ascending=False).reset_index(drop=True)
    df.index += 1
    return df

# --- 4. INTERFAZ ---
st.title("🏆 Campeonato Bursátil 2026")
col1, col2 = st.columns([1, 3])

with col1:
    st.header("Configuración")
    fecha_inicio = st.date_input("Inicio de Ronda", datetime(2026, 2, 17))
    fecha_fin = st.date_input("Cierre de Ronda", datetime.today())
    boton = st.button("🚀 ACTUALIZAR TABLERO")

if boton:
    df_mercado = obtener_datos(fecha_inicio, fecha_fin)
    ranking_list = df_mercado["Ticker"].tolist()
    
    st.session_state.resultados = []

    for nombre, datos in PREDICCIONES.items():
        pts_total = 0
        
        # Regla 1: Top 15 (10 pts c/u si están en el top 15 real)
        top_15_real = ranking_list[:15]
        aciertos_t15 = len(set(datos["top_15"]) & set(top_15_real))
        pts_total += aciertos_t15 * 10
        
        # Regla 4: Pick Estrella
        pos_estrella = ranking_list.index(datos["pick_estrella"]) + 1
        pts_estrella = 0
        if pos_estrella == 1: pts_estrella = 40
        elif pos_estrella <= 3: pts_estrella = 20
        elif pos_estrella >= 25: pts_estrella = -40
        pts_total += pts_estrella
        
        st.session_state.resultados.append({
            "Competidor": nombre,
            "Puntos": pts_total,
            "Aciertos T15": aciertos_t15,
            "Pos. Estrella": pos_estrella
        })

    # --- DASHBOARD ---
    res_df = pd.DataFrame(st.session_state.resultados).sort_values("Puntos", ascending=False)
    
    st.subheader("🔥 Ranking en Tiempo Real")
    st.table(res_df)
    
    st.subheader("📈 Rendimiento de Tickers")
    st.bar_chart(df_mercado.set_index("Ticker")["Variacion"])
