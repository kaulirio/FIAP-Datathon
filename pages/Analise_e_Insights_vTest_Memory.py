#Import libraries
import streamlit as st
import pandas as pd
import json
import gdown #Use gdown to Access the File
import re
import unicodedata
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from collections import Counter
import gc
import os
import plotly.express as px
import matplotlib.pyplot as plt
import locale
import psutil
# locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')  # for macOS/Linux
#locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')  # for Windows



# Check whether the JSON files have been loaded into the python application
#if 'df_Vagas' not in globals() and 'df_Applicants' not in the streamlit session():
if 'df_Vagas' not in st.session_state or 'df_Applicants' not in st.session_state or 'df_Prospects' not in st.session_state:
    # #Imports JSON files from my personal Google Drive (files made public)
    # # Replace with your own FILE_ID
    file_Prospects  = '1sh88eHjyIp0wXtcRIFozgN064VGOOxEs'
    file_Applicants = '17859ae_Ki5CImI9-1lhJ335GMDW0f2Qr'
    file_Vagas      = '1YKM7yDTzjHJVf82l2RxEx-SuLxFxCxrl'

    # # Download the JSON files
    gdown.download(f'https://drive.google.com/uc?export=download&id={file_Prospects}', 'prospects.json', quiet=False)
    gdown.download(f'https://drive.google.com/uc?export=download&id={file_Applicants}', 'applicants.json', quiet=False)
    gdown.download(f'https://drive.google.com/uc?export=download&id={file_Vagas}', 'vagas.json', quiet=False)

    # #Load the JSON File into Python
    with open('prospects.json', 'r') as prospects_file:
        data_Prospects = json.load(prospects_file)

    with open('applicants.json', 'r') as applicants_file:
        data_Applicants = json.load(applicants_file)

    with open('vagas.json', 'r') as vagas_file:
        data_Vagas = json.load(vagas_file)


    # # Convert the JSON so that each prospect candidate is represented as a separate row in the DataFrame
    # # -----------------------
    # #prospects.JSON file
    # # -----------------------
    records = []

    for prof_id, profile_info in data_Prospects.items():
        titulo = profile_info.get("titulo")
        modalidade = profile_info.get("modalidade")

        for prospect in profile_info.get("prospects", []):
            record = {
                "id_prospect": prof_id,
                "titulo": titulo,
                "modalidade": modalidade,
                "nome_candidato": prospect.get("nome"),
                "codigo_candidato": prospect.get("codigo"),
                "situacao_candidado": prospect.get("situacao_candidado"),
                "data_candidatura": prospect.get("data_candidatura"),
                "ultima_atualizacao": prospect.get("ultima_atualizacao"),
                "comentario": prospect.get("comentario"),
                "recrutador": prospect.get("recrutador")
            }
            records.append(record)

    # Convert to DataFrame
    # df_Prospects = pd.DataFrame(records)
    st.session_state.df_Prospects = pd.DataFrame(records)


    # -----------------------
    #applicants.JSON file
    # -----------------------
    records = []

    for prof_id, profile_info in data_Applicants.items():
        record = {
            "id_applicant": prof_id
        }

        # Flatten sections
        for section_name, section_data in profile_info.items():
            if isinstance(section_data, dict):
                for key, value in section_data.items():
                    record[f"{section_name}__{key}"] = value
            else:
                # Just in case any sections are not dicts (e.g., cv_pt or cv_en directly under profile)
                record[section_name] = section_data

        records.append(record)

    # Convert to DataFrame
    #df_Applicants = pd.DataFrame(records)
    st.session_state.df_Applicants = pd.DataFrame(records)

    #test

    # -----------------------
    #vagas.JSON file
    # -----------------------
    records = []

    for prof_id, profile_info in data_Vagas.items():
        record = {
            "id_vaga": prof_id
        }

        # Flatten sections
        for section_name, section_data in profile_info.items():
            if isinstance(section_data, dict):
                for key, value in section_data.items():
                    record[f"{section_name}__{key}"] = value
            else:
                record[section_name] = section_data

        records.append(record)

    # Convert to DataFrame
    #df_Vagas = pd.DataFrame(records)
    st.session_state.df_Vagas = pd.DataFrame(records)


    #Release memory used
    # Clear variables
    del data_Vagas
    del data_Applicants
    del data_Prospects
    # Force garbage collection
    gc.collect()

    
df_Vagas = st.session_state.df_Vagas
df_Applicants = st.session_state.df_Applicants
df_Prospects = st.session_state.df_Prospects


# Count NaN or empty values per column
empty_counts = (df_Vagas.isnull() | (df_Vagas == '')).sum()

# Identify columns with more than 13.000 missing/empty values
cols_to_drop = empty_counts[empty_counts > 13000].index

# Drop them from the DataFrame
df_Vagas.drop(columns=cols_to_drop, inplace=True)

# Convert date fields to datetime
df_Vagas['informacoes_basicas__data_requicisao'] = pd.to_datetime(df_Vagas['informacoes_basicas__data_requicisao'], format='%d-%m-%Y', errors='coerce' )
df_Vagas['informacoes_basicas__data_inicial'] = pd.to_datetime(df_Vagas['informacoes_basicas__data_inicial'], format='%d-%m-%Y', errors='coerce' )
df_Vagas['informacoes_basicas__data_final'] = pd.to_datetime(df_Vagas['informacoes_basicas__data_final'], format='%d-%m-%Y', errors='coerce' )





#Montando a estrutura do dashboard
# -----------------------------
# Título e introdução - HEADER
# -----------------------------
st.set_page_config(page_title="Análises e Insights Estratégicos", layout="wide")

# # Header with logo and title
# col1, col2 = st.columns([1, 6])

# with col1:
#     st.image("https://decision.pt/wp-content/uploads/2019/12/Logo_Decision.png", width=200)

# with col2:
#     st.markdown("## Sistema de Recomendação de Talentos")
#     st.markdown("### Selecione uma vaga na aba filtros para visualizar os candidatos mais compatíveis")


memory = psutil.virtual_memory()

st.write("**Uso de Memória RAM**")
st.write(f"Total: {memory.total / 1e6:.2f} MB")
st.write(f"Disponível: {memory.available / 1e6:.2f} MB")
st.write(f"Em uso: {memory.used / 1e6:.2f} MB")
st.write(f"Percentual usado: {memory.percent}%")

st.markdown("""
          <style>

        
        .stElementContainer{
            /* This is a comment 
background-color: rgb(73,162,252);   */
            }    
        .stSidebar{
           /* background-color: rgb(206,224,254);
            rgb(73, 162, 252)   */

        }
    </style>      
            
<div style="display: flex; align-items: center; background-color:white; color:black;">
    <img src="https://decision.pt/wp-content/uploads/2019/12/Logo_Decision.png" width="150" style="margin-right: 20px;background-color:white">
    <div>
        <h1 style="margin-bottom: 5px;font-color=black;">Análises e Insights Estratégicos</h1>
        <h3 style="margin-top: 0;">Visualizações interativas para apoiar a tomada de decisão baseada em dados</h3>
    </div>
</div>
""", unsafe_allow_html=True)
    

# st.title("DashVagaoard de Matching entre Vagas e Candidatos")
# st.subheader("Selecione uma vaga na aba filtros para visualizar os candidatos mais compatíveis")

# -----------------------------
# Filtros e seleção - SIDEBAR
# -----------------------------
st.sidebar.header("Filtros para Prospecções")

#Prepare df_Prospects 
# Convert to datetime
df_Prospects['data_candidatura'] = pd.to_datetime(df_Prospects['data_candidatura'], format='%d-%m-%Y')

# Create month-year column
df_Prospects['mes_ano'] = df_Prospects['data_candidatura'].dt.to_period('M').astype(str)

# Create a column for year
df_Prospects['ano'] = df_Prospects['data_candidatura'].dt.year

# Ensure 'mes_ano' is in datetime format (first day of month)
df_Prospects['mes_ano_dt'] = pd.to_datetime(df_Prospects['mes_ano'], format='%Y-%m')

df_Prospects['mes_ano'] = df_Prospects['data_candidatura'].dt.strftime('%b.%Y')  # e.g. "Jan.2024"

# Get sorted unique month-year values
meses_unicos = sorted(df_Prospects['mes_ano'].dropna().unique(), key=lambda x: pd.to_datetime(x, format='%b.%Y'))

# Select range using Streamlit slider or multiselect
mes_inicio, mes_fim = st.sidebar.select_slider(
    "Selecione o intervalo de meses:",
    options=meses_unicos,
    value=(meses_unicos[-12], meses_unicos[-1])
)

# Convert selection back to datetime for filtering
inicio = pd.to_datetime(mes_inicio, format='%b.%Y')
fim = pd.to_datetime(mes_fim, format='%b.%Y') + pd.offsets.MonthEnd(0)

# Filter the DataFrame by Period
df_filtered = df_Prospects[(df_Prospects['data_candidatura'] >= inicio) & (df_Prospects['data_candidatura'] <= fim)]

# Gerar lista de recrutadores com base no mês selecionado
lista_recrutadores = sorted(df_filtered['recrutador'].dropna().unique())
# Inserir a opção "Todos" no topo
lista_recrutadores.insert(0, "Todos")
# TITULO VAGA FILTER "Recrutador" Filtro lateral
recrutador_selecionado = st.sidebar.selectbox("Recrutador (a):", lista_recrutadores)

# Aplicar filtro somente se "Todos" não for selecionado
if recrutador_selecionado != "Todos":
    df_filtered = df_filtered[df_filtered['recrutador'] == recrutador_selecionado]










st.sidebar.header("Filtros para Vagas")
#Lista de meses existentes na base de vagas

df_Vagas['mes_ano'] = df_Vagas['informacoes_basicas__data_requicisao'].dt.strftime('%b.%Y')  # e.g. "Jan.2024"

# Get sorted unique month-year values
meses_unicos_vagas = sorted(df_Vagas['mes_ano'].dropna().unique(), key=lambda x: pd.to_datetime(x, format='%b.%Y'))

# Select range using Streamlit slider or multiselect
mes_inicio_vagas, mes_fim_vagas = st.sidebar.select_slider(
    "Selecione o intervalo de meses:",
    options=meses_unicos_vagas,
    value=(meses_unicos_vagas[-12], meses_unicos_vagas[-1])
)

# Convert selection back to datetime for filtering
inicio_vagas = pd.to_datetime(mes_inicio_vagas, format='%b.%Y')
fim_vagas = pd.to_datetime(mes_fim_vagas, format='%b.%Y') + pd.offsets.MonthEnd(0)

# Filter the DataFrame by Period
df_Vagas = df_Vagas[(df_Vagas['informacoes_basicas__data_requicisao'] >= inicio_vagas) & (df_Vagas['informacoes_basicas__data_requicisao'] <= fim_vagas)]

# Gerar lista de Clientes/Solicitantes com base no mês selecionado
lista_clientes = sorted(df_Vagas['informacoes_basicas__solicitante_cliente'].dropna().unique())
# Inserir a opção "Todos" no topo
lista_clientes.insert(0, "Todos")
# TITULO VAGA FILTER "Clientes/Solicitantes" Filtro lateral
clientes_selecionado = st.sidebar.selectbox("Cliente/Solitante:", lista_clientes)

# Aplicar filtro somente se "Todos" não for selecionado
if clientes_selecionado != "Todos":
    df_Vagas = df_Vagas[df_Vagas['informacoes_basicas__solicitante_cliente'] == clientes_selecionado]















# -----------------------------
# Corpo do dashboard - BODY
# -----------------------------

col1, col2 = st.columns(2)
with col1:
    # local = st.selectbox("Local candidato:", lista_local_candidatos)     
    # Dashboard Body's title
    st.markdown("")
    st.markdown(f"#### Distribuição de Candidatos por Situação - {inicio.strftime('%b.%Y')} até {fim.strftime('%b.%Y')}")


    # Group by candidate status
    status_counts = df_filtered['situacao_candidado'].value_counts().reset_index()
    status_counts.columns = ['Situação Candidato', 'Total']

    fig = px.pie(
        status_counts,
        names='Situação Candidato',
        values='Total',
        # title='Distribuição de Situação dos Candidatos',
        hole=0.4  # optional: for donut-style
    )

    # Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)
with col2:
    # nivel_academico = st.selectbox("Nível Acadênico:", lista_nivel_academico)    
    # Convert date fields to datetime
    df_Applicants['infos_basicas__data_criacao'] = pd.to_datetime(df_Applicants['infos_basicas__data_criacao'], format='%d-%m-%Y %H:%M:%S', errors='coerce' )
    df_Applicants['infos_basicas__data_atualizacao'] = pd.to_datetime(df_Applicants['infos_basicas__data_atualizacao'], format='%d-%m-%Y %H:%M:%S', errors='coerce' )
    df_Applicants['informacoes_pessoais__data_aceite'] = pd.to_datetime(df_Applicants['informacoes_pessoais__data_aceite'], format='%d-%m-%Y %H:%M:%S', errors='coerce' )
    df_Applicants['informacoes_pessoais__data_nascimento'] = pd.to_datetime(df_Applicants['informacoes_pessoais__data_nascimento'], format='%d-%m-%Y %H:%M:%S', errors='coerce' )
    
    


    df_Applicants['mes_ano'] = df_Applicants['infos_basicas__data_criacao'].dt.strftime('%b.%Y')  # e.g. "Jan.2024"

    # Get sorted unique month-year values
    meses_unicos_applicants = sorted(df_Applicants['mes_ano'].dropna().unique(), key=lambda x: pd.to_datetime(x, format='%b.%Y'))


    inicio_applicants = pd.to_datetime("2024-04-01")
    fim_applicants = pd.to_datetime("2025-03-01")
    # st.markdown(f"###### ")
    st.markdown(
    "<h4 style='text-align: center; margin-top:16px;'>Principais Palavras-Chave em Perfis</h4>",
    unsafe_allow_html=True
    )


    # Select range using Streamlit slider or multiselect
    mes_inicio_applicants, mes_fim_applicants = st.select_slider(
        "Selecione o intervalo de meses:",
        options=meses_unicos_applicants,
        value=(meses_unicos_applicants[-12], meses_unicos_applicants[-1])
    )

    # Convert selection back to datetime for filtering
    inicio_applicants = pd.to_datetime(mes_inicio_applicants, format='%b.%Y')
    fim_applicants = pd.to_datetime(mes_fim_applicants, format='%b.%Y') + pd.offsets.MonthEnd(0)

    # Filter the DataFrame by Period
    df_Applicants = df_Applicants[(df_Applicants['infos_basicas__data_criacao'] >= inicio_applicants) & (df_Applicants['infos_basicas__data_criacao'] <= fim_applicants)]













    
    
    
    
    
    # Prepare the text
    objetivos = df_Applicants['infos_basicas__objetivo_profissional'].dropna().astype(str)

    # Clean and filter
    all_text = ' '.join(objetivos).lower()
    all_text = re.sub(r'[^\w\s]', '', all_text)
    words = [word for word in all_text.split() if len(word) >= 3]
    word_counts = Counter(words)
    most_common_words = word_counts.most_common(20)

    # Create DataFrame
    common_df = pd.DataFrame(most_common_words, columns=['word', 'count'])



    # Create bar chart using Plotly
    fig = px.bar(
        common_df,
        x='word',
        y='count',
        # title='Principais Palavras-Chave em Perfis',
        labels={'word': 'Palavra-Chave', 'count': 'Frequência'}
    )

    # Reduce margin above chart
    fig.update_layout(
        margin=dict(t=0),
        height=360

    )

    # Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)







# THIRD CHART - VAGAS
# Convert date fields to datetime
df_Vagas['informacoes_basicas__data_requicisao'] = pd.to_datetime(df_Vagas['informacoes_basicas__data_requicisao'], format='%d-%m-%Y', errors='coerce' )
df_Vagas['informacoes_basicas__data_inicial'] = pd.to_datetime(df_Vagas['informacoes_basicas__data_inicial'], format='%d-%m-%Y', errors='coerce' )
df_Vagas['informacoes_basicas__data_final'] = pd.to_datetime(df_Vagas['informacoes_basicas__data_final'], format='%d-%m-%Y', errors='coerce' )

# Convert to datetime
df_Vagas['data_requicisao_dt'] = pd.to_datetime(
    df_Vagas['informacoes_basicas__data_requicisao'],
    errors='coerce'
)

# Create a Month-Year column
df_Vagas['mes_ano'] = df_Vagas['data_requicisao_dt'].dt.to_period('M').astype(str)

# Filter for the last 12 months (Removed)
df_last_12 = df_Vagas

# Group and count
vagas_last_12 = df_last_12.groupby('mes_ano')['id_vaga'].count().sort_index()


# st.markdown(f"#### Número de Vagas nos periodo de - {inicio.strftime('%b.%Y')} até {fim.strftime('%b.%Y')}")
st.markdown(
    f"<h4 style='text-align: center;'>Número de Vagas no período de {inicio_vagas.strftime('%b.%Y')} até {fim_vagas.strftime('%b.%Y')}</h4>",
    unsafe_allow_html=True
)



# Convert to DataFrame
df_vagas = vagas_last_12.reset_index()
df_vagas.columns = ['mes_ano', 'quantidade']

# Ensure 'mes_ano' is datetime
df_vagas['mes_ano'] = pd.to_datetime(df_vagas['mes_ano'])

# Format to 'MMM.yyyy' in Portuguese if locale is supported
df_vagas['mes_ano_str'] = df_vagas['mes_ano'].dt.strftime('%b.%Y')

# Ensure correct order
df_vagas['mes_ano_str'] = pd.Categorical(df_vagas['mes_ano_str'], categories=df_vagas['mes_ano_str'], ordered=True)

# Create bar chart
fig = px.bar(
    df_vagas,
    x='mes_ano_str',
    y='quantidade',
    text='quantidade',
    labels={'mes_ano_str': '', 'quantidade': ''}
)

# Show all x-axis ticks
fig.update_layout(
    xaxis=dict(
        tickmode='array',
        tickvals=df_vagas['mes_ano_str'],
        ticktext=df_vagas['mes_ano_str']
    ),
    xaxis_tickangle=-45,
    height=400,
    margin=dict(t=50, b=100)
)

fig.update_traces(textposition='outside')

# Show in Streamlit
st.plotly_chart(fig, use_container_width=True)