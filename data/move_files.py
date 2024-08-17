import os
import shutil

# Ruta de la carpeta principal
ruta_principal = "./PDFs"

# Recorre todas las subcarpetas y archivos
for subdir, _, archivos in os.walk(ruta_principal):
    if subdir == ruta_principal:
        continue  # Saltar la carpeta principal

    for archivo in archivos:
        # Ruta completa del archivo actual
        ruta_archivo = os.path.join(subdir, archivo)
        
        # Mover el archivo a la carpeta principal
        shutil.move(ruta_archivo, ruta_principal)

    # Eliminar la subcarpeta vacía
    os.rmdir(subdir)

print("Archivos movidos exitosamente.")
