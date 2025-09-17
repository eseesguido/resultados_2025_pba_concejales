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
            
            # Mostrar las claves principales para debugging
            print("Claves principales en la respuesta:", list(data.keys()))
            
            # Analizar la estructura de 'amb' que parece contener los datos
            if 'amb' in data and len(data['amb']) > 0:
                print("Estructura del primer elemento de 'amb':", list(data['amb'][0].keys()))
                
                # Veamos qué hay en 'ambitos'
                first_amb = data['amb'][0]
                if 'ambitos' in first_amb:
                    print("Primer elemento de 'ambitos':", first_amb['ambitos'][:3] if len(first_amb['ambitos']) > 3 else first_amb['ambitos'])
                    if len(first_amb['ambitos']) > 0:
                        print("Estructura de un elemento de 'ambitos':", list(first_amb['ambitos'][0].keys()))
                
                # Buscar IDs de telegrama en la nueva estructura
                telegram_ids = []
                
                for amb_item in data['amb']:
                    if 'ambitos' in amb_item:
                        for ambito in amb_item['ambitos']:
                            # Buscar en diferentes posibles ubicaciones
                            if 'm' in ambito:  # Si 'm' está en este nivel
                                for mesa in ambito['m']:
                                    if 'i' in mesa:
                                        telegram_ids.append(mesa['i'])
                            elif 'i' in ambito and 'l' in ambito:  # Si el ambito mismo es una mesa
                                if ambito['l'] == 70:  # Nivel 70 = Mesa según 'levels'
                                    telegram_ids.append(ambito['i'])
                
                print(f"Total de IDs encontrados: {len(telegram_ids)}")
                return telegram_ids
            else:
                print("No se encontró la estructura esperada en la respuesta")
                return []
            
        else:
            print(f"Error {response.status_code} al obtener la lista de IDs.")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Ocurrió un error de conexión: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {e}")
        return []
    except KeyError as e:
        print(f"Error: Clave no encontrada: {e}")
        print("Estructura completa de la respuesta:")
        print(json.dumps(data, indent=2)[:1000] + "..." if len(json.dumps(data, indent=2)) > 1000 else json.dumps(data, indent=2))
        return []

def save_structure_to_file(data, filename="response_structure.json"):
    """
    Guarda la estructura completa de la respuesta en un archivo para análisis
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Estructura guardada en {filename}")
    except Exception as e:
        print(f"Error al guardar archivo: {e}")

# Ejemplo de uso mejorado:
if __name__ == "__main__":
    print("Iniciando scraping de datos electorales...")
    
    try:
        response = requests.get(nomenclator_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            
            # Guardar la estructura completa para análisis
            save_structure_to_file(data)
            
            # Obtener IDs
            telegram_ids = get_telegram_ids()
            
            if telegram_ids:
                print("Primeros 10 IDs:", telegram_ids[:10])
                print("Últimos 5 IDs:", telegram_ids[-5:])
                
                # Guardar los IDs en un archivo
                with open("telegram_ids.json", "w") as f:
                    json.dump(telegram_ids, f)
                print(f"IDs guardados en telegram_ids.json")
            else:
                print("No se pudieron obtener los IDs")
        else:
            print(f"Error {response.status_code} en la petición inicial")
            
    except Exception as e:
        print(f"Error general: {e}")