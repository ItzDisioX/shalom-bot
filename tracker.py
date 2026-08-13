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
        print(f"Error enviando mensaje: {e}")

def consultar_estado():
    # URL actualizada para el rastreo oficial
    url = f"https://shalom.com.pe/rastrea/api/v1/tracking?numero={NRO_GUIA}&codigo={CODIGO_ENVIO}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get("status_name", "Desconocido")
    except Exception as e:
        print(f"Error consultando el sitio: {e}")
    return None

def ejecutar_monitoreo():
    print(f"Iniciando monitoreo continuo para guía {NRO_GUIA}...")
    while True:
        estado = consultar_estado()
        print(f"[{time.strftime('%H:%M:%S')}] Estado: {estado}")
        
        if estado and "DESTINO" in estado.upper():
            enviar_notificacion(f"🚨 ¡Tu pedido de Shalom (Guía {NRO_GUIA}) ya llegó a la agencia de destino!")
            print("Notificación enviada. Tarea finalizada.")
            break
            enviar_notificacion("🤖 Prueba: ¡El bot está activo y rastreando tu paquete!")
        time.sleep(1800)  # Revisa cada 30 minutos

if __name__ == "__main__":
    # Inicia el miniservidor web en segundo plano
    threading.Thread(target=run_web_server, daemon=True).start()
    # Inicia el monitoreo de Shalom
    def ejecutar_monitoreo():
    mensaje_inicio = f"🤖 Bot de Shalom activo. Rastreando guía {NRO_GUIA}..."
    print(mensaje_inicio, flush=True)
    
    # MANDA UN MENSAJE DE CONFIRMACIÓN AL INICIAR
    enviar_notificacion(mensaje_inicio)

    while True:
        estado = consultar_estado()
        print(f"[{time.strftime('%H:%M:%S')}] Estado actual: {estado}", flush=True)
        
        if estado and "DESTINO" in estado.upper():
            enviar_notificacion(f"🚨 ¡Tu pedido de Shalom (Guía {NRO_GUIA}) ya llegó a la agencia de destino!")
            print("Notificación de llegada enviada.", flush=True)
            break
            
        time.sleep(1800)  # Consulta cada 30 minutos
