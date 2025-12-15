import os
from pymongo import MongoClient
from bson.objectid import ObjectId

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
client = MongoClient(MONGO_URI)
db = client.get_database('gen_horario')
materias_coll = db.get_collection('materias')

# Colección para datos de carreras (estructura similar a sia-extractor outputs)
carreras_coll = db.get_collection('carreras')

def get_all_materias():
    docs = list(materias_coll.find())
    for d in docs:
        d['id'] = str(d.pop('_id'))
    return docs

def insert_materia(doc):
    # doc is a dict serializable to BSON
    res = materias_coll.insert_one(doc)
    return str(res.inserted_id)

def replace_materias(docs):
    materias_coll.delete_many({})
    if docs:
        materias_coll.insert_many(docs)

def clear_materias():
    materias_coll.delete_many({})

def upsert_materias(list_of_docs):
    """Inserta o actualiza materias por su código (o nombre si no tiene código)."""
    for doc in list_of_docs:
        key = doc.get('codigo') or doc.get('nombre')
        if not key:
            continue
        materias_coll.replace_one({'codigo': doc.get('codigo')}, doc, upsert=True)

def get_carrera_by_name_and_sede(nombre_carrera, sede=None):
    q = {'carrera': {'$regex': f'^{re_escape(nombre_carrera)}$', '$options': 'i'}}
    if sede:
        q['sede'] = {'$regex': f'^{re_escape(sede)}$', '$options': 'i'}
    doc = carreras_coll.find_one(q)
    return doc

def get_carrera_by_code(code):
    return carreras_coll.find_one({'codigo': code})

def insert_carreras(docs):
    if not docs:
        return
    carreras_coll.insert_many(docs)

def get_all_carreras():
    return list(carreras_coll.find())

def re_escape(s):
    # simple escape for regex
    import re
    return re.escape(s)
