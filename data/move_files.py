import os
import shutil

# Path to the main folder
ruta_principal = os.getenv('DATA_PATH')

# Traverse all subfolders and files
for subdir, _, archivos in os.walk(ruta_principal):
    if subdir == ruta_principal:
        continue  # Skip the main folder

    for archivo in archivos:
        # Full path of the current file
        ruta_archivo = os.path.join(subdir, archivo)
        
        # Move the file to the main folder
        shutil.move(ruta_archivo, ruta_principal)

    # Remove the empty subfolder
    os.rmdir(subdir)

print("Files moved successfully.")
