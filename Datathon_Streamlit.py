#Import libraries
import streamlit as st
import pandas as pd
import json
import gdown #Use gdown to Access the File

# #Imports JSON files from my personal Google Drive (files made public)
# # Replace with your own FILE_ID
# file_Prospects  = '1sh88eHjyIp0wXtcRIFozgN064VGOOxEs'
# file_Applicants = '17859ae_Ki5CImI9-1lhJ335GMDW0f2Qr'
file_Vagas      = '1YKM7yDTzjHJVf82l2RxEx-SuLxFxCxrl'

# # Download the JSON files
# gdown.download(f'https://drive.google.com/uc?export=download&id={file_Prospects}', 'prospects.json', quiet=False)
# gdown.download(f'https://drive.google.com/uc?export=download&id={file_Applicants}', 'applicants.json', quiet=False)
gdown.download(f'https://drive.google.com/uc?export=download&id={file_Vagas}', 'vagas.json', quiet=False)

# #Load the JSON File into Python
# with open('prospects.json', 'r') as prospects_file:
#     data_Prospects = json.load(prospects_file)

# with open('applicants.json', 'r') as applicants_file:
#     data_Applicants = json.load(applicants_file)

with open('vagas.json', 'r') as vagas_file:
    data_Vagas = json.load(vagas_file)



# # Convert the JSON so that each prospect candidate is represented as a separate row in the DataFrame
# # -----------------------
# #prospects.JSON file
# # -----------------------
# records = []

# for prof_id, profile_info in data_Prospects.items():
#     titulo = profile_info.get("titulo")
#     modalidade = profile_info.get("modalidade")

#     for prospect in profile_info.get("prospects", []):
#         record = {
#             "id_prospect": prof_id,
#             "titulo": titulo,
#             "modalidade": modalidade,
#             "nome_candidato": prospect.get("nome"),
#             "codigo_candidato": prospect.get("codigo"),
#             "situacao_candidado": prospect.get("situacao_candidado"),
#             "data_candidatura": prospect.get("data_candidatura"),
#             "ultima_atualizacao": prospect.get("ultima_atualizacao"),
#             "comentario": prospect.get("comentario"),
#             "recrutador": prospect.get("recrutador")
#         }
#         records.append(record)

# # Convert to DataFrame
# df_Prospects = pd.DataFrame(records)


# # -----------------------
# #applicants.JSON file
# # -----------------------
# records = []

# for prof_id, profile_info in data_Applicants.items():
#     record = {
#         "id_applicant": prof_id
#     }

#     # Flatten sections
#     for section_name, section_data in profile_info.items():
#         if isinstance(section_data, dict):
#             for key, value in section_data.items():
#                 record[f"{section_name}__{key}"] = value
#         else:
#             # Just in case any sections are not dicts (e.g., cv_pt or cv_en directly under profile)
#             record[section_name] = section_data

#     records.append(record)

# # Convert to DataFrame
# df_Applicants = pd.DataFrame(records)


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
df_Vagas = pd.DataFrame(records)

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
# Título e introdução
# -----------------------------
st.set_page_config(page_title="Sistema de Recomendação de Talentos por Vaga", layout="wide")

st.title("Dashboard de Matching entre Vagas e Candidatos")
st.subheader("Selecione uma vaga para visualizar os candidatos mais compatíveis")

# -----------------------------
# Sidebar - Filtros e seleção
# -----------------------------
st.sidebar.header("Selecione a vaga desejada")

#Lista de meses existentes na base de vagas
# Criar nova coluna no formato 'MMM.yyyy'
df_Vagas['mes_ano'] = df_Vagas['informacoes_basicas__data_requicisao'].dt.strftime('%b.%Y')

# Converter para datetime temporariamente (formato: %b.%Y → 'Apr.2019')
lista_meses_ordenada = sorted(
    df_Vagas['mes_ano'].dropna().unique(),
    key=lambda x: pd.to_datetime(x, format='%b.%Y')
)
mth_selecionado = st.sidebar.selectbox("Título da vaga:", lista_meses_ordenada)

# Exemplo de seleção de vaga - Lista de vagas
lista_vagas = sorted(df_Vagas['informacoes_basicas__titulo_vaga'])
vaga_selecionada = st.sidebar.selectbox("Mês.Ano:", lista_vagas)

#Ações quando o um valor no filtro for selecionado
# Filtrar o dataframe pelo mês selecionado
df_filtrado = df_Vagas[df_Vagas['mes_ano'] == mth_selecionado]

# Gerar lista de vagas com base no mês selecionado
lista_vagas = sorted(df_filtrado['informacoes_basicas__titulo_vaga'].dropna().unique())

# Selecionar a vaga
vaga_selecionada = st.sidebar.selectbox("Título da vaga:", lista_vagas)

# -----------------------------
# Exibição dos candidatos compatíveis
# -----------------------------
st.markdown(f"### Candidatos compatíveis com a vaga: {vaga_selecionada}")
st.dataframe(df_Vagas, use_container_width=True)


# st.set_page_config(
#     page_title = 'PAINEL DE AÇÕES DA B3',
#     layout = 'wide'
# )

# st.header("**PAINEL DE PREÇO DE FECHAMENTO E DIVIDENDOS DE AÇÕES DA B3**")

# st.markdown("**PAINEL DE PREÇO DE FECHAMENTO E DIVIDENDfffOS DE AÇÕES DA B3**")


# ticker = st.text_input('Digite o ticket da ação', 'BBAS3')
# empresa = yf.Ticker(f"{ticker}.SA")

# tickerDF = empresa.history( period  = "1d",
#                             start   = "2019-01-01",
#                             end     = "2025-01-20"
# )

# col1, col2, col3 = st.columns([1, 1, 1])

# with col1:
#     st.write(f"**Empresa:**  {empresa.info['longName']}")
# with col2:
#     st.write(f"**Mercado:** R$ {empresa.info['industry']}")
# with col3:
#     st.write(f"**Preço Atual:** R$ {empresa.info['currentPrice']}")

# st.line_chart(tickerDF.Close)
# st.bar_chart(tickerDF.Dividends)