#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import signal
import time
import datetime
import random
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont
from RPi import GPIO
import ftplib
import subprocess

# Configuración de la pantalla OLED I2C SSD1306 de 0.96 pulgadas
serial = i2c(port=1, address=0x3C)
disp = ssd1306(serial)

# Configuración de imagen
width = disp.width
height = disp.height
image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)

# Fuente para el texto
font = ImageFont.load_default()

# Configuración del botón
buttonPin = 26
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Datos del NAS
ftp_host = "192.168.50.100"  # Dirección IP del NAS
ftp_user = "usuario"         # Usuario del FTP
ftp_pass = "contraseña"      # Contraseña del FTP
ftp_video_dir = "/videos"    # Carpeta en el NAS con videos

# Variables globales
video_list = []
is_playing = False
player_process = None

def writeLog(myLine):
    now = datetime.datetime.now()
    dtFormatted = now.strftime("%Y-%m-%d %H:%M:%S")
    with open('log.txt', 'a') as f:
        myLine = str(dtFormatted) + "," + myLine
        f.write(myLine + "\n")

def updateScreen(message, time_elapsed=None, duration=None):
    # Limpiar la pantalla
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    
    # Mostrar el mensaje principal
    draw.text((0, 0), "Video Player", font=font, fill=255)
    draw.text((0, 16), f"{message}", font=font, fill=255)
    
    # Mostrar progreso si está disponible
    if time_elapsed is not None and duration is not None:
        draw.text((0, 26), f"Time: {time_elapsed}/{duration} min", font=font, fill=255)

    # Actualizar la pantalla
    disp.display(image)

def fetch_video_list():
    global video_list
    try:
        with ftplib.FTP(ftp_host) as ftp:
            ftp.login(ftp_user, ftp_pass)
            ftp.cwd(ftp_video_dir)
            video_list = ftp.nlst()
            print(f"Videos found: {video_list}")
    except Exception as e:
        print(f"Error fetching video list: {e}")
        video_list = []

def play_random_video():
    global player_process, is_playing

    if not video_list:
        print("No videos available to play.")
        updateScreen("No videos found")
        return

    # Seleccionar un video al azar
    random_video = random.choice(video_list)
    print(f"Playing: {random_video}")
    updateScreen(f"Playing: {random_video}")
    
    # Descargar el video temporalmente y reproducirlo
    try:
        with ftplib.FTP(ftp_host) as ftp:
            ftp.login(ftp_user, ftp_pass)
            ftp.cwd(ftp_video_dir)
            with open(random_video, "wb") as f:
                ftp.retrbinary(f"RETR {random_video}", f.write)
        
        # Reproducir con VLC en HDMI
        player_process = subprocess.Popen(
            ["vlc", "--fullscreen", "--no-video-title", random_video],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        is_playing = True
    except Exception as e:
        print(f"Error playing video: {e}")
        updateScreen("Error playing video")

def toggle_play_pause():
    global player_process, is_playing

    if player_process is None:
        play_random_video()
    else:
        if is_playing:
            print("Pausing video")
            updateScreen("Paused")
            player_process.send_signal(signal.SIGSTOP)
        else:
            print("Resuming video")
            updateScreen("Resuming")
            player_process.send_signal(signal.SIGCONT)
        is_playing = not is_playing

def signal_handler(sig, frame):
    print('Interrupted')
    writeLog("Interrupted")
    if player_process:
        player_process.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main(argv):
    print("Video Player with Button Control")
    writeLog("Started")

    # Inicializar pantalla y cargar lista de videos
    updateScreen("Fetching videos...")
    fetch_video_list()
    updateScreen("Ready. Press Button!")

    while True:
        button_state = GPIO.input(buttonPin)
        if button_state == GPIO.LOW:  # Botón presionado
            toggle_play_pause()
            time.sleep(0.3)  # Evitar rebotes

if __name__ == '__main__':
    main(sys.argv[1:])
