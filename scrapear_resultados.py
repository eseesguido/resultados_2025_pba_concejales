#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
import time

STRUCTURE_FILE = "response_structure.json"
OUTPUT_FILE = "resultados.json"

# --- Si querés usar la cookie que probó y funcionó, pegala aquí (opcional).
# Recomiendo dejarla sólo para pruebas locales. Si la borrás, el script
# intentará obtener cookies automáticamente.
COOKIE_FALLBACK = ("_ga=GA1.1.2147232300.1744320354; "
                   "_ga_FD1T68DDF3=GS1.1.1744320354.1.1.1744320803.20.0.0; "
                   "_ga_1LC2CWY6VE=GS2.1.s1754851657$o1$g1$t1754851852$j60$l0$h0; "
                   "_ga_YCMT9Y4XSM=GS2.1.s1757977788$o2$g1$t1757978006$j60$l0$h447930829; "
                   "_ga_1Y379TMGM5=GS2.1.s1758214999$o9$g1$t1758215024$j35$l0$h0")

BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "es-419,es;q=0.9,en;q=0.8,it;q=0.7,gl;q=0.6",
    "Origin": "https://resultados.eleccionesbonaerenses.gba.gob.ar",
}

# --- Helper: extraer (i, c) de todas las mesas (l==70)
def extract_mesas_from_structure(structure):
    mesas = []  # list of dicts: {"i": ..., "c": ...}
    def rec(node):
        if isinstance(node, dict):
            if node.get("l") == 70:
                i = node.get("i")
                c = node.get("c")
                if i and c:
                    mesas.append({"i": i, "c": c})
            for v in node.values():
                rec(v)
        elif isinstance(node, list):
            for it in node:
                rec(it)
    rec(structure)
    return mesas

# --- Intentar conseguir cookies automáticamente (haciendo GET a la página principal)
def try_get_session_cookies():
    session = requests.Session()
    # headers para la session inicial
    session.headers.update({
        "User-Agent": BASE_HEADERS["User-Agent"],
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": BASE_HEADERS["Accept-Language"],
        "Referer": "https://resultados.eleccionesbonaerenses.gba.gob.ar/",
    })
    try:
        r = session.get("https://resultados.eleccionesbonaerenses.gba.gob.ar/resultados", timeout=10)
        # si la página respondió OK, retornamos la session (con cookies)
        if r.status_code == 200:
            return session
        else:
            return None
    except Exception:
        return None

# --- Construir headers para la petición de getScopeDataMap
def build_headers_for_mesa(telegram_numeric_id, cookie_string=None):
    headers = BASE_HEADERS.copy()
    headers["Referer"] = f"https://resultados.eleccionesbonaerenses.gba.gob.ar/resultados/2/{telegram_numeric_id}/-1"
    if cookie_string:
        headers["Cookie"] = cookie_string
    return headers

# --- Obtener resultados para una mesa (usa session si viene, sino requests.get con headers)
def fetch_mesa_results(hash_c, telegram_numeric_id, session=None, cookie_fallback=None):
    url = f"https://resultados.eleccionesbonaerenses.gba.gob.ar/backend-difu/scope/data/getScopeDataMap/{hash_c}/7/0/-1"
    # Si tenemos session (con cookies automáticas), usarlo
    if session:
        # actualizar headers dinámicos en la session (incluye Referer)
        session.headers.update(build_headers_for_mesa(telegram_numeric_id))
        try:
            r = session.get(url, timeout=10)
            return r.status_code, r
        except Exception as e:
            return None, e
    else:
        headers = build_headers_for_mesa(telegram_numeric_id, cookie_string=cookie_fallback)
        try:
            r = requests.get(url, headers=headers, timeout=10)
            return r.status_code, r
        except Exception as e:
            return None, e

# ---------------------------
# MAIN
# ---------------------------
if __name__ == "__main__":
    print("Leyendo structure desde", STRUCTURE_FILE)
    with open(STRUCTURE_FILE, "r", encoding="utf-8") as f:
        structure = json.load(f)

    mesas = extract_mesas_from_structure(structure)
    print(f"Mesas encontradas en el structure: {len(mesas)} (ej: primeros 3) ->", mesas[:3])

    # Intentamos obtener cookies automáticamente con session
    print("Intentando obtener cookies automáticamente con una session...")
    session = try_get_session_cookies()
    if session:
        print("Session iniciada: cookies obtenidas automáticamente.")
    else:
        print("No se pudieron obtener cookies automáticamente. Usaremos cookie fallback (la que pegaste).")

    resultados = {}
    total = len(mesas)
    for idx, m in enumerate(mesas, start=1):
        i = m["i"]   # telegram numeric id (para referer)
        c = m["c"]   # hash que va en la URL
        print(f"[{idx}/{total}] Consultando mesa i={i}  c={c} ...", end=" ")

        status, resp_or_exc = fetch_mesa_results(c, i, session=session, cookie_fallback=COOKIE_FALLBACK)

        # Manejo de respuesta
        if status == 200:
            try:
                json_data = resp_or_exc.json()
                resultados[str(i)] = json_data
                print("OK")
            except Exception as e:
                print("ERROR parseando JSON:", e)
        elif status == 403:
            print("403 Forbidden. Posible cookie vencida / bloqueo.")
            # si teníamos session, intentar con fallback de cookie (forzado)
            if session:
                print("Intento fallback con cookie manual...")
                # intentar sin session usando la cookie manual
                status2, resp2 = fetch_mesa_results(c, i, session=None, cookie_fallback=COOKIE_FALLBACK)
                if status2 == 200:
                    try:
                        resultados[str(i)] = resp2.json()
                        print("OK con fallback cookie")
                    except Exception as e:
                        print("ERROR parseando JSON en fallback:", e)
                else:
                    print(f"Fallback tambien falló: {status2}")
            else:
                print("Usá una cookie válida. Reemplazá COOKIE_FALLBACK por la cookie actual del navegador.")
        elif status is None:
            print("Error de conexión:", resp_or_exc)
        else:
            print(f"Status {status}. Respuesta corta:", getattr(resp_or_exc, "text", str(resp_or_exc))[:200])

        # anti-rate-limit: pausa pequeña para no bombardear el server
        time.sleep(0.25)

    # Guardar resultados
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

    print(f"Guardados {len(resultados)} resultados en {OUTPUT_FILE}")
    print("Si ves muchos 403, reemplaza COOKIE_FALLBACK con la cookie actual del navegador o vuelve a obtener cookies dinámicamente.")
