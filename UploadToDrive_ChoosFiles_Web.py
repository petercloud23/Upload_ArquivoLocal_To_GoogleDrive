import os
import io
import requests
import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# --- Escopos ---
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# --- Autenticação ---
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

# --- Listar pastas recursivamente ---
def listar_pastas_recursivo(service, parent_id=None, caminho_atual="Raiz"):
    pastas = {}
    page_token = None
    while True:
        resposta = service.files().list(
            q=f"mimeType='application/vnd.google-apps.folder' and trashed=false" +
              (f" and '{parent_id}' in parents" if parent_id else ""),
            spaces='drive',
            fields="nextPageToken, files(id, name)",
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            pageSize=200,
            pageToken=page_token
        ).execute()
        for file in resposta.get('files', []):
            caminho_completo = f"{caminho_atual} / {file['name']}"
            pastas[caminho_completo] = file['id']
            # Recursivamente lista subpastas
            subpastas = listar_pastas_recursivo(service, parent_id=file['id'], caminho_atual=caminho_completo)
            pastas.update(subpastas)
        page_token = resposta.get('nextPageToken', None)
        if page_token is None:
            break
    return pastas

# --- Upload ---
def upload_para_drive(service, arquivo, pasta_id=None):
    file_metadata = {'name': arquivo.name}
    if pasta_id:
        file_metadata['parents'] = [pasta_id]
    media = MediaIoBaseUpload(io.BytesIO(arquivo.getbuffer()), mimetype=arquivo.type)
    file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    return file

# --- Desconectar conta ---
def desconectar_conta():
    if os.path.exists("token.json"):
        try:
            creds = Credentials.from_authorized_user_file("token.json")
            revoke = requests.post(
                'https://oauth2.googleapis.com/revoke',
                params={'token': creds.token},
                headers={'content-type': 'application/x-www-form-urlencoded'}
            )
            os.remove("token.json")
            if revoke.status_code == 200:
                st.success("✅ Conta desconectada com sucesso!")
            else:
                st.warning("⚠️ Falha ao revogar token, mas desconexão local concluída.")
        except Exception as e:
            st.error(f"Erro ao desconectar: {e}")
    else:
        st.info("Nenhuma conta autenticada no momento.")

# --- Interface ---
st.set_page_config(page_title="Upload para Google Drive", page_icon="☁️")
st.title("☁️ Upload para Google Drive")

st.markdown("""
Envie arquivos diretamente para seu **Google Drive**.  
Escolha a pasta de destino usando o menu abaixo.  
Agora você pode ver todas as subpastas com seus caminhos completos.
""")

# Autenticar e listar pastas
try:
    service = autenticar_google()
    pastas_dict = {'Raiz do Drive': None}  # Sempre incluir raiz
    pastas_dict.update(listar_pastas_recursivo(service))
except Exception as e:
    st.error(f"Erro na autenticação ou listagem de pastas: {e}")
    st.stop()

# Menu suspenso com caminhos completos das pastas
if pastas_dict:
    pasta_selecionada_nome = st.selectbox(
        "📁 Selecione a pasta de destino:",
        options=list(pastas_dict.keys())
    )
    pasta_id = pastas_dict.get(pasta_selecionada_nome, None)
else:
    st.warning("Nenhuma pasta encontrada além da raiz.")
    pasta_selecionada_nome = "Raiz do Drive"
    pasta_id = None

# Upload de arquivo
arquivo = st.file_uploader("Escolha um arquivo para enviar", type=None)

if st.button("📤 Enviar para Drive"):
    if arquivo:
        if pasta_id is not None or pasta_selecionada_nome == "Raiz do Drive":
            try:
                file_info = upload_para_drive(service, arquivo, pasta_id)
                st.success(f"✅ Arquivo enviado com sucesso!\n\n📁 ID: `{file_info.get('id')}`")
                st.markdown(f"[🔗 Abrir no Google Drive]({file_info.get('webViewLink')})")
            except Exception as e:
                st.error(f"Ocorreu um erro: {e}")
        else:
            st.warning("Selecione uma pasta válida para enviar o arquivo.")
    else:
        st.warning("Por favor, selecione um arquivo primeiro.")

# Linha divisória
st.divider()

# Botão de desconexão
if st.button("🔒 Desconectar conta Google"):
    desconectar_conta()

st.markdown("---")
st.caption("Desenvolvido com ❤️ em Python + Streamlit + Google Drive API")
