import os, re, requests, feedparser

TOKEN   = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
DESCUENTO_MINIMO = 10  # cambia este número si quieres más o menos filtro
ARCHIVO = "vistos.txt"

def enviar(texto):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": texto, "parse_mode": "HTML"},
        timeout=15
    )

def main():
    try:
        with open(ARCHIVO, encoding="utf-8") as f:
            vistos = set(f.read().splitlines())
    except:
        vistos = set()

    primera_vez = len(vistos) == 0

    feed = feedparser.parse("https://es.camelcamelcamel.com/top_drops/feed")

    if not feed.entries:
        print("Feed vacío o bloqueado")
        return

    nuevos = []
    for e in feed.entries:
        uid = e.get("id") or e.get("link", "")
        if not uid or uid in vistos:
            continue
        titulo = e.get("title", "")
        enlace = e.get("link", "")
        # Extraer porcentaje de bajada del título
        pct_match = re.search(r"(\d+)\s*%", titulo)
        pct = int(pct_match.group(1)) if pct_match else 0
        vistos.add(uid)
        if pct >= DESCUENTO_MINIMO:
            nuevos.append(f"📉 <b>Amazon.es</b> — bajada {pct}%\n{titulo}\n{enlace}")

    with open(ARCHIVO, "w", encoding="utf-8") as f:
        f.write("\n".join(list(vistos)[-3000:]))

    if primera_vez:
        enviar(f"✅ Vigilante activo. Avisaré solo de bajadas ≥{DESCUENTO_MINIMO}%.")
        print("Primera ejecución: memorizado sin avisar.")
        return

    for msg in nuevos:
        enviar(msg)
    print(f"Avisos enviados: {len(nuevos)}")

if __name__ == "__main__":
    main()
