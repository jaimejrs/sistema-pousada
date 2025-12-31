import streamlit as st
import streamlit_authenticator as stauth
import os
import copy
from models import Session
from utils import local_css
from views import dashboard, mapa, reservas, clientes, quartos

# CONFIG
st.set_page_config(page_title="Recanto da Lagoa", layout="wide", page_icon="🏖️")
local_css()

# AUTENTICAÇÃO
try:
    config = st.secrets["auth"]
except:
    st.error("Erro: arquivo secrets.toml não encontrado ou mal configurado.")
    st.stop()

credentials_copy = copy.deepcopy(config['credentials'])

authenticator = stauth.Authenticate(
    credentials_copy, 
    config['name'], 
    config['key'], 
    config['expiry_days']
)


authenticator.login(location='main')

authentication_status = st.session_state.get("authentication_status")
name = st.session_state.get("name")
username = st.session_state.get("username")

if authentication_status is False:
    st.error('Usuário ou senha incorretos')
    st.stop()
elif authentication_status is None:
    st.warning('Por favor, faça login.')
    st.stop()

# BARRA LATERAL
with st.sidebar:
    st.write(f"Olá, **{name}**!")
    
    authenticator.logout('Sair', 'sidebar')
    
    st.divider()
    if os.path.exists("logo.png"): 
        st.image("logo.png", width="stretch")
    else: 
        st.title("Recanto da Lagoa")

st.sidebar.title("Navegação")
menu = st.sidebar.radio(
    "Ir para:",
    ["Painel de Controle", "Mapa de Ocupação", "Nova Reserva", "Gerenciar Reservas", "Clientes", "Quartos"],
    label_visibility="collapsed"
)

# VIEWS
session = Session()

if menu == "Painel de Controle":
    dashboard.render(session)

elif menu == "Mapa de Ocupação":
    mapa.render(session)

elif menu == "Nova Reserva":
    reservas.render_nova(session)

elif menu == "Gerenciar Reservas":
    reservas.render_gerenciar(session)

elif menu == "Clientes":
    clientes.render(session)

elif menu == "Quartos":
    quartos.render(session)

session.close()