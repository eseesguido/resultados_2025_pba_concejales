import json
import requests

# Encabezados para que la petición parezca un navegador
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

# Cargar el archivo con la estructura jerárquica
with open("response_structure.json", "r", encoding="utf-8") as f:
    data = json.load(f)

def find_hash_by_telegram_id(telegram_id, data):
    """
    Busca dentro de response_structure.json el 'c' (hash) asociado al telegram_id (i).
    """
    def recursive_search(node):
        if isinstance(node, dict):
            if node.get("l") == 70 and node.get("i") == telegram_id:
                return node.get("c")  # usamos 'c' porque ya vimos que guarda el hash
            for v in node.values():
                result = recursive_search(v)
                if result:
                    return result
        elif isinstance(node, list):
            for item in node:
                result = recursive_search(item)
                if result:
                    return result
        return None

    return recursive_search(data)

def get_results_by_telegram_id(telegram_id):
    """
    Dado un telegram_id, encuentra el hash y consulta los resultados de esa mesa.
    """
    hash_id = find_hash_by_telegram_id(telegram_id, data)
    if not hash_id:
        print(f"No encontré hash para telegram_id {telegram_id}")
        return None

    url = f"https://resultados.eleccionesbonaerenses.gba.gob.ar/backend-difu/scope/data/getScopeDataMap/{hash_id}/7/0/-1"
    print(f"Consultando: {url}")

    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json()
    else:
        print(f"Error {resp.status_code} al consultar resultados")
        return None

if __name__ == "__main__":
    telegram_id = 9037  # podés cambiarlo por cualquiera de telegram_ids.json
    results = get_results_by_telegram_id(telegram_id)
    if results:
        # Mostrar un preview de los resultados
        print(json.dumps(results, indent=2, ensure_ascii=False)[:1500])
