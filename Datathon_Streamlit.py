#Import libraries
import pandas as pd
import json
import gdown #Use gdown to Access the File
import streamlit as st


#Imports JSON files from my personal Google Drive (files made public)
# Replace with your own FILE_ID
file_Prospects  = '1sh88eHjyIp0wXtcRIFozgN064VGOOxEs'
file_Applicants = '17859ae_Ki5CImI9-1lhJ335GMDW0f2Qr'
file_Vagas      = '1YKM7yDTzjHJVf82l2RxEx-SuLxFxCxrl'

# Download the JSON files
gdown.download(f'https://drive.google.com/uc?export=download&id={file_Prospects}', 'prospects.json', quiet=False)
gdown.download(f'https://drive.google.com/uc?export=download&id={file_Applicants}', 'applicants.json', quiet=False)
gdown.download(f'https://drive.google.com/uc?export=download&id={file_Vagas}', 'vagas.json', quiet=False)

#Load the JSON File into Python
with open('prospects.json', 'r') as prospects_file:
    data_Prospects = json.load(prospects_file)

with open('applicants.json', 'r') as applicants_file:
    data_Applicants = json.load(applicants_file)

with open('vagas.json', 'r') as vagas_file:
    data_Vagas = json.load(vagas_file)



# Convert the JSON so that each prospect candidate is represented as a separate row in the DataFrame
# -----------------------
#prospects.JSON file
# -----------------------
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
df_Prospects = pd.DataFrame(records)


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
df_Applicants = pd.DataFrame(records)


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

# Show the DataFrame
df_Prospects.head()





# st.set_page_config(
#     page_title = 'PAINEL DE AÇÕES DA B3',
#     layout = 'wide'
# )

# st.header("**PAINEL DE PREÇO DE FECHAMENTO E DIVIDENDOS DE AÇÕES DA B3**")

# # st.markdown("**PAINEL DE PREÇO DE FECHAMENTO E DIVIDENDfffOS DE AÇÕES DA B3**")


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
