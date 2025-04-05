import streamlit as st
from datetime import datetime
import math
import uuid
import sqlite3

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
st.set_page_config(page_title="Finanças com Dados", page_icon="💰")
st.title("Finanças com Dados 💰")

with st.form("simulador_form"):
    despesa_mensal = st.number_input("Despesa Mensal", min_value=0.0)
    tipo_trabalho = st.selectbox("Tipo de Trabalho", ["CLT", "Autônomo"])
    n_dependentes = st.number_input("Número de Dependentes", min_value=0, step=1)
    valor_atual = st.number_input("Valor Atual Investido", min_value=0.0)
    meta = st.number_input("Meta Financeira (R$)", min_value=0.0)
    prazo_anos = st.number_input("Prazo (anos)", min_value=0.0)
    aporte_atual = st.number_input("Aporte Mensal Atual", min_value=0.0)
    taxa_retorno_anual = st.number_input("Taxa de Retorno Anual (%)", min_value=0.0)
    enviar = st.form_submit_button("Simular")

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

    st.success("Simulação realizada com sucesso!")
    st.metric("Reserva de Emergência Ideal (R$)", f"{reserva_ideal:.2f}")
    st.metric("Aporte Mensal Necessário (R$)", f"{aporte_necessario:.2f}")
    st.metric("Tempo Estimado para Meta (anos)", f"{tempo_estimado:.1f}")