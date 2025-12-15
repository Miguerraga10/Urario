"""Script para cargar documentos de carreras desde la carpeta `Datos/` a la colección `carreras` en MongoDB.

Uso:
  set MONGO_URI=mongodb://...; python web_app/scripts/load_carreras.py

El script intentará leer archivos JSON en `Datos/` y cargar documentos en la colección.
"""
import os
import json
from web_app import db

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATOS_DIR = os.path.join(BASE, 'Datos')

def load_files():
    docs = []
    if not os.path.isdir(DATOS_DIR):
        print('No existe la carpeta Datos/ en:', DATOS_DIR)
        return docs
    for fname in os.listdir(DATOS_DIR):
        if not fname.lower().endswith('.json'):
            continue
        path = os.path.join(DATOS_DIR, fname)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Si es lista, extendemos; si es dict, lo añadimos
            if isinstance(data, list):
                docs.extend(data)
            elif isinstance(data, dict):
                docs.append(data)
            print(f'Leído {path} -> {len(docs)} docs acumuladas')
        except Exception as e:
            print('Error leyendo', path, e)
    return docs

def main():
    docs = load_files()
    if not docs:
        print('No se encontraron documentos para insertar.')
        return
    try:
        db.insert_carreras(docs)
        print(f'Insertadas {len(docs)} documentos en la colección carreras.')
    except Exception as e:
        print('Error insertando en DB:', e)

if __name__ == '__main__':
    main()
