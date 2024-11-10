import os
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from src.settings import settings

logger = logging.getLogger("app")



class GoogleDriveClient:
    def __init__(
            self,
            client_secrets_path: str = "client_secrets.json",
            oauth_scope: list | None = None,
            reusable_token_path: str | None = None
    ):
        self.reusable_token_path = reusable_token_path
        self.client_secrets_path = client_secrets_path
        self.oauth_scope = oauth_scope or ["https://www.googleapis.com/auth/drive"]
        self.credentials = self._authenticate()
        self.service = self._get_service()


    def _authenticate(self) -> Credentials:
        try:
            logger.info("Autenticando con Google Drive")
            creds = None
            if os.path.exists(self.reusable_token_path):
                logger.info(f"Usando token reutilizable.")
                creds = Credentials.from_authorized_user_file(self.reusable_token_path)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    creds = self._get_new_credentials()

                with open(self.reusable_token_path, "w") as token:
                    token.write(creds.to_json())

            logger.info("Autenticación exitosa.")
            return creds
        except Exception as e:
            logger.error(f"Error durante la autenticación: {e}")
            raise

    def _get_new_credentials(self) -> Credentials:
        logger.info("Obteniendo nuevas credenciales.")
        flow = InstalledAppFlow.from_client_secrets_file(
            self.client_secrets_path, scopes=self.oauth_scope
        )
        creds = flow.run_local_server(port=0)
        return creds

    def _get_service(self) -> Resource:
        return build("drive", "v3", credentials=self.credentials)

    def list_items_in_folder(self, folder_id: str, page_size: int = 10):
        try:
            query = f"'{folder_id}' in parents and trashed=false"
            results = (
                self.service.files()
                .list(
                    q=query,
                    pageSize=page_size,
                    fields="nextPageToken, files(id, name, kind), kind",
                )
                .execute()
            )
            items = results.get("files", [])
            for item in items:
                logger.info(f"File: {item['name']} (ID: {item['id']})")
            return items
        except HttpError as e:
            logger.error(f"Error al listar archivos y carpetas en la carpeta {folder_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error al listar archivos y carpetas en la carpeta {folder_id}: {e}")
            raise

    def upload_file_to_folder(self, folder_id: str, file_path: str):
        """"""
        # Verifica que el archivo existe y tiene una extensión válida
        if not os.path.isfile(file_path):
            logger.error(f"El archivo {file_path} no existe.")
            return None

        # Obtiene la extensión del archivo
        _, file_extension = os.path.splitext(file_path)
        if file_extension.lower() not in settings.get("file_types_to_monitor"):
            logger.error(f"El tipo de archivo '{file_extension}' no es soportado.")
            return None

        try:
            logger.info(f"Subiendo archivo {file_path} a la carpeta {folder_id}")
            file_name = os.path.basename(file_path)
            file_metadata = {
                "name": file_name,
                "parents": [folder_id]
            }
            media = MediaFileUpload(file_path, resumable=True)
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id"
            ).execute()
            logger.info(f"Archivo subido: {file.get('id')}")
            return file
        except Exception as e:
            logger.error(f"Error al subir archivo {file_path} a la carpeta {folder_id}: {e}")
            raise
