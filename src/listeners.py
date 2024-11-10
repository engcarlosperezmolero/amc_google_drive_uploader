import os
import threading
import time
import logging

from googleapiclient.errors import HttpError

from src.settings import settings
from src.drive_client import GoogleDriveClient


logger = logging.getLogger("app")

def monitor_and_upload_folder(
        drive_client: GoogleDriveClient,
        folder_path: str,
        target_folder_id: str,
        stop_event: threading.Event,
):
    """
    Monitorea una carpeta local y sube archivos nuevos a Google Drive.
    """
    # Lista de archivos ya conocidos para evitar duplicados
    known_files = set(os.listdir(folder_path))

    logger.info("Iniciando monitoreo de la carpeta...")

    while True:
        try:
            # Obtén la lista actual de archivos en la carpeta
            current_files = set(os.listdir(folder_path))

            # Detecta los archivos nuevos comparando con `known_files`
            new_files = current_files - known_files

            # Subir archivos nuevos
            for new_file in new_files:
                file_path = os.path.join(folder_path, new_file)
                logger.info(f"Detectado archivo nuevo: {new_file}. Intentando subirlo...")

                try:
                    # Sube el archivo a la carpeta de Google Drive
                    drive_client.upload_file_to_folder(target_folder_id, file_path)
                    logger.info(f"Archivo {new_file} subido exitosamente.")
                except HttpError as e:
                    logger.error(f"Error al intentar subir el archivo {new_file}: {e}")

            # Actualiza la lista de archivos conocidos
            known_files = current_files

            # Espera 1 segundo antes de verificar nuevamente
            if stop_event.wait(settings.get("check_folder_interval_seconds")):
                logger.info("Deteniendo monitoreo de la carpeta...")
                break


        except Exception as e:
            logger.error(f"Error en el monitoreo de la carpeta: {e}")
            time.sleep(5)  # Espera más tiempo en caso de un error

    logger.info("Monitoreo de la carpeta detenido.")