import os
import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def autenticar_google():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

def upload_para_drive(service, arquivo):
    file_metadata = {'name': arquivo.name}
    media = MediaIoBaseUpload(io.BytesIO(arquivo.getbuffer()), mimetype=arquivo.type)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

# Interface Streamlit
st.title("☁️ Upload para Google Drive")

arquivo = st.file_uploader("Escolha um arquivo para enviar", type=None)
if st.button("Enviar para Drive"):
    if arquivo:
        try:
            service = autenticar_google()
            file_id = upload_para_drive(service, arquivo)
            st.success(f"✅ Arquivo enviado com sucesso!\nID: {file_id}")
        except Exception as e:
            st.error(f"Ocorreu um erro: {e}")
    else:
        st.warning("Por favor, selecione um arquivo primeiro.")
