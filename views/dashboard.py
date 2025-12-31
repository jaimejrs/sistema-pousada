import streamlit as st
import pandas as pd
import altair as alt
from datetime import date, datetime, timedelta
from models import Reserva, Cliente, Quarto

def render(session):
    st.title("Painel de Controle")
    
    df_res = pd.read_sql(session.query(Reserva).statement, session.bind)
    df_cli = pd.read_sql(session.query(Cliente).statement, session.bind)
    
    if df_res.empty:
        st.info("Sem dados suficientes para gerar gráficos.")
        return

    df_res['data_checkin'] = pd.to_datetime(df_res['data_checkin'])
    df_res['data_checkout'] = pd.to_datetime(df_res['data_checkout'])
    df_res['mes_ano'] = df_res['data_checkin'].dt.strftime('%Y-%m') 
    df_res['ano'] = df_res['data_checkin'].dt.year
    df_res['mes'] = df_res['data_checkin'].dt.month
    
    # KPIS
    hoje = datetime.now()
    inicio_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    ativas_hoje = len(df_res[df_res['status'] == 'Ativa'])
    canceladas_mes = len(df_res[
        (df_res['status'] == 'Cancelada') & 
        (df_res['data_checkin'] >= inicio_mes)
    ])
    total_clientes = len(df_cli)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Reservas Ativas", ativas_hoje, delta_color="normal")
    c2.metric("Cancelamentos (Mês)", canceladas_mes, delta_color="inverse")
    c3.metric("Clientes Cadastrados", total_clientes)
    
    receita_mes = df_res[
        (df_res['status'] != 'Cancelada') & 
        (df_res['data_checkin'] >= inicio_mes) &
        (df_res['data_checkin'] < (inicio_mes + timedelta(days=32)).replace(day=1))
    ]['valor_total'].sum()
    c4.metric("Faturamento (Mês)", f"R$ {receita_mes:,.2f}")
    
    st.markdown("---")
    
    # GRÁFICOS
    
    # 1. EVOLUÇÃO DE RESERVAS
    st.subheader("Evolução de Reservas")
    
    dados_mensais = df_res.groupby('mes_ano').size().reset_index(name='qtd')
    media_reservas = dados_mensais['qtd'].mean()
    dados_mensais['media'] = media_reservas
    
    base = alt.Chart(dados_mensais).encode(x=alt.X('mes_ano', title='Mês'))
    barras = base.mark_bar(color='#1B76CF').encode(
        y=alt.Y('qtd', title='Qtd Reservas'),
        tooltip=[alt.Tooltip('mes_ano', title='Mês'), alt.Tooltip('qtd', title='Reservas')]
    )
    linha_media = base.mark_rule(color='red', strokeDash=[5, 5]).encode(
        y='media', 
        size=alt.value(2),
        tooltip=[alt.Tooltip('media', title='Média Histórica', format=',.1f')]
    )
    
    grafico_1 = (barras + linha_media).properties(height=300).interactive()
    st.altair_chart(grafico_1, width="stretch")
    
    col_g2, col_g3 = st.columns(2)
    
    with col_g2:
        st.subheader("Dias com Ocupação no Mês")
        
        df_res['range_datas'] = df_res.apply(
            lambda x: pd.date_range(x['data_checkin'], x['data_checkout'] - pd.Timedelta(days=1)).to_list() 
            if x['data_checkout'] > x['data_checkin'] else [x['data_checkin']], 
            axis=1
        )
        
        df_exploded = df_res.explode('range_datas')
        df_exploded['mes_referencia'] = df_exploded['range_datas'].dt.strftime('%Y-%m')
        
        dias_unicos_mes = df_exploded.groupby('mes_referencia')['range_datas'].nunique().reset_index(name='dias_ativos')
        
        grafico_2 = alt.Chart(dias_unicos_mes).mark_bar(color='#1B76CF').encode(
            x=alt.X('mes_referencia', title='Mês'),
            y=alt.Y('dias_ativos', title='Dias com Hóspedes (Máx 31)'),
            tooltip=[
                alt.Tooltip('mes_referencia', title='Mês'), 
                alt.Tooltip('dias_ativos', title='Dias Ativos')
            ]
        ).properties(height=300)
        st.altair_chart(grafico_2, width="stretch")
        st.caption("Indica em quantos dias do mês a pousada teve pelo menos 1 hóspede.")

    with col_g3:
        st.subheader("Comparativo de Volume (Ano x Ano)")
        
        ano_atual = date.today().year
        ano_anterior = ano_atual - 1
        
        df_comp = df_res[df_res['ano'].isin([ano_anterior, ano_atual])].copy()
        comp_data = df_comp.groupby(['ano', 'mes'])['id'].count().reset_index(name='qtd_reservas')
        
        grafico_3 = alt.Chart(comp_data).mark_line(point=True).encode(
            x=alt.X('mes:O', title='Mês', axis=alt.Axis(labelExpr="datum.value")), 
            y=alt.Y('qtd_reservas', title='Quantidade de Reservas'),
            color=alt.Color('ano:N', title='Ano'),
            tooltip=[
                alt.Tooltip('ano', title='Ano'), 
                alt.Tooltip('mes', title='Mês'), 
                alt.Tooltip('qtd_reservas', title='Reservas')
            ]
        ).properties(height=300)
        st.altair_chart(grafico_3, width="stretch")

    # 4. GRÁFICO FINAL
    st.subheader("Fluxo de Check-ins por Dia da Semana")
    
    mapa_dias = {
        'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta', 
        'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
    }
    df_res['dia_semana_ing'] = df_res['data_checkin'].dt.day_name()
    df_res['dia_semana'] = df_res['dia_semana_ing'].map(mapa_dias)
    
    ordem_dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    
    fluxo_semana = df_res.groupby('dia_semana')['id'].count().reset_index(name='total_checkins')
    
    grafico_4 = alt.Chart(fluxo_semana).mark_bar().encode(
        x=alt.X('dia_semana', title='Dia da Semana', sort=ordem_dias),
        y=alt.Y('total_checkins', title='Total de Check-ins'),
        color=alt.Color('total_checkins', legend=None, scale=alt.Scale(scheme='blues')),
        tooltip=[alt.Tooltip('dia_semana', title='Dia'), alt.Tooltip('total_checkins', title='Check-ins')]
    ).properties(height=300)
    
    st.altair_chart(grafico_4, width="stretch")
    st.caption("Identifique os dias de maior movimento para planejar limpeza e recepção.")