import os
import time
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- MINISERVIDOR PARA ENGAÑAR A RENDER FREE ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Bot Shalom activo y corriendo!")

    def log_message(self, format, *args):
        return  # Desactiva logs molestos del servidor HTTP en la consola

def iniciar_servidor_web():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    print(f"Servidor web iniciado en puerto {port}", flush=True)
    server.serve_forever()

# --- DATOS DE CONFIGURACIÓN ---
NRO_GUIA = os.getenv("NRO_GUIA", "91465467")
CODIGO_ENVIO = os.getenv("CODIGO_ENVIO", "339J")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8814913036:AAFa2NxxAfdoLaTLokSs9YUwjP1rchmlCiU")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "7078514318")

def enviar_notificacion(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error enviando mensaje a Telegram: {e}", flush=True)

def consultar_estado():
    url = f"https://shalom.com.pe/rastrea/api/v1/tracking?numero={NRO_GUIA}&codigo={CODIGO_ENVIO}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://shalom.com.pe/rastrea/"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return str(data[0].get("status_name", "Desconocido")).strip()
            elif isinstance(data, dict):
                estado = data.get("status_name") or data.get("estado") or data.get("status")
                if estado:
                    return str(estado).strip()
        else:
            print(f"Respuesta HTTP {response.status_code} de Shalom", flush=True)
    except Exception as e:
        print(f"Error en consulta: {e}", flush=True)
    return None

def ejecutar_monitoreo():
    print(f"Iniciando monitoreo para guía {NRO_GUIA}...", flush=True)
    
    # Notificación al arrancar para saber que el bot despertó
    enviar_notificacion(f"🤖 *Bot de Shalom activo.*\nRastreando guía `{NRO_GUIA}`")
    
    ultimo_estado = None

    while True:
        try:
            estado_actual = consultar_estado()
            
            if estado_actual:
                print(f"[{time.strftime('%H:%M:%S')}] Estado detectado: '{estado_actual}'", flush=True)
                
                if ultimo_estado is None:
                    ultimo_estado = estado_actual
                elif estado_actual.upper() != ultimo_estado.upper():
                    mensaje = f"📦 *¡CAMBIO EN TU PAQUETE DE SHALOM!*\n\nGuía: `{NRO_GUIA}`\nAnterior: {ultimo_estado}\n👉 Nuevo Estado: *{estado_actual}*"
                    enviar_notificacion(mensaje)
                    print(f"Cambio notificado: {ultimo_estado} -> {estado_actual}", flush=True)
                    ultimo_estado = estado_actual
                    
                    if any(kw in estado_actual.upper() for kw in ["ENTREGADO", "RECOGIDO", "FINALIZADO"]):
                        enviar_notificacion(f"✅ Encomienda {NRO_GUIA} entregada. Monitoreo finalizado.")
                        break
            else:
                print(f"[{time.strftime('%H:%M:%S')}] Estado no disponible en este intento.", flush=True)
        except Exception as err:
            print(f"Error inesperado en el bucle: {err}", flush=True)

        time.sleep(1800)  # Consulta cada 30 minutos

if __name__ == "__main__":
    # Iniciar servidor web en segundo plano
    t = threading.Thread(target=iniciar_servidor_web)
    t.daemon = True
    t.start()

    # Iniciar ciclo principal de rastreo
    ejecutar_monitoreo()
