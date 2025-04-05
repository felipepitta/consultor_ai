import streamlit as st
import plotly.graph_objects as go
import openai
import os

# Configurar a API Key da OpenAI (lembre de usar secrets no deploy)
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Consultor de Investimentos IA", layout="centered")
st.title("🤖 Consultor Inteligente de Investimentos")

st.markdown("""
Este assistente te ajuda a entender quanto investir por mês e como seu patrimônio pode evoluir com o tempo. 
Além disso, a inteligência artificial te dá sugestões com base no seu perfil e objetivos.
""")

st.subheader("Preencha suas informações abaixo:")

renda_mensal = st.number_input("Renda mensal (R$)", min_value=0.0, format="%.2f", help="Sua renda mensal líquida.")
custo_mensal = st.number_input("Custo mensal de vida (R$)", min_value=0.0, format="%.2f", help="Gastos mensais médios com moradia, alimentação, transporte, etc.")
aporte_mensal = st.number_input("Aporte mensal (R$)", min_value=0.0, format="%.2f", help="Quanto pretende investir por mês.")
perfil = st.selectbox("Perfil de investidor", ["Conservador", "Moderado", "Arrojado"], help="Seu apetite ao risco: Conservador, Moderado ou Arrojado.")
objetivo = st.text_area("Objetivo financeiro", help="Ex: comprar uma casa, aposentadoria, liberdade financeira, etc.")

# Cálculo da reserva de emergência automaticamente
reserva_emergencia = custo_mensal * 6

# Parâmetros de retorno e prazos
retornos = [0.05, 0.075, 0.10]
prazos = [3, 5, 10]

# Simulações
resultados = {}
for r in retornos:
    for t in prazos:
        total = 0
        for i in range(t * 12):
            total = (total + aporte_mensal) * (1 + r / 12)
        resultados[f"Retorno {int(r*100)}% a.a - {t} anos"] = round(total, 2)

# Gráfico
st.subheader("📈 Simulações de crescimento do investimento")
fig = go.Figure()
fig.add_trace(go.Bar(x=list(resultados.keys()), y=list(resultados.values()), name="Valor Futuro"))
fig.update_layout(xaxis_title="Cenário", yaxis_title="R$ Acumulado", height=500)
st.plotly_chart(fig)

# Mostrar reserva de emergência
st.subheader("🔒 Reserva de Emergência Ideal")
st.write(f"Com seus custos mensais, sua reserva de emergência ideal é de **R$ {reserva_emergencia:,.2f}**")

# Requisição à OpenAI com sugestões
if st.button("🔍 Obter sugestão personalizada da IA"):
    with st.spinner("Consultando IA..."):
        prompt = f"""
Sou um consultor financeiro. Aqui estão os dados do cliente:
- Renda mensal: R$ {renda_mensal}
- Custo mensal: R$ {custo_mensal}
- Aporte mensal: R$ {aporte_mensal}
- Reserva de emergência: R$ {reserva_emergencia}
- Perfil: {perfil}
- Objetivo: {objetivo}

Com base nesses dados, dê sugestões de como ele pode diversificar seus investimentos, quais ativos pode considerar (renda fixa, ações, fundos, etc), e quais estratégias pode seguir para alcançar seu objetivo.
"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "Você é um consultor financeiro."},
                         {"role": "user", "content": prompt}]
            )
            st.subheader("🤖 Sugestão da IA")
            st.write(response.choices[0].message.content)
        except Exception as e:
            st.error(f"Erro ao consultar a IA: {e}")

# Botão limpar
if st.button("🧹 Limpar"):
    st.cache_data.clear()
    st.experimental_rerun()