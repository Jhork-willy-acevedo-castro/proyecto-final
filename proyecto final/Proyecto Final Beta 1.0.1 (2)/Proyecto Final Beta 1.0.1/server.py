# ==========================================
# archivo: server.py  (NO modificar)
# Servidor HTTP simple (stdlib) - Supervisión Contractual
# Persistencia: JSON (db.json, users.json). Export: CSV
# Depende de: auth.py y supervision.py
# ==========================================
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import json
import sys

import auth
import supervision

HOST = "0.0.0.0"
PORT = 8080


def _json_response(handler, code, payload):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _read_body(handler):
    length = int(handler.headers.get("Content-Length", 0) or 0)
    raw = handler.rfile.read(length) if length > 0 else b""
    ctype = (handler.headers.get("Content-Type") or "").lower()
    if "application/json" in ctype and raw:
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return {}
    if "application/x-www-form-urlencoded" in ctype and raw:
        return {k: v[0] for k, v in parse_qs(raw.decode("utf-8")).items()}
    return {}


def _require_login(b_or_q):
    user = str((b_or_q.get("user") or "")).strip()
    pwd = str((b_or_q.get("password") or "")).strip()
    if not user or not pwd:
        return (False, user, pwd, "invalid credentials")
    u = auth.findUser(user)
    if u is None or u.get("password") != pwd:
        return (False, user, pwd, "wrong credentials")
    if u.get("session") is not True:
        return (False, user, pwd, "user not logged in")
    return (True, user, pwd, "ok")


class SupervisionHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stdout.write("%s - - [%s] " % (self.client_address[0], self.log_date_time_string()))
        sys.stdout.write((fmt % args) + "\n")

    # ------------------------
    # GET
    # ------------------------
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        q = {k: v[0] for k, v in parse_qs(parsed.query).items()}

        if path == "/health":
            return _json_response(self, 200, {"status": "ok"})

        # Requiere sesión en todo lo demás
        ok, user, pwd, msg = _require_login(q)
        if not ok:
            return _json_response(self, 401, {"error": msg})

        if path == "/list":
            try:
                data = supervision.listContracts()
                return _json_response(self, 200, {"contracts": data})
            except Exception as e:
                return _json_response(self, 500, {"error": str(e)})

        if path == "/search":
            try:
                number = (q.get("number") or "").strip()
                found = supervision.searchContract(number)
                if not found:
                    return _json_response(self, 404, {"error": "not found"})
                return _json_response(self, 200, found)
            except Exception as e:
                return _json_response(self, 500, {"error": str(e)})

        if path == "/tracking/list":
            try:
                number = (q.get("number") or "").strip()
                res = supervision.listTrackings(number)
                if isinstance(res, list):
                    return _json_response(self, 200, {"trackings": res})
                if res == "contract not found":
                    return _json_response(self, 404, {"error": res})
                return _json_response(self, 400, {"error": res})
            except Exception as e:
                return _json_response(self, 500, {"error": str(e)})

        if path == "/tracking/avg":
            try:
                number = (q.get("number") or "").strip()
                res = supervision.avgProgress(number)
                if isinstance(res, dict):
                    return _json_response(self, 200, res)
                if res == "contract not found":
                    return _json_response(self, 404, {"error": res})
                return _json_response(self, 400, {"error": res})
            except Exception as e:
                return _json_response(self, 500, {"error": str(e)})

        if path == "/stats":
            try:
                res = supervision.stats()
                return _json_response(self, 200, res)
            except Exception as e:
                return _json_response(self, 500, {"error": str(e)})

        return _json_response(self, 404, {"error": "unknown endpoint"})

    # ------------------------
    # POST
    # ------------------------
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        b = _read_body(self)

        # ---- Usuarios (NO requiere sesión) ----
        if path == "/user/register":
            try:
                msg = auth.registerUser(
                    str(b.get("user", "")).strip(),
                    str(b.get("password", "")).strip(),
                    str(b.get("role", "")).strip()
                )
                if msg == "ok":
                    return _json_response(self, 201, {"message": "registered"})
                if msg == "user exists":
                    return _json_response(self, 409, {"error": msg})
                return _json_response(self, 400, {"error": msg})
            except Exception as e:
                return _json_response(self, 500, {"error": str(e)})

        if path == "/user/session":
            try:
                flag = str(b.get("flag", "false")).strip().lower() == "true"
                msg = auth.openCloseSession(
                    str(b.get("user", "")).strip(),
                    str(b.get("password", "")).strip(),
                    flag
                )
                if msg == "ok":
                    return _json_response(self, 200, {"message": "session updated"})
                if msg == "wrong credentials":
                    return _json_response(self, 401, {"error": msg})
                return _json_response(self, 400, {"error": msg})
            except Exception as e:
                return _json_response(self, 500, {"error": str(e)})

        # ---- Resto requiere sesión ----
        ok, user, pwd, msg = _require_login(b)
        if not ok:
            return _json_response(self, 401, {"error": msg})

        if path == "/register":
            try:
                if not auth.hasRole(user, ("supervisor", "admin")):
                    return _json_response(self, 403, {"error": "unauthorized"})

                msg2 = supervision.registerContract(
                    str(b.get("number", "")).strip(),
                    str(b.get("contractor", "")).strip(),
                    str(b.get("object", "")).strip(),
                    str(b.get("start", "")).strip(),
                    str(b.get("end", "")).strip(),
                    str(b.get("value", "")).strip(),
                    str(b.get("supervisor", "")).strip(),
                    str(b.get("status", "")).strip(),
                    str(b.get("email", "")).strip(),
                )
                if msg2 == "ok":
                    return _json_response(self, 201, {"message": "registered"})
                if msg2 == "number already exists":
                    return _json_response(self, 409, {"error": msg2})
                return _json_response(self, 400, {"error": msg2})
            except Exception as e:
                return _json_response(self, 500, {"error": str(e)})

        if path == "/tracking/add":
            try:
                if not auth.hasRole(user, ("supervisor", "admin")):
                    return _json_response(self, 403, {"error": "unauthorized"})

                msg2 = supervision.addTracking(
                    str(b.get("number", "")).strip(),
                    str(b.get("date", "")).strip(),
                    str(b.get("desc", "")).strip(),
                    str(b.get("progress", "")).strip(),
                    str(b.get("obs", "")).strip(),
                )
                if msg2 == "ok":
                    return _json_response(self, 201, {"message": "added"})
                if msg2 == "contract not found":
                    return _json_response(self, 404, {"error": msg2})
                return _json_response(self, 400, {"error": msg2})
            except Exception as e:
                return _json_response(self, 500, {"error": str(e)})

        if path == "/export":
            try:
                if not auth.hasRole(user, ("admin",)):
                    return _json_response(self, 403, {"error": "unauthorized"})
                supervision.exportCsv()
                return _json_response(self, 200, {"message": "exported"})
            except Exception as e:
                return _json_response(self, 500, {"error": str(e)})

        return _json_response(self, 404, {"error": "unknown endpoint"})


if __name__ == "__main__":
    httpd = HTTPServer((HOST, PORT), SupervisionHandler)
    print(f"Supervision server running on http://{HOST}:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        httpd.server_close()