"""
Script para vaciar los logs. La carpeta por defecto se llama logs, si posee otro nombre
cambiar el string en CARPETA_LOGS
"""
import os

CARPETA_LOGS = os.path.join(os.getcwd(), 'logs')

with os.scandir(CARPETA_LOGS) as dirs:
    for file in dirs:
        open(os.path.join(CARPETA_LOGS, file.name), 'w').close()
        print(f'Archivo {file.name} vaciado!')
