import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- Configuração da Página ---
st.set_page_config(page_title="Painel Pro - B3", page_icon="⚡", layout="wide")

# --- Barra Lateral (Sidebar) ---
with st.sidebar:
    st.image("https://i.imgur.com/M6LpJ8o.png", width=100) # Um logo simples
    st.title("Painel Pro de Análise")
    st.write("---")
    st.header("Configurações")
    
    # Lista de ativos editável pelo usuário
    default_assets = (
        "PETR4.SA,VALE3.SA,ITUB4.SA,BBDC4.SA,B3SA3.SA,ELET3.SA,ABEV3.SA,RENT3.SA,"
        "WEGE3.SA,PRIO3.SA,HAPV3.SA,ITSA4.SA,SUZB3.SA,GGBR4.SA,BBAS3.SA,EQTL3.SA,"
        "RADL3.SA,RDOR3.SA,CSAN3.SA,MGLU3.SA,VIVT3.SA,LREN3.SA,ASAI3.SA,TOTS3.SA,"
        "EMBR3.SA,CMIG4.SA,NTCO3.SA,BRFS3.SA,SBSP3.SA,CIEL3.SA,COGN3.SA,VIIA3.SA"
    )
    assets_input = st.text_area("Ativos para Análise (separados por vírgula)", value=default_assets, height=250)
    ativos = [ativo.strip().upper() for ativo in assets_input.split(',')]

# --- Título Principal ---
st.title('⚡ Painel de Análise de Mercado - B3')
st.write('Uma ferramenta para analisar a tendência das principais ações brasileiras e identificar oportunidades de Gaps no pré-mercado.')

# --- Função de Análise (com cache para performance) ---
@st.cache_data(ttl=900)
def analisar_mercado(ativos_selecionados):
    lista_de_analise = []
    for ativo in ativos_selecionados:
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
            if ultimo_preco > sma50 and ultimo_preco > sma200: tendencia = "Alta Forte"
            elif ultimo_preco > sma50 or ultimo_preco > sma200: tendencia = "Alta"
            elif ultimo_preco < sma50 and ultimo_preco < sma200: tendencia = "Baixa Forte"
            else: tendencia = "Baixa"
            
            dados_pre = ticker.info
            gap_percentual = None
            if 'preMarketPrice' in dados_pre and dados_pre['preMarketPrice'] is not None:
                preco_pre_mercado = dados_pre['preMarketPrice']
                fechamento_anterior = hist['Close'].iloc[-2]
                gap_percentual = ((preco_pre_mercado - fechamento_anterior) / fechamento_anterior) * 100
            
            lista_de_analise.append({
                'Ativo': ativo,
                'Preço Atual': ultimo_preco,
                'Tendência': tendencia,
                'Gap (%)': gap_percentual,
                'Dist. Média 50d (%)': ((ultimo_preco / sma50) - 1) * 100,
            })
        except Exception as e: pass 
    return pd.DataFrame(lista_de_analise)

# --- Lógica da Interface ---
if st.sidebar.button('📊 Gerar Análise de Mercado'):
    with st.spinner('Analisando o mercado... Isso pode levar alguns minutos.'):
        df_analise = analisar_mercado(ativos)
    
    st.success('Análise finalizada!')

    col1, col2, col3 = st.columns(3)
    total_ativos = len(df_analise)
    ativos_em_alta_forte = len(df_analise[df_analise['Tendência'] == 'Alta Forte'])
    ativos_com_gap = len(df_analise.dropna(subset=['Gap (%)']))
    col1.metric("Total de Ativos Analisados", f"{total_ativos}")
    col2.metric("Ativos em Alta Forte", f"{ativos_em_alta_forte}")
    col3.metric("Ativos com Gap Hoje", f"{ativos_com_gap}")
    st.write("---")

    def colorir_tendencia(val):
        color = '#4F4F4F' # Cor padrão cinza escuro
        if val == 'Alta Forte': color = 'green'
        elif val == 'Alta': color = 'lightgreen'
        elif val == 'Baixa Forte': color = 'red'
        elif val == 'Baixa': color = 'lightpink'
        return f'color: {color}; font-weight: bold;'

    tab_tabela, tab_graficos = st.tabs(["📋 Tabela de Dados", "📈 Gráficos Visuais"])

    with tab_tabela:
        st.subheader('Análise de Tendência dos Ativos')
        # --- CORREÇÃO APLICADA AQUI ---
        # Removemos o '.format()' para garantir compatibilidade e aplicamos a cor ao texto
        df_styled = df_analise.style.apply(lambda row: row.map(colorir_tendencia), subset=['Tendência'])
        
        st.dataframe(df_styled, hide_index=True, use_container_width=True)

        # --- Botão de Download ---
        @st.cache_data
