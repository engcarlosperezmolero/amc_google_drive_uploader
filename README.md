
## consent oauth
https://console.cloud.google.com/auth/clients?project=sandbox-charly

## carpeta de kuamo
https://drive.google.com/drive/folders/1YWCfj01WElUWKxKwiYhx6XifCzwXqhqN

## quick start:
https://developers.google.com/drive/api/quickstart/python#configure_the_sample

## Resource.File methods documentation:
https://developers.google.com/drive/api/reference/rest/v3/files#resource:-file

## A implementar
- [ ] usar archivo de logs para monitorear el estado del archivo siendo exportado
      segun el link https://helpx.adobe.com/media-encoder/using/log-files.html#encoding_log_file, 
      remover asi el input de la ruta a la carpeta a escuchar ya que ahora se puede extraer
      de los logs directamente.
- [ ] implementar verificacion de carpeta del google drive una vez dado el ID.

pendientes:
- [ ] mejorar el threading para que no se bloquee la GUI.
- [ ] arreglar tema de la locacion del token reusable generado por el backend
- [ ] arreglar la GUI para que funcione sin problemas:
  - boton para iniciar sesion en google y mostrar label indicando el resultado
  - mostrar labels de los inputs de carpetas o archivos seleccionados
  - mostrar labels del nombre de la carpeta a la cual corresponde el id introducido (drive)

- [x] re usar un token despues de iniciar sesion la primera vez (averiguar si expira)
- [x] hacer cliente usando la V3 de la api de google drive
- [x] subir archivos usando https://developers.google.com/drive/api/guides/manage-uploads#resumable
- [x] implementar https://developers.google.com/drive/api/guides/manage-uploads#resume-upload

### Drive folder id:
- `1YWCfj01WElUWKxKwiYhx6XifCzwXqhqN` de kuamasi
- `1R3tTlcFcuAjbHtHnXPf6geOygNgqBu1H` de chemeng para pruebas


## comandos para compilar en x86_64 - intel (desde mac m1)
- tener instalado python con universal2 (se instalo python13.0.0 desde la pagina oficial)
```bash
# chequar que python sea universal2
file /usr/local/bin/python3

# crear el entorno virtual en x86_64
arch -x86_64 /usr/local/bin/python3 -m venv venv_x86
source venv_x86/bin/activate
pip install -r requirements.txt

# ejecutar el script en x86_64
# puede que necesite cambiar alguna ruta al .gif en la gui
python -m src.app

# chequear que se instalo correctamente todo en x86_64
find venv_x86/lib/python3.13/site-packages/ -name "*.so" -exec file {} \;

# instalar pyinstaller en x86_64
pip install pyinstaller

# compilar en x86_64
arch -x86_64 pyinstaller --onefile --windowed --icon=aiqo8-r1uuv.icns  src/app.py --add-data "src/icon_uploader.gif:." --name="GoogleDriveUploaderK_x86_64" --target-arch=x86_64

```