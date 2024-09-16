# Basisimage verwenden
FROM python:3.11-slim

# Arbeitsverzeichnis festlegen
WORKDIR /app

# Kopiere die requirements-Datei in das Image
COPY requirements.txt .

# Installiere die Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den restlichen Code ins Arbeitsverzeichnis
COPY . .

# Starte den Bot
CMD ["python", "main.py"]