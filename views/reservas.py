import streamlit as st
from datetime import date, datetime, time
from models import Reserva, Cliente, Quarto
from sqlalchemy import or_
from utils import formatar_cpf_visual, arredondar_dias, verificar_disponibilidade, TABELA_PRECOS

def render_nova(session):
    st.header("Criar Nova Reserva")
    clientes = session.query(Cliente).all()
    quartos = session.query(Quarto).all()
    
    if not clientes or not quartos:
        st.warning("Necessário cadastrar Clientes e Quartos primeiro.")
    else:
        cli_dict = {f"{c.nome} | {formatar_cpf_visual(c.cpf)}": c.id for c in clientes}
        qto_dict = {f"Quarto {q.numero} ({q.tipo})": q.id for q in quartos}
        c_key = st.selectbox("Cliente", list(cli_dict.keys()))
        q_key = st.selectbox("Quarto", list(qto_dict.keys()))
        c1, c2 = st.columns(2)
        d_in = c1.date_input("Entrada", min_value=date.today())
        t_in = c1.time_input("Hora Entrada", value=time(14, 0))
        d_out = c2.date_input("Saída", min_value=d_in)
        t_out = c2.time_input("Hora Saída", value=time(12, 0))
        dt_in = datetime.combine(d_in, t_in)
        dt_out = datetime.combine(d_out, t_out)
        
        st.markdown("---")
        tarifa_nome = st.selectbox("Tabela", list(TABELA_PRECOS.keys()))
        valor_base = TABELA_PRECOS[tarifa_nome]
        dias_cobranca = arredondar_dias(dt_in, dt_out, tarifa_nome)
        sugerido = valor_base if "Pernoite" in tarifa_nome else valor_base * dias_cobranca
        st.caption(f"Sugerido: R$ {sugerido}")
        valor_final = st.number_input("Valor Final (R$)", value=float(sugerido), step=10.0)
        
        if st.button("Confirmar", type="primary"):
            if dt_out <= dt_in: st.error("Datas inválidas")
            else:
                q_id = qto_dict[q_key]
                ok, conflito = verificar_disponibilidade(q_id, dt_in, dt_out, session)
                if not ok: st.error("Quarto ocupado!")
                else:
                    try:
                        res = Reserva(cliente_id=cli_dict[c_key], quarto_id=q_id, data_checkin=dt_in, data_checkout=dt_out, tipo_tarifa=tarifa_nome, valor_total=valor_final, status="Ativa")
                        session.add(res)
                        session.commit()
                        st.success("Sucesso!")
                    except Exception as e: st.error(str(e))

def render_gerenciar(session):
    st.header("Gerenciamento")
    termo = st.text_input("Buscar (Nome, CPF ou Quarto)")
    query = session.query(Reserva).join(Cliente).join(Quarto)
    if termo:
        query = query.filter(or_(Cliente.nome.ilike(f"%{termo}%"), Cliente.cpf.ilike(f"%{termo}%"), Quarto.numero.ilike(f"%{termo}%")))
    reservas = query.order_by(Reserva.data_checkin.desc()).all()
    
    if reservas:
        res_dict = {f"#{r.id} | {r.cliente.nome}": r.id for r in reservas}
        sel_key = st.selectbox("Selecione", list(res_dict.keys()))
        res_obj = session.query(Reserva).get(res_dict[sel_key])
        
        st.markdown("---")
        c1, c2 = st.columns(2)
        d_in = c1.date_input("Entrada", value=res_obj.data_checkin.date())
        t_in = c1.time_input("Hr Entrada", value=res_obj.data_checkin.time())
        d_out = c2.date_input("Saída", value=res_obj.data_checkout.date())
        t_out = c2.time_input("Hr Saída", value=res_obj.data_checkout.time())
        new_dt_in = datetime.combine(d_in, t_in)
        new_dt_out = datetime.combine(d_out, t_out)
        
        dias_novo = arredondar_dias(new_dt_in, new_dt_out, res_obj.tipo_tarifa)
        tarifa_base = TABELA_PRECOS.get(res_obj.tipo_tarifa, 0)
        sug = tarifa_base if "Pernoite" in res_obj.tipo_tarifa else dias_novo * tarifa_base
        if sug != res_obj.valor_total: st.warning(f"Novo valor sugerido: R$ {sug}")
        
        new_val = st.number_input("Valor", value=float(sug))
        new_status = st.selectbox("Status", ["Ativa", "Finalizada", "Cancelada"], index=["Ativa", "Finalizada", "Cancelada"].index(res_obj.status))
        
        if st.button("Salvar Alterações", type="primary"):
            if new_status == 'Ativa':
                ok, conflito = verificar_disponibilidade(res_obj.quarto_id, new_dt_in, new_dt_out, session, ignorar_reserva_id=res_obj.id)
                if not ok: 
                    st.error("Conflito de agenda!")
                    st.stop()
            res_obj.data_checkin = new_dt_in
            res_obj.data_checkout = new_dt_out
            res_obj.status = new_status
            res_obj.valor_total = new_val
            session.commit()
            st.success("Atualizado!")
            st.rerun()