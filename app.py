import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- Configuração da Página ---
st.set_page_config(page_title="Painel Pro - B3", page_icon="⚡", layout="wide")

# --- Funções Ajudantes ---
@st.cache_data(ttl=900)
def analisar_mercado(ativos_selecionados):
    lista_de_analise = []
    barra_progresso = st.progress(0, text="Iniciando análise...")
    for i, ativo in enumerate(ativos_selecionados):
        barra_progresso.progress((i + 1) / len(ativos_selecionados), text=f"Analisando: {ativo}")
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
    barra_progresso.empty()
    return pd.DataFrame(lista_de_analise)

def colorir_tendencia(val):
    color = '#4F4F4F'
    if val == 'Alta Forte': color = 'green'
    elif val == 'Alta': color = 'lightgreen'
    elif val == 'Baixa Forte': color = 'red'
    elif val == 'Baixa': color = 'lightpink'
    return f'color: {color}; font-weight: bold;'

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# --- Barra Lateral (Sidebar) ---
with st.sidebar:
    # IMAGEM DO LOGO CORRIGIDA
    st.image("https://static.vecteezy.com/system/resources/previews/013/462/760/original/simple-finance-logo-vector.jpg", width=100)
    st.title("Painel Pro de Análise")
    st.write("---")
    st.header("Configurações")
    
    default_assets = (
        "PETR4.SA,VALE3.SA,ITUB4.SA,BBDC4.SA,B3SA3.SA,ELET3.SA,ABEV3.SA,RENT3.SA,"
        "WEGE3.SA,PRIO3.SA,HAPV3.SA,ITSA4.SA,SUZB3.SA,GGBR4.SA,BBAS3.SA,EQTL3.SA,"
        "RADL3.SA,RDOR3.SA,CSAN3.SA,MGLU3.SA,VIVT3.SA,LREN3.SA,ASAI3.SA,TOTS3.SA,"
        "EMBR3.SA,CMIG4.SA,NTCO3.SA,BRFS3.SA,SBSP3.SA,CIEL3.SA,COGN3.SA,VIIA3.SA"
    )
    assets_input = st.text_area("Ativos para Análise (separados por vírgula)", value=default_assets, height=250)
    ativos = [ativo.strip().upper() for ativo in assets_input.split(',')]
    
    iniciar_analise = st.sidebar.button('📊 Gerar Análise de Mercado')

# --- Interface Principal ---
st.title('⚡ Painel de Análise de Mercado - B3')
st.write('Uma ferramenta para analisar a tendência das principais ações brasileiras e identificar oportunidades de Gaps no pré-mercado.')

tab_scanner, tab_aprenda = st.tabs(["🔎 Scanner de Mercado", "📚 Aprenda a Estratégia"])

with tab_scanner:
    if iniciar_analise:
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

        st.subheader('Análise de Tendência dos Ativos')
        df_styled = df_analise.style.apply(lambda row: row.map(colorir_tendencia), subset=['Tendência'])\
                                     .format({'Preço Atual': "R$ {:.2f}", 'Dist. Média 50d (%)': "{:.2f}%"})
        st.dataframe(df_styled, hide_index=True, use_container_width=True)

        csv = convert_df_to_csv(df_analise)
        nome_relatorio = f"analise_mercado_{datetime.now().strftime('%Y-%m-%d')}.csv"
        st.download_button("📄 Baixar Relatório Completo em CSV", csv, nome_relatorio, 'text/csv')
    else:
        st.info('Aguardando o comando para iniciar a análise. Use o botão na barra lateral.')

with tab_aprenda:
    st.header("Entendendo a Estratégia do Painel")
    st.write("Esta ferramenta não é uma recomendação de compra ou venda...") # Mantive o texto curto para não colar tudo de novo
    st.write("---")

    st.subheader("1. O Conceito de Tendência (Médias Móveis)")
    # IMAGEM DO GRÁFICO CORRIGIDA
    st.image("https://i.imgur.com/g0559pG.png", caption="Exemplo de Médias Móveis de 50 (azul) e 200 (vermelho) dias.")
    st.write("""
    O indicador mais importante para um trader é a tendência...
    """)
    st.write("---")
    
    st.subheader("2. A Oportunidade do Gap")
    st.write("""
    Um "Gap" acontece quando o preço de abertura de um ativo é muito diferente...
    """)
    st.write("---")

    st.subheader("3. O Passo Mais Importante: Gerenciamento de Risco")
    st.error("""
    **NENHUMA ESTRATÉGIA FUNCIONA SEM GERENCIAMENTO DE RISCO.**
    ...
    """)
