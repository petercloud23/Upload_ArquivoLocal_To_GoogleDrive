import os.path
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# Se modificar esses escopos, delete o arquivo token.json.
# Os escopos definem quais permissões sua aplicação terá no Google Drive.
SCOPES = ['https://www.googleapis.com/auth/drive.file'] # Permite gerenciar arquivos criados/abertos por esta app.
# SCOPES = ['https://www.googleapis.com/auth/drive'] # Permite gerenciar todos os arquivos no seu Drive (mais amplo)


def upload_basic():
    """Mostra como fazer upload de um arquivo para o Google Drive."""
    creds = None
    # O arquivo token.json armazena os tokens de atualização e acesso do usuário, e
    # é criado automaticamente quando o fluxo de autorização é concluído pela primeira vez.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # Se não houver credenciais válidas disponíveis, permita que o usuário faça login.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # O arquivo credentials.json deve estar no mesmo diretório do script.
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Salva as credenciais para a próxima execução
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)

        # --- Configuração do Arquivo para Upload ---
        # Substitua pelo caminho completo do arquivo que você quer fazer upload no seu computador.
        file_path = 'caminho/para/seu/arquivo/local.txt' # <-- ALTERE ESTA LINHA

        if not os.path.exists(file_path):
            print(f"Erro: Arquivo local não encontrado: {file_path}")
            return

        file_name = os.path.basename(file_path) # Obtém apenas o nome do arquivo

        # Metadados do arquivo para o Google Drive
        file_metadata = {'name': file_name}
        # Define o tipo de mídia do arquivo (MIME type). requests adivinha para você na maioria dos casos.
        media = MediaFileUpload(file_path, mimetype='text/plain',
                                resumable=True) # Adicione o mimetype apropriado

        # --- Realizar o Upload ---
        print(f"Fazendo upload de '{file_name}' para o Google Drive...")
        file = service.files().create(body=file_metadata, media_body=media,
                                        fields='id').execute()
        print(f"Arquivo '{file_name}' (ID: {file.get('id')}) enviado com sucesso!")

    except Exception as e:
        print(f'Ocorreu um erro: {e}')

if __name__ == '__main__':
    # Chame a função para iniciar o processo de upload
    upload_basic()