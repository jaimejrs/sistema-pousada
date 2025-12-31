import streamlit as st
from models import Quarto

def render(session):
    st.title("Gestão de Quartos")
    tab1, tab2 = st.tabs(["Cadastrar", "Gerenciar"])
    
    # ABA 1: CADASTRAR
    with tab1:
        with st.form("fq"):
            n = st.text_input("Número")
            t = st.selectbox("Tipo", ["Normal", "Especial"])
            if st.form_submit_button("Salvar"):
                try:
                    session.add(Quarto(numero=n, tipo=t))
                    session.commit()
                    st.success("Salvo com sucesso!")
                except: st.error("Erro: Número já existe?")
    
    # ABA 2: GERENCIAR
    with tab2:
        quartos = session.query(Quarto).all()
        if quartos:
            q_dict = {f"Quarto {q.numero} ({q.tipo})": q.id for q in quartos}
            escolha_q = st.selectbox("Selecione o quarto para editar:", list(q_dict.keys()))
            q_obj = session.query(Quarto).get(q_dict[escolha_q])
            
            st.markdown("---")
            with st.form("edit_q_form"):
                novo_num = st.text_input("Número", value=q_obj.numero)
                novo_tipo = st.selectbox("Tipo", ["Normal", "Especial"], index=["Normal", "Especial"].index(q_obj.tipo))
                
                col_save, col_del = st.columns([1, 4])
                
                salvou = col_save.form_submit_button("💾 Salvar")
                if salvou:
                    q_obj.numero = novo_num
                    q_obj.tipo = novo_tipo
                    try:
                        session.commit()
                        st.success("Quarto atualizado!")
                        st.rerun()
                    except: st.error("Erro ao atualizar.")
            
            st.write("")
            if st.button("Excluir Quarto"):
                try:
                    session.delete(q_obj)
                    session.commit()
                    st.success("Quarto excluído!")
                    st.rerun()
                except:
                    st.error("Não é possível excluir este quarto pois existem reservas vinculadas a ele.")