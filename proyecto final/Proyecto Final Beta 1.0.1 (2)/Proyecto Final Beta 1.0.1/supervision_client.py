# ==========================================
# archivo: supervision_client.py
# Cliente HTTP simple con requests
# Requiere: pip install requests
# ==========================================
import requests

HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}


def health(url):
    r = requests.get(url + "/health")
    return r.content.decode("utf-8", errors="replace")


# ---- Usuarios ----
def registerUser(url, user, password, role):
    body = f"user={user}&password={password}&role={role}"
    r = requests.post(url + "/user/register", data=body, headers=HEADERS)
    return r.content.decode("utf-8", errors="replace")


def openSession(url, user, password):
    body = f"user={user}&password={password}&flag=true"
    r = requests.post(url + "/user/session", data=body, headers=HEADERS)
    return r.content.decode("utf-8", errors="replace")


def closeSession(url, user, password):
    body = f"user={user}&password={password}&flag=false"
    r = requests.post(url + "/user/session", data=body, headers=HEADERS)
    return r.content.decode("utf-8", errors="replace")


# ---- Contratos ----
def registerContract(url, user, password, number, contractor, obj, start, end, value, supervisor, status, email):
    body = (
        f"user={user}&password={password}"
        f"&number={number}&contractor={contractor}&object={obj}"
        f"&start={start}&end={end}&value={value}"
        f"&supervisor={supervisor}&status={status}&email={email}"
    )
    r = requests.post(url + "/register", data=body, headers=HEADERS)
    return r.content.decode("utf-8", errors="replace")


def listContracts(url, user, password):
    r = requests.get(url + f"/list?user={user}&password={password}")
    return r.content.decode("utf-8", errors="replace")


def searchContract(url, user, password, number):
    r = requests.get(url + f"/search?user={user}&password={password}&number={number}")
    return r.content.decode("utf-8", errors="replace")


# ---- Seguimientos ----
def addTracking(url, user, password, number, date_ddmmyyyy, desc, progress, obs):
    body = (
        f"user={user}&password={password}"
        f"&number={number}&date={date_ddmmyyyy}&desc={desc}&progress={progress}&obs={obs}"
    )
    r = requests.post(url + "/tracking/add", data=body, headers=HEADERS)
    return r.content.decode("utf-8", errors="replace")


def listTrackings(url, user, password, number):
    r = requests.get(url + f"/tracking/list?user={user}&password={password}&number={number}")
    return r.content.decode("utf-8", errors="replace")


def avgProgress(url, user, password, number):
    r = requests.get(url + f"/tracking/avg?user={user}&password={password}&number={number}")
    return r.content.decode("utf-8", errors="replace")


# ---- Stats y Export ----
def stats(url, user, password):
    r = requests.get(url + f"/stats?user={user}&password={password}")
    return r.content.decode("utf-8", errors="replace")


def exportCsv(url, user, password):
    body = f"user={user}&password={password}"
    r = requests.post(url + "/export", data=body, headers=HEADERS)
    return r.content.decode("utf-8", errors="replace")
