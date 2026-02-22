import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, date, timedelta

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Tablero Oficial - Campeonato 2026", layout="wide")

# Lista oficial de 34 tickers (Yahoo usa guión para Berkshire)
TICKERS = ["MSFT", "NVDA", "GOOGL", "META", "TSM", "V", "BRK-B", "JPM", "ASML", "INTC", "AMD", "COST", "WMT", "PG", "GE", "DE", "RTX", "JNJ", "UNH", "LLY", "AMZN", "TSLA", "KO", "AAPL", "AVGO", "SPY", "QQQ", "VTI", "ACWI", "XLE", "GLD", "IBIT", "ARKK", "COPX"]

RONDAS = {
    "Ronda 1 (Feb 20 - Mar 31)": {"inicio": "2026-02-20", "fin": "2026-03-31"},
    "Ronda 2 (Abril)": {"inicio": "2026-04-01", "fin": "2026-04-30"}
}

# --- BASE DE DATOS COMPLETA DE LOS 9 COMPETIDORES ---
DATOS_IA = {
    "GPT FRICAS": {"estrella": "XLE", "top15": ["NVDA", "META", "TSM", "ASML", "MSFT", "AMZN", "GOOGL", "LLY", "COST", "V", "QQQ", "GE", "DE", "SPY", "XLE"], "top3W": ["XLE", "RTX", "GLD"], "top3L": ["ARKK", "TSLA", "INTC"], "r3": {"neutral": ["PG", "JNJ", "ACWI"], "ganancia": ["V", "BRK-B", "WMT"], "mucha_gan": ["XLE", "RTX", "NVDA"], "perdida": ["JPM", "COPX", "RTX"], "mucha_perd": ["ARKK", "TSLA", "AMD"]}},
    "GPT WARREN": {"estrella": "NVDA", "top15": ["NVDA", "TSM", "ASML", "AMZN", "GOOGL", "WMT", "COST", "LLY", "RTX", "GE", "DE", "PG", "KO", "V", "BRK-B"], "top3W": ["NVDA", "TSM", "ASML"], "top3L": ["ARKK", "TSLA", "INTC"], "r3": {"neutral": ["PG", "KO", "JPM"], "ganancia": ["V", "BRK-B", "WMT"], "mucha_gan": ["NVDA", "TSM", "ASML"], "perdida": ["INTC", "AMD", "META"], "mucha_perd": ["ARKK", "TSLA", "INTC"]}},
    "GPT AG": {"estrella": "INTC", "top15": ["INTC", "ASML", "TSM", "COPX", "WMT", "JNJ", "PG", "COST", "RTX", "META", "KO", "ACWI", "QQQ", "BRK-B", "VTI"], "top3W": ["INTC", "ASML", "TSM"], "top3L": ["AMZN", "UNH", "MSFT"], "r3": {"neutral": ["AMD", "BRK-B", "VTI"], "ganancia": ["PG", "COST", "RTX"], "mucha_gan": ["INTC", "ASML", "TSM"], "perdida": ["DE", "TSLA", "JPM"], "mucha_perd": ["AMZN", "UNH", "MSFT"]}},
    "GEMI AG": {"estrella": "NVDA", "top15": ["NVDA", "MSFT", "TSM", "LLY", "COPX", "AMZN", "META", "ASML", "GOOGL", "AMD", "JPM", "GE", "SPY", "QQQ", "VTI"], "top3W": ["NVDA", "MSFT", "TSM"], "top3L": ["IBIT", "ARKK", "INTC"], "r3": {"neutral": ["PG", "KO", "JNJ"], "ganancia": ["V", "BRK-B", "SPY"], "mucha_gan": ["NVDA", "MSFT", "COPX"], "perdida": ["WMT", "RTX", "UNH"], "mucha_perd": ["IBIT", "ARKK", "INTC"]}},
    "GEMI FRICAS": {"estrella": "NVDA", "top15": ["NVDA", "LLY", "AVGO", "TSM", "AMD", "META", "ASML", "MSFT", "GOOGL", "AMZN", "GE", "RTX", "COST", "V", "JPM"], "top3W": ["NVDA", "LLY", "AVGO"], "top3L": ["INTC", "TSLA", "DE"], "r3": {"neutral": ["PG", "KO", "JNJ"], "ganancia": ["COST", "V", "JPM"], "mucha_gan": ["NVDA", "LLY", "AVGO"], "perdida": ["MSFT", "AMZN", "GE"], "mucha_perd": ["INTC", "TSLA", "DE"]}},
    "GEMI WARREN": {"estrella": "BRK-B", "top15": ["BRK-B", "JPM", "V", "PG", "KO", "WMT", "COST", "JNJ", "UNH", "LLY", "AAPL", "MSFT", "GOOGL", "SPY", "VTI"], "top3W": ["BRK-B", "JPM", "V"], "top3L": ["ARKK", "IBIT", "NVDA"], "r3": {"neutral": ["PG", "KO", "WMT"], "ganancia": ["COST", "JNJ", "UNH"], "mucha_gan": ["BRK-B", "JPM", "V"], "perdida": ["AAPL", "MSFT", "GOOGL"], "mucha_perd": ["ARKK", "IBIT", "NVDA"]}},
    "CLAUDE ANALISTA": {"estrella": "DE", "top15": ["DE", "NVDA", "LLY", "GE", "AMD", "META", "TSM", "GOOGL", "AMZN", "ASML", "MSFT", "RTX", "JPM", "COST", "V"], "top3W": ["DE", "NVDA", "LLY"], "top3L": ["TSLA", "INTC", "IBIT"], "r3": {"neutral": ["RTX", "JPM", "COST"], "ganancia": ["ASML", "MSFT", "V"], "mucha_gan": ["DE", "NVDA", "LLY"], "perdida": ["META", "TSM", "GOOGL"], "mucha_perd": ["TSLA", "INTC", "IBIT"]}},
    "CLAUDE FRICAS": {"estrella": "ASML", "top15": ["ASML", "TSM", "NVDA", "AVGO", "AMD", "MSFT", "META", "GOOGL", "AMZN", "LLY", "GE", "RTX", "COPX", "QQQ", "XLE"], "top3W": ["ASML", "TSM", "NVDA"], "top3L": ["PG", "KO", "JNJ"], "r3": {"neutral": ["VTI", "ACWI", "SPY"], "ganancia": ["LLY", "GE", "RTX"], "mucha_gan": ["ASML", "TSM", "NVDA"], "perdida": ["AMZN", "MSFT", "META"], "mucha_perd": ["PG", "KO", "JNJ"]}},
    "CLAUDE WARREN": {"estrella": "JPM", "top15": ["JPM", "V", "BRK-B", "COST", "WMT", "PG", "KO", "JNJ", "UNH", "LLY", "AAPL", "MSFT", "GOOGL", "SPY", "ACWI"], "top3W": ["JPM", "V", "BRK-B"], "top3L": ["ARKK", "TSLA", "COPX"], "r3": {"neutral": ["PG", "KO", "JNJ"], "ganancia": ["UNH", "LLY", "AAPL"], "mucha_gan": ["JPM", "V", "BRK-B"], "perdida": ["MSFT", "GOOGL", "SPY"], "mucha_perd": ["ARKK", "TSLA", "COPX"]}}
}

# --- FUNCIONES DE CÁLCULO ---
def calcular_reglas(ia, rank_actual, vars_actuales):
    d = DATOS_IA[ia]
    # R1: Top 15 (10 pts c/u)
    p1 = len(set(d["top15"]) & set(rank_actual[:15])) * 10
    
    # R2: Top 3 Win/Loss (50 base + 10 por pos exacta)
    p2 = 0
    if set(d["top3W"]) == set(rank_actual[:3]): p2 += 50
    for i in range(3):
        if i < len(rank_actual) and d["top3W"][i] == rank_actual[i]: p2 += 10
    if set(d["top3L"]) == set(rank_actual[-3:]): p2 += 50
    for i in range(3):
        if i < len(rank_actual) and d["top3L"][i] == rank_actual[-(3-i)]: p2 += 10
            
    # R3: Rangos
    p3 = 0
    for cat, tickers in d["r3"].items():
        hits = 0
        for t in tickers:
            v = vars_actuales.get(t, 0)
            if cat == "neutral" and -1.5 <= v <= 1.5: p3 += 2; hits += 1
            elif cat == "ganancia" and 1.51 <= v <= 5: p3 += 4; hits += 1
            elif cat == "mucha_gan" and v > 5: p3 += 6; hits += 1
            elif cat == "perdida" and -5 <= v <= -1.51: p3 -= 1; hits += 1
            elif cat == "mucha_perd" and v < -5: p3 -= 2; hits += 1
        if hits == 3: p3 += 5 # Bonus grupo

    # R4: Estrella
    p4 = 0
    pos_est = rank_actual.index(d["estrella"]) + 1
    if pos_est == 1: p4 = 40
    elif pos_est <= 3: p4 = 20
    elif pos_est >= 25: p4 = -40
    
    return p1, p2, p3, p4

# --- INTERFAZ ---
st.sidebar.header("⚙️ Configuración")
ronda_sel = st.sidebar.selectbox("Selecciona Ronda", list(RONDAS.keys()))
fecha_inicio = RONDAS[ronda_sel]["inicio"]

if st.sidebar.button("🚀 ACTUALIZAR TABLERO"):
    with st.spinner("Conectando con Wall Street..."):
        # Descarga de datos
        raw_data = yf.download(TICKERS, start=fecha_inicio)['Close'].ffill()
        
        if len(raw_data) > 0:
            hist_puntos = pd.DataFrame(index=raw_data.index)
            desglose = []
            
            # Recorrido diario
            for i in range(len(raw_data)):
                dia = raw_data.index[i]
                precios_dia = raw_data.iloc[i]
                vars_dia = ((precios_dia / raw_data.iloc[0]) - 1) * 100
                rank_dia = vars_dia.sort_values(ascending=False).index.tolist()
                
                for ia in DATOS_IA.keys():
                    p1, p2, p3, p4 = calcular_reglas(ia, rank_dia, vars_dia.to_dict())
                    hist_puntos.loc[dia, ia] = p1 + p2 + p3 + p4
                    if i == len(raw_data) - 1:
                        desglose.append({"Competidor": ia, "R1": p1, "R2": p2, "R3": p3, "R4": p4, "TOTAL": p1+p2+p3+p4})

            # VISUALIZACIÓN
            st.header(f"🏆 Estado del Campeonato: {ronda_sel}")
            
            # Gráfico Línea Continua
            st.subheader("📈 Evolución Temporal (Puntos Totales)")
            st.line_chart(hist_puntos)
            

            # Tabla Desglose
            st.subheader("📊 Auditoría por Reglas")
            df_final = pd.DataFrame(desglose).sort_values("TOTAL", ascending=False)
            st.dataframe(df_final.set_index("Competidor"), use_container_width=True)

            # Mercado
            st.subheader("🎯 Resumen de Mercado")
            c1, c2 = st.columns(2)
            ultimas_vars = ((raw_data.iloc[-1] / raw_data.iloc[0]) - 1) * 100
            with c1: st.write("**Top 5 Alcistas**"); st.table(ultimas_vars.sort_values(ascending=False).head(5))
            with c2: st.write("**Top 5 Bajistas**"); st.table(ultimas_vars.sort_values(ascending=True).head(5))
            
            st.balloons()
        else:
            st.error("No se pudieron descargar datos. Verifica la conexión.")
