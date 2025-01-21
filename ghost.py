import configparser
import time
import requests
import re

# Leer configuración desde ghost.ini
def cargar_configuracion(config_path="ghost.ini"):
    config = configparser.ConfigParser()
    config.read(config_path)
    return {
        "discord_webhook": config.get("SETTINGS", "discord"),
        "message_template_game": config.get("SETTINGS", "messagecreate"),
        "message_template_player": config.get("SETTINGS", "messageplayer"),
        "message_template_leave": config.get("SETTINGS", "messagetoleave")
    }

# Enviar mensaje al webhook de Discord
def enviar_webhook(webhook_url, mensaje):
    try:
        response = requests.post(webhook_url, json={"content": mensaje})
        if response.status_code != 204:
            print(f"Error al enviar al webhook: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error al enviar el mensaje al webhook: {e}")

# Leer el archivo log de manera continua
def monitorear_log(ruta_log, config):
    try:
        with open(ruta_log, "r") as archivo:
            # Ir al final del archivo
            archivo.seek(0, 2)
            while True:
                linea = archivo.readline()
                if not linea:
                    time.sleep(0.1)
                    continue
                procesar_linea(linea, config)
    except FileNotFoundError:
        print(f"Archivo no encontrado: {ruta_log}")
    except Exception as e:
        print(f"Error al monitorear el log: {e}")

# Procesar cada línea del log
def procesar_linea(linea, config):
    # Detectar partidas creadas
    match_game = re.search(r"creating game \[(.*)\]", linea)
    if match_game:
        nombre_partida = match_game.group(1)  # Extraer directamente el contenido de los corchetes
        mensaje = config["message_template_game"].replace("{game_name}", nombre_partida)
        enviar_webhook(config["discord_webhook"], mensaje)

    # Detectar jugadores que se conectan
    match_player = re.search(r"player \[(.*)\|(.+?)\] joined the game", linea)
    if match_player:
        usuario = match_player.group(1)  # Extraer el nombre del usuario
        ip = match_player.group(2)       # Extraer la IP
        mensaje = config["message_template_player"].replace("{user}", usuario).replace("{ip}", ip)
        enviar_webhook(config["discord_webhook"], mensaje)

    # Detectar jugadores que abandonan la partida
    match_leave = re.search(r"deleting player \[(.*)\]:", linea)
    if match_leave:
        usuario = match_leave.group(1)  # Extraer el nombre del usuario
        mensaje = config["message_template_leave"].replace("{user}", usuario)
        enviar_webhook(config["discord_webhook"], mensaje)

    # Detectar mensajes de chat en el lobby
    match_chat = re.search(r"\[Lobby\] (.+)", linea)
    if match_chat:
        mensaje_chat = match_chat.group(0)  # Capturar todo desde [Lobby] en adelante
        enviar_webhook(config["discord_webhook"], mensaje_chat)

if __name__ == "__main__":
    ruta_log = "C:/Games/logs/d2abot.log"
    config_path = "ghost.ini"

    config = cargar_configuracion(config_path)

    print("LatinBattle.com - Iniciando monitoreo del log...")
    monitorear_log(ruta_log, config)
