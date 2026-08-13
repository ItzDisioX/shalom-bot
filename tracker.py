import os
import time
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- MINISERVIDOR PARA RENDER FREE ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Bot de Shalom corriendo exitosamente!")

def run_web_server():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

# --- CONFIGURACIÓN DE TU RASTREADOR ---
NRO_GUIA = os.getenv("NRO_GUIA", "91465467")
CODIGO_ENVIO = os.getenv("CODIGO_ENVIO", "339J")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8814913036:AAFa2NxxAfdoLaTLokSs9YUwjP1rchmlCiU")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "7078514318")

def enviar_notificacion(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error enviando mensaje: {e}", flush=True)

def consultar_estado():
    url = f"https://shalom.com.pe/rastrea/api/v1/tracking?numero={NRO_GUIA}&codigo={CODIGO_ENVIO}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://shalom.com.pe/rastrea/"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            # Si la API devuelve una lista o dict
            if isinstance(data, list) and len(data) > 0:
                return data[0].get("status_name", "Desconocido")
            elif isinstance(data, dict):
                return data.get("status_name") or data.get("estado") or "Desconocido"
        else:
            print(f"Respuesta HTTP {response.status_code} de Shalom", flush=True)
    except Exception as e:
        print(f"Error consultando el sitio: {e}", flush=True)
    return None

def ejecutar_monitoreo():
    mensaje_inicio = f"🤖 Bot de Shalom activo. Rastreando guía {NRO_GUIA}..."
    print(mensaje_inicio, flush=True)
    enviar_notificacion(mensaje_inicio)

    while True:
        estado = consultar_estado()
        print(f"[{time.strftime('%H:%M:%S')}] Estado actual: {estado}", flush=True)
        
        if estado and "DESTINO" in estado.upper():
            enviar_notificacion(f"🚨 ¡Tu pedido de Shalom (Guía {NRO_GUIA}) ya llegó a la agencia de destino!")
            print("Notificación enviada.", flush=True)
            break
            
        time.sleep(1800)  # Revisa cada 30 minutos

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    ejecutar_monitoreo()
