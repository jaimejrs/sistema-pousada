# 🏖️ Recanto da Lagoa | Sistema de Gestão Hoteleira

![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.52-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon.tech-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Status](https://img.shields.io/badge/Status-Portfolio_Demo-success?style=for-the-badge)

> **Uma solução de gerenciamento de propriedades (PMS) que centraliza reservas, gestão de ocupação e Business Intelligence em uma interface nuvem moderna.**

---

## 🌐 Acesso à Demonstração

A aplicação está implantada em ambiente de produção e disponível para testes.

🔗 **[Acesse o Sistema Online](https://recantodalagoa.streamlit.app/)**

### 🔑 Credenciais de Visitante
Para explorar as funcionalidades utilize o seguinte acesso:
* **Usuário:** `teste`
* **Senha:** `123`

---

## 🎯 Conceito e Objetivo

O Projeto foi desenvolvido para atacar o problema comum da descentralização de dados (uso de planilhas isoladas e cadernos) de pequenos empreendimentos, propondo um sistema unificado que garante integridade relacional e acesso remoto.

O foco do desenvolvimento foi equilibrar uma **Experiência de Usuário (UX)** fluida capaz de prevenir conflitos de agenda (overbooking) e fornecer métricas financeiras em tempo real.

---

## ✨ Funcionalidades Estratégicas

| Módulo | Descrição Técnica |
| :--- | :--- |
| **📊 BI & Analytics** | Dashboard executivo com cálculo automático de KPIs como Taxa de Ocupação, RevPAR (Receita por Quarto Disponível) e Ticket Médio. |
| **🗺️ Visualização Espacial** | Mapa de Ocupação interativo que traduz o estado do banco de dados em uma interface visual color-coded (Livre/Ocupado/Manutenção). |
| **📅 Engine de Reservas** | Motor de agendamento com validação lógica de intervalos de datas (`daterange overlaps`), impedindo conflitos de alocação no backend. |
| **👥 CRM de Hóspedes** | Gestão centralizada de clientes com histórico de estadias persistente. |

---

## 🛠️ Arquitetura e Decisões Técnicas

O sistema foi construído sobre uma arquitetura modular, separando a lógica de negócios da camada de apresentação.

### 1. Backend
Utilizou-se o **PostgreSQL** (hospedado via Neon.tech) como banco de dados relacional para garantir a consistência ACID das transações. A comunicação é feita via **SQLAlchemy 2.0**, utilizando ORM para abstração de queries e prevenção de injeção de SQL.

### 2. Frontend
A interface foi construída com **Streamlit**, aproveitando seu ciclo de execução reativo para atualizações instantâneas de estado. Foram desenvolvidos componentes visuais customizados via CSS injetado para adequação à identidade visual.

---

## ⚠️ Atenção (Dados Fictícios)

Este projeto é uma **demonstração de portfólio**.

* **Mock Data:** Todos os nomes de hóspedes, valores financeiros e registros de reservas presentes na aplicação foram gerados artificialmente para fins de simulação.
* **Privacidade:** A aplicação não utiliza dados reais de nenhuma entidade ou pessoa. As credenciais fornecidas são públicas e exclusivas para o ambiente de teste.

---

<div align="center">

**Desenvolvido por Jaime Teixeira**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/jaimejrs)
[![GitHub](https://img.shields.io/badge/GitHub-Profile-black?style=for-the-badge&logo=github&logoColor=white)](github.com/jaimejrs)

</div>
