# randomVideosRaspberry
a simple code to play random videos from the NAS on my homelab

    FTP: Conexión al NAS para obtener la lista de videos disponibles.
    Reproducción: Al presionar el botón por primera vez, se descarga un video aleatorio y se reproduce con VLC.
    Pausa/Despausa: Posteriores presiones del botón pausan/despausan el video.
    Pantalla: Muestra el título del video y, durante la reproducción, el tiempo transcurrido frente al total.
    Logs: Se registran eventos como errores, reproducciones y estados de pausa.

Requisitos Previos

    Instalar VLC: sudo apt install vlc.
    Configurar correctamente el acceso al NAS con FTP.
    Asegurarse de que el directorio ftp_video_dir contiene videos en un formato reproducible por VLC.

Esto debe cumplir con tus requisitos y puede ser ajustado según los detalles adicionales del proyecto.
