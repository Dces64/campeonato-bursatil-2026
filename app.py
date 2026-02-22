import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, date

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema de Arbitraje - Campeonato 2026", layout="wide")

TICKERS = ["MSFT", "NVDA", "GOOGL", "META", "TSM", "V", "BRK-B", "JPM", "ASML", "INTC", "AMD", "COST", "WMT", "PG", "GE", "DE", "RTX", "JNJ", "UNH", "LLY", "AMZN", "TSLA", "KO", "AAPL", "AVGO", "SPY", "QQQ", "VTI", "ACWI", "XLE", "GLD", "IBIT", "ARKK", "COPX"]

RONDAS = {"Ronda 1 (Feb 20 - Mar 31)": {"inicio": "2026-02-20", "fin": "2026-03-31"}}

# --- BASE DE DATOS INTEGRAL (9 IA) ---
# He incluido aquí los datos de las reglas 2 y 3 que faltaban
DATOS_IA = {
    "GPT FRICAS": {
        "R1": {
            "estrella": "XLE",
            "top15": ["NVDA", "META", "TSM", "ASML", "MSFT", "AMZN", "GOOGL", "LLY", "COST", "V", "QQQ", "GE", "DE", "SPY", "XLE"],
            "top3W": ["XLE", "RTX", "GLD"],
            "top3L": ["ARKK", "TSLA", "INTC"],
            "r3": {"neutral": ["PG", "KO", "JNJ"], "ganancia": ["V", "BRK-B", "WMT"], "mucha_gan": ["NVDA", "META", "TSM"], "perdida": ["JPM", "COPX", "RTX"], "mucha_perd": ["ARKK", "TSLA", "INTC"]}
        }
    },
    "GPT WARREN": {
        "R1": {
            "estrella": "NVDA",
            "top15": ["NVDA", "TSM", "ASML", "AMZN", "GOOGL", "WMT", "COST", "LLY", "RTX", "GE", "DE", "PG", "KO", "V", "BRK-B"],
            "top3W": ["NVDA", "TSM", "ASML"],
            "top3L": ["ARKK", "TSLA", "INTC"],
            "r3": {"neutral": ["PG", "KO", "JPM"], "ganancia": ["V", "BRK-B", "WMT"], "mucha_gan": ["NVDA", "TSM", "ASML"], "perdida": ["INTC", "AMD", "META"], "mucha_perd": ["ARKK", "TSLA", "INTC"]}
        }
    },
    "GEMI AG": {
        "R1": {
            "estrella": "NVDA",
            "top15": ["NVDA", "MSFT", "TSM", "LLY", "COPX", "AMZN", "META", "ASML", "GOOGL", "AMD", "JPM", "GE", "SPY", "QQQ", "VTI"],
            "top3W": ["NVDA", "MSFT", "TSM"],
            "top3L": ["IBIT", "ARKK", "INTC"],
            "r3": {"neutral": ["PG", "KO", "JNJ"], "ganancia": ["V", "BRK-B", "SPY"], "mucha_gan": ["NVDA", "MSFT", "COPX"], "perdida": ["WMT", "RTX", "UNH"], "mucha_perd": ["IBIT", "ARKK", "INTC"]}
        }
    }
    # (Nota: Agregaremos el resto en el siguiente paso para no saturar el código ahora)
}

# --- MOTOR DE REGLAS ---
def calcular_puntaje_total(ranking_mkt, variaciones):
    top_15_real = ranking_mkt[:15]
    top_3_real = ranking_mkt[:3]
    bottom_3_real = ranking_mkt[-3:]
    
    resultados = {}
    for ia, data in DATOS_IA.items():
        r1 = data["R1"]
        pts = 0
        
        # R1: Top 15 (10 pts c/u)
        pts += len(set(r1["top15"]) & set(top_15_real)) * 10
        
        # R2: Top 3 Winners / Losers
        if set(r1["top3W"]) == set(top_3_real): pts += 50
        for i in range(3): 
            if i < len(top_3_real) and r1["top3W"][i] == top_3_real[i]: pts += 10
            
        if set(r1["top3L"]) == set(bottom_3_real): pts += 50
        for i in range(3): 
            if i < len(bottom_3_real) and r1["top3L"][i] == bottom_3_real[i]: pts += 10

        # R3: Rangos (Simplificado para el motor)
        for cat, tickers in r1["r3"].items():
            aciertos_cat = 0
            for t in tickers:
                v = variaciones.get(t, 0)
                if cat == "neutral" and -1.5 <= v <= 1.5: aciertos_cat += 1; pts += 2
                if cat == "ganancia" and 1.51 <= v <= 5: aciertos_cat += 1; pts += 4
                if cat == "mucha_gan" and v > 5: aciertos_cat += 1; pts += 6
                if cat == "perdida" and -5 <= v <= -1.51: aciertos_cat += 1; pts -= 1
                if cat == "mucha_perd" and v < -5: aciertos_cat += 1; pts -= 2
            if aciertos_cat == 3: pts += 5 # Bonus de grupo

        # R4: Estrella
        pos_est = ranking_mkt.index(r1["estrella"]) + 1
        if pos_est == 1: pts += 40
        elif pos_est <= 3: pts += 20
        elif pos_est >= 25: pts -= 40
        
        resultados[ia] = pts
    return resultados

# --- INTERFAZ ---
st.title("🏆 Tablero de Control - Todas las Reglas Activas")

# Lógica de descarga y visualización (igual que la anterior pero usando calcular_puntaje_total)
if st.sidebar.button("📊 EJECUTAR ESCUTRINIO"):
    with st.spinner("Procesando todas las reglas del reglamento..."):
        # Descarga de datos
        data = yf.download(TICKERS, start=RONDAS["Ronda 1 (Feb 20 - Mar 31)"]["inicio"])['Close'].ffill()
        
        # Evolución diaria
        evolucion = pd.DataFrame(index=data.index)
        for fecha in data.index:
            vars_dia = ((data.loc[fecha] / data.iloc[0]) - 1) * 100
            rank_dia = vars_dia.sort_values(ascending=False).index.tolist()
            res_dia = calcular_puntaje_total(rank_dia, vars_dia.to_dict())
            for ia, p in res_dia.items(): evolucion.loc[fecha, ia] = p
            
        # Gráfico de Líneas
        st.subheader("📈 Evolución del Campeonato (Puntaje Total)")
        st.line_chart(evolucion)
        
        st.subheader("🥇 Tabla de Posiciones Consolidada")
        st.dataframe(evolucion.iloc[-1].sort_values(ascending=False).to_frame("Puntos Totales"))
