import os
import tkinter as tk
from tkinter import filedialog, messagebox
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Escopo necessário (pode usar o mesmo do seu código anterior)
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def autenticar_google():
    """Autentica no Google Drive e retorna o serviço"""
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

def upload_arquivo(service, caminho_arquivo):
    """Faz upload do arquivo selecionado"""
    if not os.path.exists(caminho_arquivo):
        messagebox.showerror("Erro", f"Arquivo não encontrado: {caminho_arquivo}")
        return

    nome_arquivo = os.path.basename(caminho_arquivo)
    media = MediaFileUpload(caminho_arquivo, resumable=True)
    file_metadata = {'name': nome_arquivo}

    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    messagebox.showinfo("Sucesso", f"Arquivo enviado!\nNome: {nome_arquivo}\nID: {file.get('id')}")

def escolher_arquivo():
    """Abre o seletor de arquivo"""
    caminho = filedialog.askopenfilename(title="Escolha um arquivo para enviar")
    if caminho:
        entry_caminho.delete(0, tk.END)
        entry_caminho.insert(0, caminho)

def enviar_para_drive():
    caminho = entry_caminho.get()
    if not caminho:
        messagebox.showwarning("Atenção", "Por favor, selecione um arquivo primeiro.")
        return
    try:
        service = autenticar_google()
        upload_arquivo(service, caminho)
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro:\n{e}")

# --- Interface Tkinter ---
janela = tk.Tk()
janela.title("Upload para Google Drive")
janela.geometry("500x200")

tk.Label(janela, text="Selecione um arquivo para enviar:", font=("Arial", 12)).pack(pady=10)

frame = tk.Frame(janela)
frame.pack(pady=5)

entry_caminho = tk.Entry(frame, width=50)
entry_caminho.pack(side=tk.LEFT, padx=5)

btn_browse = tk.Button(frame, text="Procurar", command=escolher_arquivo)
btn_browse.pack(side=tk.LEFT)

btn_upload = tk.Button(janela, text="Enviar para Google Drive", command=enviar_para_drive, bg="green", fg="white", font=("Arial", 12))
btn_upload.pack(pady=20)

janela.mainloop()
