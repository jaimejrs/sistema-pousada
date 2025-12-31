import streamlit as st
import pandas as pd
import io
from datetime import date, datetime, time, timedelta
from models import Reserva, Quarto, Cliente
from utils import arredondar_dias

def render(session):
    st.title("Calendário de Reservas")
    
    c_date, c_metrics = st.columns([1, 3])
    with c_date:
        data_inicio_grid = st.date_input("Visualizar a partir de:", value=date.today())
    
    st.subheader(f"Reservas (30 dias a partir de {data_inicio_grid.strftime('%d/%m')})")
    
    datas_colunas = [data_inicio_grid + timedelta(days=i) for i in range(30)]
    quartos_db = session.query(Quarto).all()
    
    data_fim_grid = datas_colunas[-1]
    reservas_db = session.query(Reserva).filter(
        Reserva.status == 'Ativa',
        Reserva.data_checkout >= datetime.combine(data_inicio_grid, time.min),
        Reserva.data_checkin <= datetime.combine(data_fim_grid, time.max)
    ).all()
    
    if not quartos_db:
        st.warning("Cadastre quartos para visualizar o mapa.")
    else:
        mapa_dados = []
        for q in quartos_db:
            linha = {"Quarto": f"{q.numero} ({q.tipo})"}
            for d in datas_colunas:
                ocupado_por = None
                dt_referencia = datetime.combine(d, time(14, 0)) 
                for r in reservas_db:
                    if r.quarto_id == q.id:
                        if r.data_checkin <= dt_referencia < r.data_checkout:
                            ocupado_por = r.cliente.nome.split()[0]
                            break
                linha[d.strftime('%d/%m')] = ocupado_por if ocupado_por else ""
            mapa_dados.append(linha)
            
        df_mapa = pd.DataFrame(mapa_dados)
        df_mapa.set_index("Quarto", inplace=True)
        
        def colorir_ocupados(val):
            return 'background-color: #1B76CF; color: white; font-weight: bold' if val else ''

        st.dataframe(df_mapa.style.applymap(colorir_ocupados), width="stretch", height=400)
        st.caption("Células azuis indicam quarto ocupado.")

    st.markdown("---")
    st.subheader("Lista de Reservas")
    
    query = session.query(Reserva).statement
    df = pd.read_sql(query, session.bind)
    
    if not df.empty:
        cli_df = pd.read_sql(session.query(Cliente).statement, session.bind)
        qto_df = pd.read_sql(session.query(Quarto).statement, session.bind)
        
        df = df.merge(cli_df, left_on='cliente_id', right_on='id', suffixes=('', '_cli'))
        df = df.merge(qto_df, left_on='quarto_id', right_on='id', suffixes=('', '_qto'))
        
        df['data_checkin'] = pd.to_datetime(df['data_checkin'])
        df['data_checkout'] = pd.to_datetime(df['data_checkout'])
        
        df['Entrada'] = df['data_checkin'].dt.strftime('%d/%m/%Y %H:%M')
        df['Saída'] = df['data_checkout'].dt.strftime('%d/%m/%Y %H:%M')
        
        def calc_row(row):
            return arredondar_dias(row['data_checkin'], row['data_checkout'], row['tipo_tarifa'])
            
        df['Dias'] = df.apply(calc_row, axis=1)
        
        view = df[['id', 'status', 'Entrada', 'Saída', 'Dias', 'nome', 'numero', 'tipo_tarifa', 'valor_total']]
        view.columns = ['ID', 'Status', 'Entrada', 'Saída', 'Dias', 'Cliente', 'Quarto', 'Tarifa', 'Total (R$)']
        
        col_table, col_btn = st.columns([5, 1])
        with col_table:
             st.dataframe(view, width="stretch")
        
        with col_btn:
            st.write("Exportar:")
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                view.to_excel(writer, sheet_name='Reservas', index=False)
            st.download_button(label="📥 Baixar Excel", data=buffer, file_name=f"reservas_{date.today()}.xlsx", mime="application/vnd.ms-excel")