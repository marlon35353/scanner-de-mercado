# IMPORTANTE: Copie e cole este código EXATAMENTE como está.
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- Configuração da Página ---
st.set_page_config(page_title="Painel de Análise B3", page_icon="💡", layout="wide")
st.title('💡 Painel de Análise de Mercado - B3')
st.write('Uma ferramenta para analisar a tendência das principais ações brasileiras e identificar oportunidades de Gaps no pré-mercado.')

# --- Função Principal de Análise ---
@st.cache_data(ttl=900)
def analisar_mercado():
    ativos = [
        "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "B3SA3.SA", "ELET3.SA", "ABEV3.SA", 
        "RENT3.SA", "WEGE3.SA", "PRIO3.SA", "HAPV3.SA", "ITSA4.SA", "SUZB3.SA", "GGBR4.SA",
        "BBAS3.SA", "EQTL3.SA", "RADL3.SA", "RDOR3.SA", "CSAN3.SA", "UGPA3.SA", "VBBR3.SA",
        "MGLU3.SA", "VIVT3.SA", "RAIL3.SA", "LREN3.SA", "ASAI3.SA", "KLBN11.SA", "TOTS3.SA",
        "EMBR3.SA", "HYPE3.SA", "CMIG4.SA", "NTCO3.SA", "BRFS3.SA", "SBSP3.SA", "GOAU4.SA",
        "TIMS3.SA", "CSNA3.SA", "CPLE6.SA", "ENEV3.SA", "CRFB3.SA", "CCRO3.SA", "RAIZ4.SA",
        "CIEL3.SA", "ALPA4.SA", "BEEF3.SA", "RRRP3.SA", "CYRE3.SA", "IRBR3.SA", "PCAR3.SA",
        "MRFG3.SA", "PETZ3.SA", "ARZZ3.SA", "SOMA3.SA", "EZTC3.SA", "CVCB3.SA", "USIM5.SA",
        "MRVE3.SA", "DXCO3.SA", "MULT3.SA", "BRKM5.SA", "YDUQ3.SA", "COGN3.SA", "VIIA3.SA"
    ]
    
    lista_de_analise = []
    barra_progresso = st.progress(0, text="Iniciando análise...")

    for i, ativo in enumerate(ativos):
        barra_progresso.progress((i + 1) / len(ativos), text=f"Analisando: {ativo}")
        try:
            ticker = yf.Ticker(ativo)
            hist = ticker.history(period="1y")
            
            if len(hist) < 200: continue

            hist['SMA50'] = hist['Close'].rolling(window=50).mean()
            hist['SMA200'] = hist['Close'].rolling(window=200).mean()
            
            ultimo_preco = hist['Close'].iloc[-1]
            sma50 = hist['SMA50'].iloc[-1]
            sma200 = hist['SMA200'].iloc[-1]

            tendencia = "Lateral"
            if ultimo_preco > sma50 and ultimo_preco > sma200:
                tendencia = "Alta Forte"
            elif ultimo_preco > sma50 or ultimo_preco > sma200:
                tendencia = "Alta"
            
            dados_pre = ticker.info
            gap_percentual = "N/A"
            if 'preMarketPrice' in dados_pre and dados_pre['preMarketPrice'] is not None:
                preco_pre_mercado = dados_pre['preMarketPrice']
                fechamento_anterior = hist['Close'].iloc[-2]
                gap = ((preco_pre_mercado - fechamento_anterior) / fechamento_anterior) * 100
                gap_percentual = f"{gap:.2f}%"
            
            lista_de_analise.append({
                'Ativo': ativo,
                'Preço Atual': f"R$ {ultimo_preco:.2f}",
                'Tendência': tendencia,
                'Gap (%)': gap_percentual,
                'Dist. Média 50d': f"{((ultimo_preco / sma50) - 1) * 100:.2f}%",
            })
        except Exception as e:
            pass 
            
    barra_progresso.empty()
    return pd.DataFrame(lista_de_analise)

if st.button('📊 Gerar Análise de Mercado'):
    df_analise = analisar_mercado()
    st.success('Análise finalizada!')
    
    st.subheader('Análise de Tendência dos Ativos')
    st.dataframe(df_analise, hide_index=True, use_container_width=True)

    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df_to_csv(df_analise)
    nome_relatorio = f"analise_mercado_{datetime.now().strftime('%Y-%m-%d')}.csv"
    st.download_button(
        label="📄 Baixar Relatório Completo em CSV",
        data=csv,
        file_name=nome_relatorio,
        mime='text/csv',
    )
