# ==========================================
# archivo: test_client.py (NO modificar)
# Prueba simple: auth + contratos + seguimientos + stats + export
# ==========================================
import os
import supervision_client as cli

URL = "http://localhost:8080"

# Limpieza opcional (reproducible)
for f in ("users.json", "db.json", "contracts.csv", "trackings.csv"):
    try:
        if os.path.exists(f):
            os.remove(f)
    except Exception:
        pass

print("== HEALTH ==")
print(cli.health(URL))

print("\n== REGISTRO USUARIOS ==")
print(cli.registerUser(URL, "admin1", "adm", "admin"))
print(cli.registerUser(URL, "sup1", "123", "supervisor"))
print(cli.registerUser(URL, "viewer1", "111", "viewer"))

print("\n== ABRIR SESIÓN ==")
print(cli.openSession(URL, "admin1", "adm"))
print(cli.openSession(URL, "sup1", "123"))
print(cli.openSession(URL, "viewer1", "111"))

print("\n== REGISTRAR CONTRATO (supervisor) ==")
print(cli.registerContract(
    URL, user="sup1", password="123",
    number="C-1001",
    contractor="Ana Torres",
    obj="Mantenimiento de equipos",
    start="01/02/2026",
    end="01/05/2026",
    value="3500000",
    supervisor="Carlos Mejía",
    status="ACTIVO",
    email="ana.torres@example.com"
))

print("\n== REGISTRAR CONTRATO DUPLICADO (debe fallar) ==")
print(cli.registerContract(
    URL, user="sup1", password="123",
    number="C-1001",
    contractor="Otro",
    obj="Otro",
    start="01/02/2026",
    end="01/05/2026",
    value="100",
    supervisor="X",
    status="ACTIVO",
    email="x@y.com"
))

print("\n== LISTAR CONTRATOS (viewer) ==")
print(cli.listContracts(URL, "viewer1", "111"))

print("\n== BUSCAR CONTRATO (viewer) ==")
print(cli.searchContract(URL, "viewer1", "111", "C-1001"))

print("\n== AGREGAR SEGUIMIENTO (supervisor) ==")
print(cli.addTracking(URL, "sup1", "123", number="C-1001",
                      date_ddmmyyyy="15/02/2026",
                      desc="Revisión inicial",
                      progress="10",
                      obs="Sin novedades"))

print("\n== LISTAR SEGUIMIENTOS (viewer) ==")
print(cli.listTrackings(URL, "viewer1", "111", "C-1001"))

print("\n== PROMEDIO AVANCE (viewer) ==")
print(cli.avgProgress(URL, "viewer1", "111", "C-1001"))

print("\n== STATS (viewer) ==")
print(cli.stats(URL, "viewer1", "111"))

print("\n== EXPORTAR CSV (solo admin) ==")
print(cli.exportCsv(URL, "admin1", "adm"))

print("\n== CERRAR SESIÓN ==")
print(cli.closeSession(URL, "admin1", "adm"))
print(cli.closeSession(URL, "sup1", "123"))
print(cli.closeSession(URL, "viewer1", "111"))