import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, date

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Campeonato Bursátil 2026", layout="wide")

TICKERS = [
    "MSFT", "NVDA", "GOOGL", "META", "TSM", "V", "BRK-B", "JPM", "ASML", "INTC", 
    "AMD", "COST", "WMT", "PG", "GE", "DE", "RTX", "JNJ", "UNH", "LLY", 
    "AMZN", "TSLA", "KO", "AAPL", "AVGO", "SPY", "QQQ", "VTI", "ACWI", "XLE", 
    "GLD", "IBIT", "ARKK", "COPX"
]

# Definición de Rondas según tu instrucción
RONDAS = {
    "Ronda 1 (Feb 20 - Mar 31)": {"inicio": "2026-02-20", "fin": "2026-03-31"},
    "Ronda 2 (Abril)": {"inicio": "2026-04-01", "fin": "2026-04-30"},
    "Ronda 3 (Mayo)": {"inicio": "2026-05-01", "fin": "2026-05-31"},
}

# --- BASE DE DATOS DE LOS 9 COMPETIDORES ---
DATOS_IA = {
    "GPT FRICAS": {"R1_estrella": "XLE", "R1_top15": ["NVDA", "META", "TSM", "ASML", "MSFT", "AMZN", "GOOGL", "LLY", "COST", "V", "QQQ", "GE", "DE", "SPY", "XLE"]},
    "GPT WARREN": {"R1_estrella": "NVDA", "R1_top15": ["NVDA", "TSM", "ASML", "AMZN", "GOOGL", "WMT", "COST", "LLY", "RTX", "GE", "DE", "PG", "KO", "V", "BRK-B"]},
    "GPT AG": {"R1_estrella": "INTC", "R1_top15": ["INTC", "ASML", "TSM", "COPX", "WMT", "JNJ", "PG", "COST", "RTX", "META", "KO", "ACWI", "QQQ", "BRK-B", "VTI"]},
    "GEMI AG": {"R1_estrella": "NVDA", "R1_top15": ["NVDA", "MSFT", "TSM", "LLY", "COPX", "AMZN", "META", "ASML", "GOOGL", "AMD", "JPM", "GE", "SPY", "QQQ", "VTI"]},
    "GEMI FRICAS": {"R1_estrella": "NVDA", "R1_top15": ["NVDA", "LLY", "AVGO", "TSM", "AMD", "META", "ASML", "MSFT", "GOOGL", "AMZN", "GE", "RTX", "COST", "V", "JPM"]},
    "GEMI WARREN": {"R1_estrella": "BRK-B", "R1_top15": ["BRK-B", "JPM", "V", "PG", "KO", "WMT", "COST", "JNJ", "UNH", "LLY", "AAPL", "MSFT", "GOOGL", "SPY", "VTI"]},
    "CLAUDE ANALISTA": {"R1_estrella": "DE", "R1_top15": ["DE", "NVDA", "LLY", "GE", "AMD", "META", "TSM", "GOOGL", "AMZN", "ASML", "MSFT", "RTX", "JPM", "COST", "V"]},
    "CLAUDE FRICAS": {"R1_estrella": "ASML", "R1_top15": ["ASML", "TSM", "NVDA", "AVGO", "AMD", "MSFT", "META", "GOOGL", "AMZN", "LLY", "GE", "RTX", "COPX", "QQQ", "XLE"]},
    "CLAUDE WARREN": {"R1_estrella": "JPM", "R1_top15": ["JPM", "V", "BRK-B", "COST", "WMT", "PG", "KO", "JNJ", "UNH", "LLY", "AAPL", "MSFT", "GOOGL", "SPY", "ACWI"]}
}

# --- MOTOR DE CÁLCULO HISTÓRICO ---
@st.cache_data
def obtener_historia_puntos(inicio, fin):
    # Traemos los precios de cierre diarios de todo el universo
    data = yf.download(TICKERS, start=inicio, end=fin)['Close']
    data = data.ffill() # Llenar huecos de feriados
    
    puntos_diarios = pd.DataFrame(index=data.index)
    precios_inicio = data.iloc[0]
    
    # Para cada día de la historia, calculamos el ranking y los puntos
    for fecha in data.index:
        precios_hoy = data.loc[fecha]
        variacion_hoy = ((precios_hoy / precios_inicio) - 1) * 100
        ranking_dia = variacion_hoy.sort_values(ascending=False)
        top_15_dia = ranking_dia.head(15).index.tolist()
        lista_completa = ranking_dia.index.tolist()
        
        for ia, pred in DATOS_IA.items():
            pts = 0
            # Regla 1: Top 15
            aciertos = len(set(pred["R1_top15"]) & set(top_15_dia))
            pts += aciertos * 10
            # Regla 4: Estrella
            pos_est = lista_completa.index(pred["R1_estrella"]) + 1
            if pos_est == 1: pts += 40
            elif pos_est <= 3: pts += 20
            elif pos_est >= 25: pts -= 40
            
            puntos_diarios.loc[fecha, ia] = pts
            
    return puntos_diarios, ranking_dia

# --- INTERFAZ ---
st.title("🏆 Dashboard Campeonato Bursátil 2026")

ronda_actual = st.sidebar.selectbox("Seleccionar Ronda", list(RONDAS.keys()))
f_inicio = RONDAS[ronda_actual]["inicio"]
f_fin = date.today() if datetime.today().strftime('%Y-%m-%d') < RONDAS[ronda_actual]["fin"] else RONDAS[ronda_actual]["fin"]

if st.sidebar.button("📊 ANALIZAR EVOLUCIÓN"):
    with st.spinner("Calculando trayectorias..."):
        df_evolucion, ultimo_ranking = obtener_historia_puntos(f_inicio, f_fin)
        
        # 1. GRÁFICO DE LÍNEAS (Evolución)
        st.subheader(f"📈 Evolución de Puntos - {ronda_actual}")
        st.line_chart(df_evolucion, height=400)
        

        # 2. RANKING ACTUAL
        st.divider()
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🥇 Posiciones al día de hoy")
            puntos_finales = df_evolucion.iloc[-1].sort_values(ascending=False).to_frame("Puntos Totales")
            st.dataframe(puntos_finales, use_container_width=True)
            
        with col2:
            st.subheader("🚀 Top 5 Tickers del Mes")
            st.table(ultimo_ranking.head(5).to_frame("Variación %"))

    st.balloons()
else:
    st.info("Haz clic en 'Analizar Evolución' para cargar los datos en tiempo real.")
