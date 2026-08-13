import os
import time
import requests

# Lee las variables del entorno del servidor por seguridad
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
    url = f"https://rastrea.shalom.pe/api/v1/tracking?numero={NRO_GUIA}&codigo={CODIGO_ENVIO}"
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
            
        time.sleep(1800)  # Revisa cada 30 minutos

if __name__ == "__main__":
    ejecutar_monitoreo()