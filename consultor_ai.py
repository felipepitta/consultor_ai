import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Consultor AI", layout="wide")
st.title("🤖 Consultor de Investimentos com IA")
st.markdown("""
Este app ajuda você a definir uma estratégia de reserva de emergência e de investimentos com base na sua realidade financeira.
""")

# Inicializa os valores dos campos na sessão
campos = {
    'renda_mensal': 0.0,
    'despesa_mensal': 0.0,
    'valor_reserva_desejada': 0.0,
    'aporte_mensal': 0.0,
    'perfil': 'Moderado'
}

for campo in campos:
    if campo not in st.session_state:
        st.session_state[campo] = campos[campo]

# Layout
col1, col2 = st.columns(2)

with col1:
    st.session_state['renda_mensal'] = st.number_input("Renda Mensal (R$)", value=st.session_state['renda_mensal'], step=100.0, format="%.2f")
    st.session_state['despesa_mensal'] = st.number_input("Despesas Mensais (R$)", value=st.session_state['despesa_mensal'], step=100.0, format="%.2f")
    st.session_state['valor_reserva_desejada'] = st.number_input("Reserva de Emergência Desejada (R$)", value=st.session_state['valor_reserva_desejada'], step=100.0, format="%.2f")

with col2:
    st.session_state['aporte_mensal'] = st.number_input("Aporte Mensal (R$)", value=st.session_state['aporte_mensal'], step=100.0, format="%.2f")
    st.session_state['perfil'] = st.selectbox("Perfil de Investidor", ["Conservador", "Moderado", "Arrojado"], index=["Conservador", "Moderado", "Arrojado"].index(st.session_state['perfil']))

# Botão de limpar campos
if st.button("🧹 Limpar Campos"):
    for campo in campos:
        st.session_state[campo] = campos[campo]
    st.experimental_rerun()

# Função de cálculo de evolução do capital
@st.cache_data
def calcular_evolucao(valor_inicial, aporte_mensal, taxa_juros, anos):
    meses = anos * 12
    valores = []
    montante = valor_inicial
    for i in range(meses):
        montante *= (1 + taxa_juros / 12)
        montante += aporte_mensal
        valores.append(montante)
    return valores

# Cálculo e gráficos
if st.session_state['aporte_mensal'] > 0:
    retornos = [0.05, 0.07, 0.09, 0.12]  # 5%, 7%, 9%, 12%
    prazos = [("Curto Prazo (3 anos)", 3), ("Médio Prazo (5 anos)", 5), ("Longo Prazo (10 anos)", 10)]

    fig = go.Figure()

    for taxa in retornos:
        for nome_prazo, anos in prazos:
            valores = calcular_evolucao(0, st.session_state['aporte_mensal'], taxa, anos)
            fig.add_trace(go.Scatter(y=valores, mode='lines', name=f"{int(taxa*100)}% a.a. - {nome_prazo}"))

    fig.update_layout(title="Evolução do Patrimônio Acumulado", xaxis_title="Meses", yaxis_title="Valor Acumulado (R$)", height=600)
    st.plotly_chart(fig, use_container_width=True)

    st.success("📊 Escolha uma curva de evolução conforme seu objetivo de prazo e expectativa de retorno!")

# Em breve: Sugestão de carteira com IA
st.markdown("""
### 🤖 Recomendação Inteligente (em desenvolvimento)
Futuramente, este app usará inteligência artificial para sugerir:
- Alocação ideal de ativos (Renda fixa, ações, fundos, ETFs, etc.)
- Diversificação com base no perfil de risco
- Rebalanceamento e acompanhamento periódico
""")