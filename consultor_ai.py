import streamlit as st
import plotly.graph_objects as go
from huggingface_hub import InferenceClient
import os

# Configurar chave da Hugging Face (você pode armazenar em st.secrets ou variáveis de ambiente)
hf_key = st.secrets["HUGGINGFACEHUB_API_TOKEN"] if "HUGGINGFACEHUB_API_TOKEN" in st.secrets else os.getenv("HUGGINGFACEHUB_API_TOKEN")
client = InferenceClient(model="mistralai/Mistral-7B-Instruct-v0.1", token=hf_key)

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
retornos = [0.05, 0.075, 0.10]  # 5%, 7.5%, 10%
prazos = [3, 5, 10, 15, 20, 25, 30]  # anos

# Simulações com juros compostos corretamente aplicados
resultados = {}
for r in retornos:
    retorno_mensal = r / 12
    valores = []
    for t in range(1, max(prazos)+1):
        n = t * 12
        if retorno_mensal == 0:
            total = aporte_mensal * n
        else:
            total = aporte_mensal * ((1 + retorno_mensal) ** n - 1) / retorno_mensal
        valores.append(round(total, 2))
    resultados[f"{int(r*1000)/10}% a.a"] = valores

# Gráfico de linhas suavizadas
st.subheader("📈 Projeções de Crescimento Patrimonial")
fig = go.Figure()
anos = list(range(1, max(prazos)+1))
for label, values in resultados.items():
    fig.add_trace(go.Scatter(x=anos, y=values, mode='lines+markers', name=label, line_shape='spline'))
fig.update_layout(xaxis_title="Prazo (anos)", yaxis_title="R$ Acumulado", height=500)
st.plotly_chart(fig)

# Mostrar reserva de emergência
st.subheader("🔒 Reserva de Emergência Ideal")
st.write(f"Com seus custos mensais, sua reserva de emergência ideal é de **R$ {reserva_emergencia:,.2f}**")

# Sugestão personalizada via IA (HuggingFace)
if st.button("🔍 Obter sugestão personalizada da IA"):
    with st.spinner("Analisando..."):
        prompt = (
            f"Seja um consultor financeiro brasileiro especialista em construir patrimonio. Com base nos seguintes dados do cliente, dê sugestões de como ele pode diversificar seus investimentos, quais ativos pode considerar (renda fixa, ações, fundos, etc) e quais estratégias pode seguir para alcançar seu objetivo. Crie um portfolio recomendado, calculando o percentual de cada classe de ativos\n\n"
            f"Renda mensal: R$ {renda_mensal}\n"
            f"Custo mensal: R$ {custo_mensal}\n"
            f"Aporte mensal: R$ {aporte_mensal}\n"
            f"Reserva de emergência: R$ {reserva_emergencia:.2f}\n"
            f"Perfil de investidor: {perfil}\n"
            f"Objetivo financeiro: {objetivo}"
        )
        try:
            resposta = client.text_generation(prompt, max_new_tokens=300)
            resposta_formatada = resposta.strip()
            if "Sugestão:" in resposta_formatada:
                resposta_formatada = resposta_formatada.split("Sugestão:", 1)[-1].strip()
                resposta_formatada = "Sugestão: " + resposta_formatada
            st.subheader("🤖 Sugestão da IA")
            st.write(resposta_formatada)
        except Exception as e:
            st.error(f"Erro ao consultar a IA: {e}")

# Botão limpar
if st.button("🧹 Limpar"):
    st.cache_data.clear()
    st.experimental_rerun()