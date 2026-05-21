
"""
# Contratos + Seguimientos con JSON (db.json)

 Estructura esperada:
 {
   "contracts": [
     {
       "number": "C-1001",
       "contractor": "Ana Torres",
       "object": "Mantenimiento",
       "start": "01/02/2026",
       "end": "01/05/2026",
       "value": 3500000,
       "supervisor": "Carlos Mejía",
       "status": "ACTIVO",
       "email": "ana@example.com",
       "trackings": [
         {
           "id": 1,
           "date": "15/02/2026",
           "desc": "Revisión inicial",
           "progress": 10,
           "obs": "Sin novedades"
         }
       ]
     }
   ]
 }

 Export "conveniente" -> contracts.csv y trackings.csv
"""
import os
import json
import csv
from datetime import datetime, date, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "db.json")
CONTRACTS_CSV = "contracts.csv"
TRACKINGS_CSV = "trackings.csv"


# Persistencia

def _ensure_db():
    """
    Si db.json no existe, debe crearlo con la estructura:
    {"contracts": []}
    """
    
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({"contracts": []}, f, indent=4)


def _load_db():
    _ensure_db()
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            print("Estructura inválida")
            return {"contracts": []}

        if "contracts" not in data:
            return {"contracts": []}

        if not isinstance(data["contracts"], list):
            return {"contracts": []}

        return data

    except (IOError, ValueError, json.JSONDecodeError) as e:
        print(f"Error al cargar DB: {e}")
        return {"contracts": []}


def _save_db(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error guardando DB: {e}")
        return False


# Validaciones auxiliares

def _parse_date_ddmmyyyy(s):
    """
    Debe convertir una fecha en formato dd/mm/aaaa a tipo date.
    """
    return datetime.strptime(s, "%d/%m/%Y").date()





    """
    Debe convertir una fecha en formato dd/mm/aaaa a tipo date.

    Ejemplo:
    "15/02/2026" -> date(2026, 2, 15)

    Si la fecha no es válida, debe lanzar excepción.
    """


def _valid_email(e):
    
    if not isinstance(e, str):
        return False

    if " " in e:
        return False

    if e.count("@") != 1:
        return False

    left, right = e.split("@")

    if left == "" or right == "":
        return False

    if "." not in right:
        return False

    return True
    """
    Debe validar de manera básica si un correo electrónico es válido.

    Condiciones mínimas:
    - debe ser string
    - no debe tener espacios
    - debe tener un solo @
    - debe tener texto antes y después del @
    - la parte de la derecha debe contener un punto

    Retorna:
    - True
    - False
    """


def _valid_status(s):

    valid = ["ACTIVO", "SUSPENDIDO", "TERMINADO"]

    if s in valid:
        return True
    else:
        return False
    """
    Debe validar el estado del contrato.

    Estados válidos:
    - ACTIVO
    - SUSPENDIDO
    - TERMINADO

    Retorna:
    - True
    - False
    """


def _to_positive_float(x):
    try:
        datoflotante = float(x)
        if 0 <= datoflotante:
            return datoflotante
        else:
            return None
    except:
        return None

    

    
    """
    Debe intentar convertir x a float positivo.

    Retorna:
    - valor float si es válido y mayor a cero
    - None si no es válido
    """


def _find_contract(data, number):
    

    for c in data["contracts"]:
        if c["number"] == number:
            return c

    return None
        




    


    """
    Debe buscar un contrato por número dentro de data["contracts"].

    Retorna:
    - el diccionario del contrato si existe
    - None si no existe
    """


# API principal de contratos

def registerContract(number, contractor, obj, start, end, value, supervisor, status, email):

    try:
        if not number or not contractor or not obj or not start or not end or not value or not supervisor or not status or not email:
            return "invalid data"

        if not _valid_email(email):
            return "invalid data"

        if not _valid_status(status):
            return "invalid data"

        value = _to_positive_float(value)
        if value is None:
            return "invalid data"

        try:
            fecha_inicial = _parse_date_ddmmyyyy(start)
            fecha_final = _parse_date_ddmmyyyy(end)
        except:
            return "invalid date format"

        if fecha_final < fecha_inicial:
            return "invalid date range"

        data = _load_db()

        if _find_contract(data, number) is not None:
            return "number already exists"

        contract = {
            "number": number,
            "contractor": contractor,
            "object": obj,
            "start": start,
            "end": end,
            "value": value,
            "supervisor": supervisor,
            "status": status,
            "email": email,
            "trackings": []
        }

        data["contracts"].append(contract)
        _save_db(data)

        return "ok"

    except Exception as e:
        print(f"Error en registerContract: {e}")
        return "invalid data"
    
    
    


    """
    Debe registrar un contrato nuevo.

    Validaciones obligatorias:
    - todos los campos obligatorios deben existir
    - el número de contrato debe ser único
    - el estado debe ser válido
    - el correo debe ser válido
    - el valor debe ser numérico positivo
    - la fecha debe tener formato válido
    - la fecha de inicio debe ser <= a la fecha de terminación

    El contrato debe guardarse con una lista vacía de trackings:
    "trackings": []

    Retorna:
    - "ok"
    - "invalid data"
    - "invalid date format"
    - "invalid date range"
    - "number already exists"
    """


def listContracts():
    data = _load_db()
    contracts = []      #Excluye los trackings (seguimientos). Para el listado general no se necesitan los seguimientos.

    for c in data["contracts"]:
        contracts.append({
            "number": c["number"],
            "contractor": c["contractor"],
            "object": c["object"],
            "start": c["start"],
            "end": c["end"],
            "value": c["value"],
            "supervisor": c["supervisor"],
            "status": c["status"],
            "email": c["email"]     
        })

    n = len(contracts)
    for i in range(n):
        for j in range(i + 1, n):
            if contracts[i]["contractor"] > contracts[j]["contractor"]:  # Comparar nombres de contratista alfabéticamente
                contracts[i], contracts[j] = contracts[j], contracts[i]

    return contracts

    """
    Debe devolver la lista de contratos ordenada alfabéticamente
    por contractor.

    Importante:
    - Para el listado general NO es necesario devolver los trackings.
    - Puede devolver una lista de diccionarios "liviana".

    Retorna:
    - lista de contratos
    """


def searchContract(number):
    datos = _load_db()

    for contrato in datos["contracts"]:
        if contrato["number"] == number:
            return contrato

    return None

    """
    Debe buscar un contrato por número.

    Retorna:
    - el contrato completo si existe (incluyendo trackings)
    - None si no existe
    """


# API de seguimientos

def addTracking(number, date_str, desc, progress, obs):

    try:
        if not number or not desc:
            return "invalid data"

        try:
            _parse_date_ddmmyyyy(date_str)
        except:
            return "invalid date format"

        try:
            progress = int(progress)
            if progress < 0 or progress > 100:
                return "invalid data"
        except:
            return "invalid data"

        data = _load_db()
        contract = _find_contract(data, number)

        if contract is None:
            return "contract not found"

        trackings = contract["trackings"]
        new_id = len(trackings) + 1

        tracking = {
            "id": new_id,
            "date": date_str,
            "desc": desc,
            "progress": progress,
            "obs": obs
        }

        trackings.append(tracking)
        _save_db(data)

        return "ok"

    except Exception as e:
        print(f"Error en addTracking: {e}")
        return "invalid data"
    

    



    """
    Debe agregar un seguiminto a un contrato existente.

    Validaciones:
    - number no vacío
    - date_str válido
    - desc no vacío
    - progress entero entre 0 y 100
    - el contrato debe existir

    El seguimiento debe guardarse con estructura:
    {
      "id": 
      "date": 
      "desc": 
      "progress": 
      "obs": 
    }

    El id puede ser incremental por contrato.

    Retorna:
    - "ok"
    - "invalid data"
    - "invalid date format"
    - "contract not found"
    """
    


def listTrackings(number):
    try:
        if not number:
            return "invalid data"

        data = _load_db()
        contract = _find_contract(data, number)

        if contract is None:
            return "contract not found"

        return contract["trackings"]

    except Exception as e:
        print(f"Error en listTrackings: {e}")
        return []
    

    


    """
    Debe listar los seguimientos de un contrato.

    Validaciones:
    - number no vacío
    - el contrato debe existir

    Retorna:
    - lista de seguimientos
    - "invalid data"
    - "contract not found"
    """


def avgProgress(number):
    try:
        if not number:
            return "invalid data"

        data = _load_db()
        contract = _find_contract(data, number)

        if contract is None:
            return "contract not found"

        trackings = contract["trackings"]

        if len(trackings) == 0:
            promedio = 0.0
        else:
            total = sum(t["progress"] for t in trackings)
            promedio = total / len(trackings)

        return {
            "number": number,
            "count": len(trackings),
            "avg_progress": promedio
        }

    except Exception as e:
        print(f"Error en avgProgress: {e}")
        return "invalid data"

    
    
    


    """
    Debe calcular el promedio de avance de un contrato.

    Validaciones:
    - number no vacío
    - el contrato debe existir

    Si no tiene seguimientos, el promedio debe ser 0.0

    Retorna:
    - {"number": ..., "count": ..., "avg_progress": ...}
    - "invalid data"
    - "contract not found"
    """


# Estadísticas

def stats():
    try:
        data = _load_db()
        contracts = data["contracts"]

        total_contracts = len(contracts)

        total_by_status = {
            "ACTIVO": 0,
            "SUSPENDIDO": 0,
            "TERMINADO": 0
        }

        total_value = 0
        max_contract = None
        min_contract = None
        soon = []

        today = date.today()

        for c in contracts:
            if c["status"] in total_by_status:
                total_by_status[c["status"]] += 1

            value = float(c["value"])
            total_value += value

            if max_contract is None or value > float(max_contract["value"]):
                max_contract = c

            if min_contract is None or value < float(min_contract["value"]):
                min_contract = c

            end_date = _parse_date_ddmmyyyy(c["end"])

            if 0 <= (end_date - today).days <= 30:
                soon.append(c)

        avg_value = total_value / total_contracts if total_contracts > 0 else 0

        return {
            "total_contracts": total_contracts,
            "total_by_status": total_by_status,
            "total_value": total_value,
            "avg_value": avg_value,
            "max_contract": max_contract,
            "min_contract": min_contract,
            "contracts_soon_to_end": soon
        }

    except Exception as e:
        print(f"Error en stats: {e}")
        return {}
    """
    Debe calcular las estadísticas generales del sistema:

    - total_contracts
    - total_by_status
    - total_value
    - avg_value
    - max_contract
    - min_contract
    - contracts_soon_to_end

    Donde:
    - total_by_status cuenta contratos por estado
    - total_value es la suma total de valores
    - avg_value es el promedio del valor de los contratos
    - max_contract es el contrato con mayor valor
    - min_contract es el contrato con menor valor
    - contracts_soon_to_end son contratos que vencen en los próximos 30 días

    Retorna:
    - diccionario con las estadísticas
    """
    


# Exportacón a CSV

def exportCsv():
    data = _load_db()

    with open(CONTRACTS_CSV, "w", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)

        writer.writerow([
            "number",
            "contractor",
            "object",
            "start",
            "end",
            "value",
            "supervisor",
            "status",
            "email"
        ])

        for c in data["contracts"]:
            writer.writerow([
                c["number"],
                c["contractor"],
                c["object"],
                c["start"],
                c["end"],
                c["value"],
                c["supervisor"],
                c["status"],
                c["email"]
            ])

    with open(TRACKINGS_CSV, "w", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)

        writer.writerow([
            "number",
            "id",
            "date",
            "desc",
            "progress",
            "obs"
        ])

        for c in data["contracts"]:
            for t in c["trackings"]:
                writer.writerow([
                    c["number"],
                    t["id"],
                    t["date"],
                    t["desc"],
                    t["progress"],
                    t["obs"]
                ])
    """
    Debe exportar la información a dos archivos CSV:

    1. contracts.csv
       Columnas sugeridas:
       - number
       - contractor
       - object
       - start
       - end
       - value
       - supervisor
       - status
       - email

    2. trackings.csv
       Columnas sugeridas:
       - number
       - id
       - date
       - desc
       - progress
       - obs

    Debe recorrer los contratos y luego, para cada contrato,
    exportar también sus seguimientos.

    Esta función no retorna nada.
    """
