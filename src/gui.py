import os
import logging
import sys
import threading

import tkinter as tk
from PIL import Image, ImageTk
from tkmacosx import Button
from tkinter import filedialog, messagebox

from src.listeners import monitor_and_upload_folder
from src.drive_client import GoogleDriveClient
from src.settings import settings

logger = logging.getLogger("app")

def resource_path(relative_path):
    """Obtener la ruta del archivo, ya sea que esté en desarrollo o en el ejecutable."""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

class DriveUploaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Drive Uploader")
        self.root.geometry("800x600")

        icon_path = resource_path("icon_uploader.gif")
        image = Image.open(icon_path)
        tk_image = ImageTk.PhotoImage(image)
        self.root.iconphoto(True, tk_image)

        # Variables de configuración del usuario
        self.monitored_folder_path = tk.StringVar()
        self.credentials_path = tk.StringVar()
        self.drive_target_folder_id = tk.StringVar()
        self.check_folder_interval_seconds = settings.get("check_folder_interval_seconds", 10)
        self.file_types_to_monitor = settings.get("file_types_to_monitor", [".mp4", ".png", ".jpg", ".jpeg", ".txt"])

        # Estado de autenticación y monitoreo
        self.is_authenticated = False
        self.is_monitoring = False
        self.monitoring_thread = None
        self.stop_event = threading.Event()

        # Crear la interfaz
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Estado de autenticación:").pack(pady=5)
        self.auth_status_label = tk.Label(self.root, text="No autenticado")
        self.auth_status_label.pack(pady=5)

        # Botón para seleccionar el archivo de credenciales
        tk.Label(self.root, text="Selecciona el archivo de credenciales:").pack(pady=5)
        self.select_credentials_button = Button(self.root, text="Seleccionar archivo", command=self.select_credentials_file)
        self.select_credentials_button.pack(pady=5)
        self._apply_hover_effect(self.select_credentials_button)

        self.credentials_label = tk.Label(self.root, text="Archivo de credenciales: No seleccionado")
        self.credentials_label.pack(pady=5)

        # Botón de autenticación (deshabilitado inicialmente)
        self.auth_button = Button(self.root, text="Autenticar", command=self.authenticate, state="disabled")
        self.auth_button.pack(pady=5)
        self._apply_hover_effect(self.auth_button)

        # Botón para seleccionar carpeta de monitoreo (deshabilitado hasta autenticación)
        tk.Label(self.root, text="Selecciona la carpeta a monitorear:").pack(pady=5)
        self.select_folder_button = Button(self.root, text="Seleccionar carpeta", command=self.select_monitored_folder, state="disabled")
        self.select_folder_button.pack(pady=5)
        self._apply_hover_effect(self.select_folder_button)

        self.monitored_folder_label = tk.Label(self.root, text="Carpeta monitoreada: No seleccionada")
        self.monitored_folder_label.pack(pady=5)

        # Campo para ingresar el ID de la carpeta de destino (deshabilitado hasta autenticación)
        tk.Label(self.root, text="Ingresa el ID de la carpeta de destino en Google Drive:").pack(pady=5)
        self.drive_target_folder_entry = tk.Entry(self.root, textvariable=self.drive_target_folder_id, width=40, state="disabled")
        self.drive_target_folder_entry.pack(pady=5)

        # Botón para iniciar monitoreo (deshabilitado hasta autenticación)
        self.start_button = Button(self.root, text="Iniciar Monitoreo y Subida", command=self.start_monitoring, state="disabled")
        self.start_button.pack(pady=20)
        self._apply_hover_effect(self.start_button)
        self.start_status_label = tk.Label(self.root, text="Monitoreo no iniciado")
        self.start_status_label.pack(pady=5)

    def select_credentials_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            self.credentials_path.set(file_path)
            self.credentials_label.config(text=f"Archivo de credenciales: {file_path}")
            # Habilitar el botón de autenticación tras seleccionar credenciales
            self.auth_button.config(state="normal")

    def authenticate(self):
        if self.is_authenticated:
            return

        token_path = os.path.expanduser("~/Library/Application Support/MyDriveUploader/reusable_token.json")
        os.makedirs(os.path.dirname(token_path), exist_ok=True)

        def authenticate_thread():
            try:
                # Perform authentication
                self.drive_client = GoogleDriveClient(
                    client_secrets_path=self.credentials_path.get(),
                    reusable_token_path=token_path
                )
                self.is_authenticated = True
                # Schedule the UI update on the main thread
                self.root.after(0, lambda: self.update_authentication_status("Autenticado"))
                self.root.after(0, self.enable_post_auth_buttons)

            except Exception as e:
                logger.error(f"Error during authentication: {e}")
                self.root.after(0, lambda: messagebox.showerror("Authentication Error",
                                                                "Failed to authenticate. Please check your credentials."))

        # Iniciar el hilo de autenticación
        threading.Thread(target=authenticate_thread, daemon=True).start()

    @staticmethod
    def _apply_hover_effect(button):
        def on_enter(e):
            button.config(bg="lightblue")

        def on_leave(e):
            button.config(bg="SystemButtonFace")

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def update_authentication_status(self, status):
        self.auth_status_label.config(text=status)
        self.auth_button.config(state="disabled")

    def update_start_status(self, status):
        self.start_status_label.config(text=status)
        self.start_button.config(state="disabled")

    def enable_post_auth_buttons(self):
        # Habilitar botones después de autenticarse
        self.select_folder_button.config(state="normal")
        self.drive_target_folder_entry.config(state="normal")
        self.start_button.config(state="normal")

    def select_monitored_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.monitored_folder_path.set(folder)
            self.monitored_folder_label.config(text=f"Carpeta monitoreada: {folder}")

    def start_monitoring(self):
        if self.is_monitoring:
            messagebox.showinfo("Monitoreo en curso", "El monitoreo ya está en ejecución.")
            return

        if not self.monitored_folder_path.get() or not self.credentials_path.get() or not self.drive_target_folder_id.get():
            messagebox.showerror("Error", "Asegúrate de seleccionar la carpeta, archivo de credenciales, y de ingresar el ID de la carpeta de destino.")
            return

        # Iniciar el hilo de monitoreo
        self.is_monitoring = True
        self.stop_event.clear()  # Resetear el evento de parada
        self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.update_start_status("Monitoreando...")

    def monitoring_loop(self):
        try:
            monitor_and_upload_folder(
                drive_client=self.drive_client,
                folder_path=self.monitored_folder_path.get(),
                target_folder_id=self.drive_target_folder_id.get(),
                stop_event=self.stop_event
            )
        except Exception as e:
            logger.error(f"Error during monitoring and uploading: {e}")
            self.root.after(0, lambda: messagebox.showerror("Monitoring Error", f"Error in monitoring: {e}"))
            self.is_monitoring = False
            return

        # Schedule next run using after instead of wait
        self.root.after(self.check_folder_interval_seconds * 1000, self.monitoring_loop)

    def stop_monitoring(self):
        # Signal to stop the monitoring loop
        self.is_monitoring = False
        self.stop_event.set()  # Set the event to exit the monitoring loop

        # Give threads time to exit and clear any resources
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            # Wait for the monitoring thread to finish
            self.monitoring_thread.join(timeout=0.5)


    def on_closing(self):
        # Stop the monitoring if it is running
        self.stop_monitoring()
        # Finally, close the Tkinter window
        self.root.destroy()

def run_app():
    root = tk.Tk()
    app = DriveUploaderApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)  # Manejar el cierre de la ventana
    root.mainloop()