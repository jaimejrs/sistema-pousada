import streamlit as st
import pandas as pd
from models import Cliente, Reserva
from sqlalchemy import or_
from utils import limpar_cpf, formatar_cpf_visual

def render(session):
    st.title("Gestão de Clientes")
    tab1, tab2, tab3 = st.tabs(["Novo", "Buscar e Editar", "Histórico"])
    
    # ABA 1: NOVO
    with tab1:
        with st.form("fc"):
            n = st.text_input("Nome")
            c = st.text_input("CPF")
            e = st.text_input("Email")
            t = st.text_input("Tel")
            if st.form_submit_button("Salvar"):
                try:
                    session.add(Cliente(nome=n, cpf=limpar_cpf(c), email=e, telefone=t))
                    session.commit()
                    st.success("Salvo com sucesso!")
                except: st.error("Erro ao salvar (CPF duplicado?)")
    
    # ABA 2: EDITAR
    with tab2:
        termo = st.text_input("Buscar Cliente (Nome ou CPF)", key="busca_edit")
        q = session.query(Cliente)
        if termo: 
            q = q.filter(or_(Cliente.nome.ilike(f"%{termo}%"), Cliente.cpf.ilike(f"%{termo}%")))
        clis = q.limit(50).all()
        
        if clis:
            c_dict = {f"{c.nome} | CPF: {formatar_cpf_visual(c.cpf)}": c.id for c in clis}
            key_selecionada = st.selectbox("Selecione para editar", list(c_dict.keys()), key="sel_edit")
            cid = c_dict[key_selecionada]
            c_obj = session.query(Cliente).get(cid)
            
            with st.form("edit_c"):
                n = st.text_input("Nome", value=c_obj.nome)
                e = st.text_input("Email", value=c_obj.email or "")
                t = st.text_input("Tel", value=c_obj.telefone or "")
                if st.form_submit_button("Atualizar"):
                    c_obj.nome = n
                    c_obj.email = e
                    c_obj.telefone = t
                    session.commit()
                    st.success("Atualizado!")
                    st.rerun()
            
            if st.button("Excluir Cliente"):
                try:
                    session.delete(c_obj)
                    session.commit()
                    st.rerun()
                except: st.error("Não é possível excluir cliente com reservas existentes.")
        else:
            if termo: st.warning("Nenhum cliente encontrado.")

    # ABA 3: HISTÓRICO
    with tab3:
        st.subheader("Histórico do Hóspede")
        termo_hist = st.text_input("Buscar Cliente (Nome ou CPF)", key="busca_hist")
        
        candidatos = []
        if termo_hist:
            candidatos = session.query(Cliente).filter(
                or_(Cliente.nome.ilike(f"%{termo_hist}%"), Cliente.cpf.ilike(f"%{termo_hist}%"))
            ).limit(20).all()
        
        if candidatos:
            dict_candidatos = {f"{c.nome} | CPF: {formatar_cpf_visual(c.cpf)}": c.id for c in candidatos}
            escolha = st.selectbox("Selecione o Cliente:", list(dict_candidatos.keys()), key="sel_hist_final")
            
            cid_final = dict_candidatos[escolha]
            res = session.query(Reserva).filter(Reserva.cliente_id == cid_final).order_by(Reserva.data_checkin.desc()).all()
            
            if res:
                reservas_validas = [r for r in res if r.status != 'Cancelada']
                gasto_total = sum([r.valor_total for r in reservas_validas])
                qtd_reservas = len(reservas_validas)
                ticket_medio = gasto_total / qtd_reservas if qtd_reservas > 0 else 0
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Gasto Total", f"R$ {gasto_total:,.2f}")
                c2.metric("Reservas Concluídas", qtd_reservas)
                c3.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
                
                df_h = pd.DataFrame([{ 
                    "Checkin": r.data_checkin.strftime('%d/%m/%Y'), 
                    "Checkout": r.data_checkout.strftime('%d/%m/%Y'),
                    "Valor": f"R$ {r.valor_total:.2f}", 
                    "Status": r.status
                } for r in res])
                
                def color_status(val):
                    color = '#1B76CF' if val == 'Ativa' or val == 'Finalizada' else 'red'
                    return f'color: {color}; font-weight: bold'
                
                st.dataframe(df_h.style.applymap(color_status, subset=['Status']), width="stretch")
            else:
                st.info("Este cliente não possui histórico de reservas.")
        elif termo_hist:
            st.warning("Nenhum cliente encontrado.")