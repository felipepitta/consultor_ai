from datetime import datetime
from typing import Literal
import math
import uuid
import sqlite3
import streamlit as st
import plotly.graph_objects as go
import locale

locale.setlocale(locale.LC_ALL, '')

# --- Banco de dados SQLite ---
conn = sqlite3.connect("usuarios.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id TEXT PRIMARY KEY,
    timestamp TEXT,
    despesa_mensal REAL,
    tipo_trabalho TEXT,
    n_dependentes INTEGER,
    valor_atual REAL,
    meta REAL,
    prazo_anos REAL,
    aporte_atual REAL,
    taxa_retorno_anual REAL,
    reserva_ideal REAL,
    aporte_necessario REAL,
    tempo_estimado REAL
)
''')
conn.commit()

# --- Funções de cálculo ---
def calcular_reserva(despesa_mensal, tipo_trabalho, n_dependentes):
    meses_reserva = 6 if tipo_trabalho.lower() == 'clt' else 12
    reserva = (despesa_mensal * meses_reserva) + (n_dependentes * 1000)
    return reserva

def calcular_aporte_necessario(meta, prazo_anos, taxa_retorno_anual):
    i = taxa_retorno_anual / 12 / 100
    n = prazo_anos * 12
    if n == 0:
        return 0
    if i == 0:
        return meta / n
    aporte = meta * i / ((1 + i) ** n - 1)
    return aporte

def calcular_tempo_para_meta(valor_atual, aporte_mensal, taxa_retorno_anual, meta):
    i = taxa_retorno_anual / 12 / 100
    saldo = valor_atual
    meses = 0
    while saldo < meta and meses < 1000:
        saldo = saldo * (1 + i) + aporte_mensal
        meses += 1
    anos = meses / 12
    return round(anos, 1)

# --- Interface Streamlit ---
st.set_page_config(page_title="Consultor-AI", page_icon="🤖💰")
st.title("Consultor-AI 🤖💰")

st.markdown("""
Este é o seu consultor financeiro inteligente. Preencha os dados abaixo para obter sua reserva de emergência ideal,
quanto você precisa aportar mensalmente e por quanto tempo para atingir sua meta financeira.
""")

with st.form("simulador_form"):
    despesa_mensal = st.number_input("Despesa Mensal", min_value=0.0, help="Inclua todas as suas despesas mensais como aluguel, comida, transporte, etc.")
    tipo_trabalho = st.selectbox("Tipo de Trabalho", ["CLT", "Autônomo"], help="Se você trabalha registrado, selecione CLT. Caso contrário, escolha Autônomo.")
    n_dependentes = st.number_input("Número de Dependentes", min_value=0, step=1, help="Quantas pessoas dependem financeiramente de você?")
    valor_atual = st.number_input("Valor Atual Investido", min_value=0.0, help="Quanto você já tem investido para sua meta?")
    meta = st.number_input("Meta Financeira (R$)", min_value=0.0, help="Qual o valor final que você deseja atingir?")
    prazo_anos = st.number_input("Prazo (anos)", min_value=0.0, help="Em quantos anos você deseja atingir sua meta?")
    aporte_atual = st.number_input("Aporte Mensal Atual", min_value=0.0, help="Quanto você já consegue investir por mês atualmente?")
    taxa_retorno_anual = st.number_input("Taxa de Retorno Anual (%)", min_value=0.0, help="Qual a taxa de retorno anual esperada dos seus investimentos?")

    col1, col2 = st.columns(2)
    enviar = col1.form_submit_button("Simular")
    limpar = col2.form_submit_button("Limpar")

if limpar:
    st.experimental_rerun()

if enviar:
    reserva_ideal = calcular_reserva(despesa_mensal, tipo_trabalho, n_dependentes)
    aporte_necessario = calcular_aporte_necessario(meta, prazo_anos, taxa_retorno_anual)
    tempo_estimado = calcular_tempo_para_meta(valor_atual, aporte_atual, taxa_retorno_anual, meta)

    id_user = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO usuarios VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        id_user, timestamp,
        despesa_mensal, tipo_trabalho, n_dependentes,
        valor_atual, meta, prazo_anos,
        aporte_atual, taxa_retorno_anual,
        reserva_ideal, aporte_necessario, tempo_estimado
    ))
    conn.commit()

    st.success("✅ Simulação realizada com sucesso!")

    col1, col2, col3 = st.columns(3)
    col1.metric("Reserva de Emergência Ideal", f"R$ {reserva_ideal:,.2f}")
    col2.metric("Aporte Mensal Necessário", f"R$ {aporte_necessario:,.2f}")
    col3.metric("Tempo Estimado (anos)", f"{tempo_estimado:.1f}")

    progresso = min(valor_atual / meta, 1.0)

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor_atual,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Progresso da Meta Financeira"},
        gauge={
            'axis': {'range': [None, meta]},
            'bar': {'color': "green"},
            'steps': [
                {'range': [0, meta * 0.5], 'color': "lightgray"},
                {'range': [meta * 0.5, meta], 'color': "gray"},
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': meta
            }
        }
    ))

    st.plotly_chart(fig, use_container_width=True)