# Web app para Generador de Horarios

Instrucciones rápidas:

- Instalar dependencias (recomendado usar un virtualenv):

```powershell
python -m pip install -r web_app/requirements.txt
```

- Ejecutar MongoDB localmente (por ejemplo usando `mongod`).
- Ajustar variable de entorno `MONGO_URI` si es necesario.
- Iniciar la app:

```powershell
set MONGO_URI=mongodb://localhost:27017; python web_app/app.py
```

La interfaz estará disponible en `http://127.0.0.1:5000/`.

Notas:
- El backend usa `pymongo` para almacenar y recuperar materias.
- La generación de horarios reutiliza la lógica existente, pero se evita abrir ventanas GUI (se ejecuta en modo headless).
 - La generación de horarios reutiliza la lógica existente, pero se evita abrir ventanas GUI (se ejecuta en modo headless).

Para deploy en Render/Heroku:

- El `Procfile` incluido ejecuta `gunicorn`.
- Configure la variable de entorno `MONGO_URI` en Render apuntando a su clúster de MongoDB Atlas.

Para poblar la colección `carreras` con los JSON locales, ejecutar:

```powershell
set MONGO_URI=mongodb://localhost:27017; python web_app/scripts/load_carreras.py
```

Start command recomendado (si no usa `Procfile`):

```powershell
gunicorn -w 4 web_app.app:app
```
