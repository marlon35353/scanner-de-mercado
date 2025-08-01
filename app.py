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

    # --- Cartões de Resumo (Metrics) ---
    col1, col2, col3 = st.columns(3)
    total_ativos = len(df_analise)
    ativos_em_alta_forte = len(df_analise[df_analise['Tendência'] == 'Alta Forte'])
    ativos_com_gap = len(df_analise.dropna(subset=['Gap (%)']))
    col1.metric("Total de Ativos Analisados", f"{total_ativos}")
    col2.metric("Ativos em Alta Forte", f"{ativos_em_alta_forte}")
    col3.metric("Ativos com Gap Hoje", f"{ativos_com_gap}")
    st.write("---")

    # --- Função para colorir a tabela ---
    def colorir_tendencia(val):
        color = 'gray'
        if val == 'Alta Forte': color = 'lightgreen'
        elif val == 'Alta': color = 'palegreen'
        elif val == 'Baixa Forte': color = 'lightcoral'
        elif val == 'Baixa': color = 'lightpink'
        return f'background-color: {color}'

    # --- Abas (Tabs) ---
    tab_tabela, tab_graficos = st.tabs(["📋 Tabela de Dados", "📈 Gráficos Visuais"])

    with tab_tabela:
        st.subheader('Análise de Tendência dos Ativos')
        df_styled = df_analise.style.applymap(colorir_tendencia, subset=['Tendência'])\
                                     .format({'Preço Atual': "R$ {:.2f}", 
                                              'Gap (%)': "{:.2f}%", 
                                              'Dist. Média 50d (%)': "{:.2f}%"})
        st.dataframe(df_styled, hide_index=True, use_container_width=True)

        # --- Botão de Download ---
        @st.cache_data
        def convert_df_to_csv(df): return df.to_csv(index=False).encode('utf-8')
        csv = convert_df_to_csv(df_analise)
        nome_relatorio = f"analise_mercado_{datetime.now().strftime('%Y-%m-%d')}.csv"
        st.download_button(
            label="📄 Baixar Relatório Completo em CSV",
            data=csv,
            file_name=nome_relatorio,
            mime='text/csv',
        )

    with tab_graficos:
        st.subheader('Visualização da Distância para a Média de 50 Dias')
        st.write("Ativos com barras positivas estão acima da média (tendência de alta de curto prazo).")
        
        # Prepara dados para o gráfico
        df_grafico = df_analise.set_index('Ativo')['Dist. Média 50d (%)'].dropna()
        st.bar_chart(df_grafico)

else:
    st.info('Aguardando o comando para iniciar a análise. Use o botão na barra lateral.')
