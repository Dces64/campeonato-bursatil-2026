
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

# --- 2. ENTRADA DE DATOS DE LAS IA (Cargados desde tu análisis) ---
PREDICCIONES = {
    "GPT FRICAS": {
        "pick_estrella": "XLE",
        "top_15": ["NVDA", "META", "TSM", "ASML", "MSFT", "AMZN", "GOOGL", "LLY", "COST", "V", "QQQ", "GE", "DE", "SPY", "XLE"],
        "top_3_ganadoras": ["XLE", "RTX", "GLD"],
        "top_3_perdedoras": ["ARKK", "TSLA", "INTC"]
    },
    "GPT WARREN": {
        "pick_estrella": "NVDA",
        "top_15": ["NVDA", "TSM", "ASML", "AMZN", "GOOGL", "WMT", "COST", "LLY", "RTX", "GE", "DE", "PG", "KO", "V", "BRK-B"],
        "top_3_ganadoras": ["NVDA", "TSM", "ASML"],
        "top_3_perdedoras": ["ARKK", "TSLA", "INTC"]
    },
    "GPT AG": {
        "pick_estrella": "INTC",
        "top_15": ["INTC", "ASML", "TSM", "COPX", "WMT", "JNJ", "PG", "COST", "RTX", "META", "KO", "ACWI", "QQQ", "BRK-B", "VTI"],
        "top_3_ganadoras": ["INTC", "ASML", "TSM"],
        "top_3_perdedoras": ["AMZN", "UNH", "MSFT"]
    },
    "GEMI AG": {
        "pick_estrella": "NVDA",
        "top_15": ["NVDA", "MSFT", "TSM", "LLY", "COPX", "AMZN", "META", "ASML", "GOOGL", "AMD", "JPM", "GE", "SPY", "QQQ", "VTI"],
        "top_3_ganadoras": ["NVDA", "MSFT", "TSM"],
        "top_3_perdedoras": ["IBIT", "ARKK", "INTC"]
    },
    "GEMI FRICAS": {
        "pick_estrella": "NVDA",
        "top_15": ["NVDA", "LLY", "AVGO", "TSM", "AMD", "META", "ASML", "MSFT", "GOOGL", "AMZN", "GE", "RTX", "COST", "V", "JPM"],
        "top_3_ganadoras": ["NVDA", "LLY", "AVGO"],
        "top_3_perdedoras": ["INTC", "TSLA", "DE"]
    },
    "GEMI WARREN": {
        "pick_estrella": "BRK-B",
        "top_15": ["BRK-B", "JPM", "V", "PG", "KO", "WMT", "COST", "JNJ", "UNH", "LLY", "AAPL", "MSFT", "GOOGL", "SPY", "VTI"],
        "top_3_ganadoras": ["BRK-B", "JPM", "V"],
        "top_3_perdedoras": ["ARKK", "IBIT", "NVDA"]
    },
    "CLAUDE ANALISTA": {
        "pick_estrella": "DE",
        "top_15": ["DE", "NVDA", "LLY", "GE", "AMD", "META", "TSM", "GOOGL", "AMZN", "ASML", "MSFT", "RTX", "JPM", "COST", "V"],
        "top_3_ganadoras": ["DE", "NVDA", "LLY"],
        "top_3_perdedoras": ["TSLA", "INTC", "IBIT"]
    },
    "CLAUDE FRICAS": {
        "pick_estrella": "ASML",
        "top_15": ["ASML", "TSM", "NVDA", "AVGO", "AMD", "MSFT", "META", "GOOGL", "AMZN", "LLY", "GE", "RTX", "COPX", "QQQ", "XLE"],
        "top_3_ganadoras": ["ASML", "TSM", "NVDA"],
        "top_3_perdedoras": ["PG", "KO", "JNJ"]
    },
    "CLAUDE WARREN": {
        "pick_estrella": "JPM",
        "top_15": ["JPM", "V", "BRK-B", "COST", "WMT", "PG", "KO", "JNJ", "UNH", "LLY", "AAPL", "MSFT", "GOOGL", "SPY", "ACWI"],
        "top_3_ganadoras": ["JPM", "V", "BRK-B"],
        "top_3_perdedoras": ["ARKK", "TSLA", "COPX"]
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

    # --- DASHBOARD VISUAL ---
    res_df = pd.DataFrame(st.session_state.resultados).sort_values("Puntos", ascending=False)
    
    st.subheader("🔥 Ranking de Competidores")
    # Gráfico de barras interactivo
    st.bar_chart(data=res_df, x="Competidor", y="Puntos", color="Competidor")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.write("### 📋 Tabla de Posiciones")
        st.dataframe(res_df.set_index("Competidor"), use_container_width=True)
    
    with col_t2:
        st.write("### 📈 Mercado (Top 5 del Mes)")
        st.table(df_mercado.head(5))

    st.balloons() # ¡Festejo automático cuando termina el cálculo!
