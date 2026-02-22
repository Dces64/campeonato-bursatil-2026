import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Campeonato Bursátil 2026", layout="wide")
st.title("🏆 Tablero de Control - Campeonato Bursátil 2026")

# --- 1. EL UNIVERSO DE TICKERS ---
# Nota: Yahoo Finance usa BRK-B en lugar de BRK.B
TICKERS = [
    "MSFT", "NVDA", "GOOGL", "META", "TSM", "V", "BRK-B", "JPM", "ASML", "INTC", 
    "AMD", "COST", "WMT", "PG", "GE", "DE", "RTX", "JNJ", "UNH", "LLY", 
    "AMZN", "TSLA", "KO", "AAPL", "AVGO", "SPY", "QQQ", "VTI", "ACWI", "XLE", 
    "GLD", "IBIT", "ARKK", "COPX"
]

# --- 2. FECHAS DE LA RONDA ---
st.sidebar.header("Configuración de la Ronda")
st.sidebar.write("Elige las fechas para calcular (Ej: 1er día hábil a último día hábil)")
start_date = st.sidebar.date_input("Fecha de Apertura", datetime(2026, 2, 23))
end_date = st.sidebar.date_input("Fecha de Cierre (Actual)", datetime.today())

# --- 3. MOTOR DE DATOS (Se conecta a Wall Street solo) ---
@st.cache_data # Esto hace que no descargue los datos a cada rato, haciéndola rapidísima
def obtener_datos(start, end, tickers):
    # Sumamos un día a end_date para asegurar que traiga el cierre de ese día
    end_adj = end + timedelta(days=1)
    
    # Descargamos todos los tickers a la vez
    data = yf.download(tickers, start=start, end=end_adj, group_by='ticker', auto_adjust=True)
    
    resultados = []
    for ticker in tickers:
        try:
            # Tomamos la apertura del primer día y el cierre del último día disponible
            apertura = data[ticker]['Open'].iloc[0]
            cierre = data[ticker]['Close'].iloc[-1]
            
            # Cálculo de variación mensual = (Cierre / Apertura - 1) * 100
            variacion = ((cierre / apertura) - 1) * 100
            
            resultados.append({
                "Ticker": ticker,
                "Apertura": round(apertura, 2),
                "Cierre": round(cierre, 2),
                "Variación (%)": round(variacion, 2)
            })
        except Exception as e:
            # Si un ticker falla (ej: feriado), lo salta temporalmente
            pass
            
    df = pd.DataFrame(resultados)
    
    # Ordenamos del mejor al peor (Ranking real)
    if not df.empty:
        df = df.sort_values(by="Variación (%)", ascending=False).reset_index(drop=True)
        df.index = df.index + 1 # Para que el ranking empiece en 1 y no en 0
        
    return df

# --- 4. EJECUCIÓN DEL CÁLCULO ---
st.write("### 📊 Rendimiento Real del Mercado")
if st.sidebar.button("Calcular Resultados de la Ronda"):
    with st.spinner("Conectando con Wall Street y calculando..."):
        df_mercado = obtener_datos(start_date, end_date, TICKERS)
        
        # Mostramos la tabla principal
        st.dataframe(df_mercado, use_container_width=True)
        
        # --- EJEMPLO REGLA 4: Pick Estrella (Automatizado) ---
        st.write("---")
        st.write("### ⭐ Evaluación de Picks Estrellas (Regla 4)")
        
        # Aquí pondrás lo que predijo cada IA. Esto es un ejemplo:
        predicciones = {
            "Claude 3.5": "NVDA",
            "GPT Fricas": "XLE",
            "Gemi AG": "IBIT"
        }
        
        resultados_picks = []
        for ia, pick in predicciones.items():
            if pick in df_mercado['Ticker'].values:
                # Buscamos en qué posición del ranking quedó el pick
                posicion = df_mercado[df_mercado['Ticker'] == pick].index[0]
                
                # Reglas de puntaje
                puntos = 0
                if posicion == 1: puntos = 40
                elif posicion <= 3: puntos = 20
                elif posicion <= 5: puntos = 10
                elif posicion >= 25: puntos = -40 # Top 10 últimos (puestos 25 a 34)
                
                resultados_picks.append({"IA": ia, "Pick Estrella": pick, "Posición Final": posicion, "Puntos Ganados": puntos})
                
        st.table(pd.DataFrame(resultados_picks))
        
        st.success("¡Cálculo finalizado con éxito! Este es solo el comienzo.")
