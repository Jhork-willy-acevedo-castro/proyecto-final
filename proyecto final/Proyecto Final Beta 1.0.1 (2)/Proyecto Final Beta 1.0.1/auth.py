import os
import json


# Esto obtiene la ruta exacta de la carpeta donde está ESTE archivo (auth.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ahora unimos esa carpeta con el nombre del archivo JSON
USERS_FILE = os.path.join(BASE_DIR, "users.json")

def _ensure_users_file():
    #Crea el archivo con si no existe.
    if not os.path.exists(USERS_FILE):
        data = {"users": []}
        try:
            with open(USERS_FILE, "w") as f:
                json.dump(data, f, indent=4)
            return True
        except IOError: #En caso de un error al crear archivo
            return False
    return True

def _load():
    #Carga los datos en caso de existir archivo
    _ensure_users_file()
    try:
        with open(USERS_FILE, "r") as f:
            data = json.load(f)
    
            if "users" not in data:
                return {"users": []}
            return data
    except (IOError, json.JSONDecodeError): #En caso de que el archivo tenga algun error o no deje leer
        return {"users": []}

def _save(data):
    #Guarda la estructura completa sobrescribiendo el archivo.
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error al guardar: {e}")

def _valid_role(role):
    return role in ["admin", "supervisor", "viewer"]

def findUser(user):
    data = _load()
    for u in data.get("users", []):
        if u["user"] == user:
            return u
    return None

def registerUser(user, password, role):
    # Validaciones básicas
    if not user.strip() or not password.strip() or not _valid_role(role):
        return "invalid data"
    
    #Comprobar que no este 
    if findUser(user):
        return "user exists"
    
    data = _load()
    data["users"].append({
        "user": user,
        "password": password,
        "role": role,
        "session": False
    })
    _save(data)
    return "ok"

def openCloseSession(user, password, flag):
    data = _load()
    found = False
    for u in data["users"]:
        if u["user"] == user and u["password"] == password:
            u["session"] = flag
            found = True
            break
    
    if found:
        _save(data)
        return "ok"
    return "wrong credentials"

def hasRole(user, allowed_roles):
    u = findUser(user)
    if u and u.get("role") in allowed_roles:
        return True
    return False

def get_user_role(username):
    users = findUser(username) # Usas la función que ya lee el JSON
    if users:
        return users.get("role") # Devuelve 'admin', 'supervisor', etc.
    return None