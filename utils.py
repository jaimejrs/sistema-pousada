import streamlit as st
import re
from sqlalchemy import and_
from models import Reserva

# ESTILIZAÇÃO CSS
def local_css():
    st.markdown(
        """
        <style>
        h1, h2, h3, h4, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #000028 !important; }
        div.stButton > button:first-child { background-color: #1B76CF; color: white; border-radius: 8px; border: none; font-weight: bold; padding: 0.5rem 1rem; }
        div.stButton > button:hover { background-color: #145a9e; border: none; color: white; }
        [data-testid="stMetricValue"] { color: #1B76CF !important; }
        [data-testid="stMetricLabel"] { color: #000028 !important; }
        [data-testid="stSidebar"] > div:first-child { padding-top: 1rem; }
        </style>
        """,
        unsafe_allow_html=True
    )

# PREÇOS
TABELA_PRECOS = {"Pernoite": 150.00, "Diária Casal": 200.00, "Diária Triplo": 250.00}

# FUNÇOES AUXILIARES
def limpar_cpf(cpf):
    if not cpf: return ""
    return re.sub(r'\D', '', cpf)

def formatar_cpf_visual(cpf_limpo):
    if not cpf_limpo or len(cpf_limpo) != 11:
        return cpf_limpo
    return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"

def arredondar_dias(dt_in, dt_out, tipo_tarifa):
    if "Pernoite" in tipo_tarifa: return 0.5
    delta_seconds = (dt_out - dt_in).total_seconds()
    dias_reais = delta_seconds / 86400
    dias_arredondados = round(dias_reais * 2) / 2
    return max(0.5, dias_arredondados)

def verificar_disponibilidade(quarto_id, dt_in, dt_out, session, ignorar_reserva_id=None):
    query = session.query(Reserva).filter(
        and_(
            Reserva.quarto_id == quarto_id,
            Reserva.status == 'Ativa',
            Reserva.data_checkin < dt_out,
            Reserva.data_checkout > dt_in
        )
    )
    if ignorar_reserva_id: query = query.filter(Reserva.id != ignorar_reserva_id)
    conflito = query.first()
    return (False, conflito) if conflito else (True, None)