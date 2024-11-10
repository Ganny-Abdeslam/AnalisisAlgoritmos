from pymongo import MongoClient
import re

# Conectar a la base de datos MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["analisis"]
collection = db["articulos"]

# Leer el archivo de datos
with open("unificados.bib", "r", encoding="utf-8") as file:
    content = file.read()


# Separar los registros basados en el delimitador
records = content.strip().split("------------------------------------")

# Procesar e insertar cada registro
for record in records:
    # Saltar si el registro está vacío
    if not record.strip():
        continue
    
    # Extraer los campos del registro con manejo de ausencias
    data = {
        "BDOrigen": re.search(r"BDOrigen:\s*(.*)", record).group(1).strip() if re.search(r"BDOrigen:\s*(.*)", record) else "",
        "Tipe": re.search(r"Tipe:\s*(.*)", record).group(1).strip() if re.search(r"Tipe:\s*(.*)", record) else "",
        "journal": re.search(r"journal:\s*(.*)", record).group(1).strip() if re.search(r"journal:\s*(.*)", record) else "",
        "author": re.search(r"author:\s*(.*)", record).group(1).strip() if re.search(r"author:\s*(.*)", record) else "",
        "title": re.search(r"title:\s*(.*)", record).group(1).strip() if re.search(r"title:\s*(.*)", record) else "",
        "year": int(re.search(r"year:\s*(\d+)", record).group(1).strip()) if re.search(r"year:\s*(\d+)", record) else None,
        "abstract": re.search(r"abstract:\s*(.*)", record).group(1).strip() if re.search(r"abstract:\s*(.*)", record) else "",
        "doi": re.search(r"doi:\s*(.*)", record).group(1).strip() if re.search(r"doi:\s*(.*)", record) else "",
    }
    
    # Insertar en la colección de MongoDB
    collection.insert_one(data)

print("Datos insertados en MongoDB.")
