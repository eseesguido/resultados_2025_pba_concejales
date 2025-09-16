import requests
import json

# URL para obtener el listado de todos los IDs de telegrama
nomenclator_url = "https://resultados.eleccionesbonaerenses.gba.gob.ar/backend-difu/nomenclator/getNomenclator"

# Encabezados para que la petición parezca un navegador
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

def get_telegram_ids():
    """
    Obtiene la lista de todos los IDs de telegrama de la API.
    """
    print("Obteniendo la lista de IDs de telegrama...")
    try:
        response = requests.get(nomenclator_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(data) 

            
            # --- LÍNEA PARA DEBUGGING ---
            # Descomenta esta línea para ver la estructura completa de los datos
            # print("Estructura de la respuesta:", data)
            
            # --- CAMBIO CLAVE: USAMOS LA CLAVE CORRECTA ---
            ids = [item['idTelegrama'] for item in data['result']]
            print(f"Lista de IDs obtenida. Total: {len(ids)}")
            return ids
        else:
            print(f"Error {response.status_code} al obtener la lista de IDs.")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Ocurrió un error de conexión: {e}")
        return []

# Ejemplo de uso:
if __name__ == "__main__":
    telegram_ids = get_telegram_ids()
    if telegram_ids:
        print("Primeros 5 IDs:", telegram_ids[:5])