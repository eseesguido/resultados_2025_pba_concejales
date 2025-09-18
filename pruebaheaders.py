import requests

url = "https://resultados.eleccionesbonaerenses.gba.gob.ar/backend-difu/scope/data/getScopeDataMap/00000000000001d1e4e7b262/7/0/-1"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "es-419,es;q=0.9,en;q=0.8,it;q=0.7,gl;q=0.6",
    "Referer": "https://resultados.eleccionesbonaerenses.gba.gob.ar/resultados/2/9043/-1",
    "Origin": "https://resultados.eleccionesbonaerenses.gba.gob.ar",
    "Cookie": "_ga=GA1.1.2147232300.1744320354; _ga_FD1T68DDF3=GS1.1.1744320354.1.1.1744320803.20.0.0; _ga_1LC2CWY6VE=GS2.1.s1754851657$o1$g1$t1754851852$j60$l0$h0; _ga_YCMT9Y4XSM=GS2.1.s1757977788$o2$g1$t1757978006$j60$l0$h447930829; _ga_1Y379TMGM5=GS2.1.s1758214999$o9$g1$t1758215024$j35$l0$h0",
}

resp = requests.get(url, headers=headers)

print("Status:", resp.status_code)
print("Primeros 500 chars:")
print(resp.text[:500])
