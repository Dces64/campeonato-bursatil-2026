import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, date

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Tablero de Control - Campeonato 2026", layout="wide")

TICKERS = ["MSFT", "NVDA", "GOOGL", "META", "TSM", "V", "BRK-B", "JPM", "ASML", "INTC", "AMD", "COST", "WMT", "PG", "GE", "DE", "RTX", "JNJ", "UNH", "LLY", "AMZN", "TSLA", "KO", "AAPL", "AVGO", "SPY", "QQQ", "VTI", "ACWI", "XLE", "GLD", "IBIT", "ARKK", "COPX"]

# Ronda 1 extendida según tus instrucciones
RONDAS = {"Ronda 1": {"inicio": "2026-02-20", "fin": "2026-03-31"}}

# --- BASE DE DATOS COMPLETA (9 COMPETIDORES) ---
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

# --- MOTOR DE CÁLCULO ---
def obtener_score(ia, ranking_mkt, variaciones):
    ia_data = DATOS_IA[ia]
    p1 = len(set(ia_data["top15"]) & set(ranking_mkt[:15])) * 10
    
    p2 = 0
    if set(ia_data["top3W"]) == set(ranking_mkt[:3]): p2 += 50
    for i in range(3): 
        if i < len(ranking_mkt) and ia_data["top3W"][i] == ranking_mkt[i]: p2 += 10
    if set(ia_data["top3L"]) == set(ranking_mkt[-3:]): p2 += 50
    for i in range(3):
        if i < len(ranking_mkt) and ia_data["top3L"][i] == ranking_mkt[-(3-i)]: p2 += 10
            
    p3 = 0
    for cat, tks in ia_data["r3"].items():
        aciertos = 0
        for t in tks:
            v = variaciones.get(t, 0)
            if cat=="neutral" and -1.5<=v<=1.5: p3+=2; aciertos+=1
            elif cat=="ganancia" and 1.51<=v<=5: p3+=4; aciertos+=1
            elif cat=="mucha_gan" and v>5: p3+=6; aciertos+=1
            elif cat=="perdida" and -5<=v<=-1.51: p3-=1; aciertos+=1
            elif cat=="mucha_perd" and v<-5: p3-=2; aciertos+=1
        if aciertos == 3: p3 += 5
        
    p4 = 0
    pos_est = ranking_mkt.index(ia_data["estrella"]) + 1
    if pos_est == 1: p4 = 40
    elif pos_est <= 3: p4 = 20
    elif pos_est >= 25: p4 = -40
    
    return p1, p2, p3, p4

# --- INTERFAZ ---
st.title("🏆 Campeonato Bursátil 2026 - Control Center")

if st.sidebar.button("🚀 ACTUALIZAR SISTEMA"):
    with st.spinner("Descargando historial y auditando reglas..."):
        # Descarga histórica para la línea continua
        data = yf.download(TICKERS, start=RONDAS["Ronda 1"]["inicio"])['Close'].ffill()
        
        evolucion = pd.DataFrame(index=data.index)
        desglose_final = []

        for fecha in data.index:
            precios_hoy = data.loc[fecha]
            vars_hoy = ((precios_hoy / data.iloc[0]) - 1) * 100
            rank_hoy = vars_hoy.sort_values(ascending=False).index.tolist()
            
            for ia in DATOS_IA.keys():
                p1, p2, p3, p4 = obtener_score(ia, rank_hoy, vars_hoy.to_dict())
                total = p1 + p2 + p3 + p4
                evolucion.loc[fecha, ia] = total
                if fecha == data.index[-1]:
                    desglose_final.append({"Competidor": ia, "R1": p1, "R2": p2, "R3": p3, "R4": p4, "TOTAL": total})

        # 1. GRÁFICO DE LÍNEA CONTINUA (Estilo Google Finance)
        st.subheader("📈 Evolución de Puntos (Histórico)")
        st.line_chart(evolucion, height=450)
        

        # 2. TABLA DE DESGLOSE POR REGLAS
        st.subheader("📊 Auditoría de Reglas (Puntos al Corte)")
        df_final = pd.DataFrame(desglose_final).sort_values("TOTAL", ascending=False)
        st.dataframe(df_final.set_index("Competidor"), use_container_width=True)

        # 3. RANKING DE MERCADO
        st.subheader("🎯 Estado del Mercado (Top vs Bottom)")
        col1, col2 = st.columns(2)
        vars_actuales = ((data.iloc[-1] / data.iloc[0]) - 1) * 100
        rank_actual = vars_actuales.sort_values(ascending=False)
        with col1: st.write("**Top 5 Ganadoras**"); st.table(rank_actual.head(5))
        with col2: st.write("**Top 5 Perdedoras**"); st.table(rank_actual.tail(5))

    st.balloons()
