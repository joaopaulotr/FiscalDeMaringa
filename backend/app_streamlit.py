import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from coletor import processar_liquidacoes_pagas, limpar_nome_fornecedor
import locale

# Configuração da página
st.set_page_config(
    page_title="Fiscal de Maringá - Análise de Liquidações",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuração de locale para formatação brasileira
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        pass

# Função para formatar valores em reais
def formatar_valor(valor):
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def carregar_dados_liquidacoes():
    caminho_arquivo = "backend/Liquidações pagas (1).csv"
    df = processar_liquidacoes_pagas(caminho_arquivo, silencioso=True)
    return df

# Título principal
st.title("🏛️ Fiscal de Maringá")

abas = st.tabs([
    "📊 Liquidações",
    "🏢 Fornecedores",
    "📁 Outros Dados"
])

with abas[0]:
    st.header("📊 Análise de Liquidações Pagas")
    df = carregar_dados_liquidacoes()
    if df is not None:
        st.subheader("🔎 Resumo das Liquidações")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 Total Gasto", formatar_valor(df['valor'].sum()), delta=f"+{formatar_valor(df['valor'].max())}")
        with col2:
            st.metric("📝 Registros", len(df), delta=f"+{len(df[df['valor'] > df['valor'].mean()])} acima da média")
        with col3:
            st.metric("📊 Média", formatar_valor(df['valor'].mean()), delta=f"Mediana: {formatar_valor(df['valor'].median())}")
        with col4:
            st.metric("🏆 Maior Gasto", formatar_valor(df['valor'].max()), delta=f"Min: {formatar_valor(df['valor'].min())}")
        st.markdown("---")
#===============================================================================================================
        # Gráficos Top Fornecedores agrupados
        st.subheader("Fornecedores - Top 10 e Participação (%)")
        col_graf1, col_graf2 = st.columns(2)
        with col_graf1:
            top_fornecedores = df.groupby('fornecedor_limpo')['valor'].sum().sort_values(ascending=False).head(10)
            fig_bar = px.bar(
                x=top_fornecedores.values,
                y=top_fornecedores.index,
                orientation='h',
                labels={'x': 'Valor (R$)', 'y': 'Fornecedor'},
                title='Top 10 por Valor',
                color=top_fornecedores.values,
                color_continuous_scale='sunset'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        with col_graf2:
            fig_pie = px.pie(
                names=top_fornecedores.head(5).index,
                values=top_fornecedores.head(5).values,
                color_discrete_sequence=px.colors.sequential.RdBu,
                title='Top 5 - Participação (%)'
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("---")
#===============================================================================================================
        # Gráfico Gastos por Mês
        st.subheader("📅 Gastos por Mês")
        df['mes_ano'] = df['data'].dt.to_period('M').astype(str)
        gastos_mes = df.groupby('mes_ano')['valor'].sum().reset_index()
        fig_mes = px.line(
            gastos_mes,
            x='mes_ano',
            y='valor',
            labels={'mes_ano': 'Mês/Ano', 'valor': 'Total Gasto (R$)'},
            title='Gastos por Mês',
            markers=True,
            color_discrete_sequence=['#FF5733']
        )
        st.plotly_chart(fig_mes, use_container_width=True)
        st.markdown("---")
#===============================================================================================================
        st.subheader("🖥️  DataFrame Completo")
        st.dataframe(df)
    else:
        st.error("❌ Erro ao carregar os dados de liquidações.")
        st.markdown("---")
        st.subheader("🖥️  DataFrame Completo")
        df = pd.DataFrame(columns=['data', 'fornecedor_limpo', 'valor', 'tipo_licitacao', 'empenho'])
        st.dataframe(df)
#===============================================================================================================
with abas[1]:
    st.header("🏢 Análise de Fornecedores")
    st.info("Adicione aqui a análise de fornecedores e carregamento de dados específicos.")
    # Exemplo: st.dataframe(df_fornecedores)

with abas[2]:
    st.header("📁 Outros Dados")
    st.info("Adicione aqui outras análises e dados legais.")
    # Exemplo: st.dataframe(df_outros)
#===============================================================================================================
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; color:gray; font-size:0.9em;">
        Fiscal de Maringá &copy; 2025 &mdash; Desenvolvido por João Paulo<br>
        Dados públicos da Prefeitura de Maringá | Projeto sem fins lucrativos
    </div>
    """,
    unsafe_allow_html=True
)