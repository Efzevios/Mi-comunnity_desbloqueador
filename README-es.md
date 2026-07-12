[Português](README.md) | [English](README-en.md) | [Español](README-es.md)

# MIUI Auto Unlock

Script en Python para automatizar la solicitud de desbloqueo del Bootloader en Xiaomi Community (MIUI/HyperOS).
El script se ejecuta de forma automática, eludiendo el límite diario de cupos que se reinicia a las 00:00:00 (hora de Beijing). Maneja automáticamente la compensación de ping y abre múltiples hilos (threads) para no perder la ventana de tiempo.

## Requisitos
- Linux (Systemd)
- Python 3.x
- Navegador con sesión iniciada en Xiaomi Community Global para obtener el token

## Instalación

1. Clona el repositorio en tu ordenador:
   ```bash
   git clone https://github.com/TU_USUARIO/miui-auto-unlock.git ~/Github/Pessoal/Mi-comunnity_desbloqueador
   ```
2. El script instala las dependencias de Python automáticamente (requests, ntplib, pytz, urllib3) si no las tienes.

## Cómo Usar

### 1. Obteniendo el Token de Sesión
Para que el script funcione, necesita estar autenticado en tu cuenta.
1. Accede al sitio oficial: `https://new-ams.c.mi.com/global` e inicia sesión.
2. Abre las Herramientas de Desarrollador (F12) en el navegador.
3. Ve a la pestaña **Storage** (Almacenamiento) > **Cookies**.
4. Busca la cookie llamada `new_bbs_serviceToken`.
5. Copia el valor de esta cookie y pégalo dentro del archivo `token.txt` en la carpeta del script, reemplazando el texto `COLE_SEU_TOKEN_AQUI`.

*(Nota: El token suele caducar en unas 24 horas, por lo que se recomienda actualizarlo diariamente antes de la medianoche de China).*

### 2. Configurando el Timeshift
El archivo `timeshift.txt` sirve para compensar tu Ping (latencia) de comunicación hasta China, disparando el script un poco antes para que llegue al servidor en el milisegundo exacto.
El valor predeterminado que dejamos es `351.0` (en milisegundos). Puedes cambiar este archivo si conoces el ping exacto de tu servidor, pero el valor por defecto suele funcionar bien para conexiones normales.

### 3. Ejecutando el Script

Puedes ejecutarlo manualmente:
```bash
python3 auto_unlock.py
```

O, para no tener que dejar la terminal abierta, recomiendo configurar el script como un servicio del sistema para que se ejecute en segundo plano:

1. Crea el archivo de servicio en `~/.config/systemd/user/miui-unlock.service` con el siguiente contenido:

```ini
[Unit]
Description=MIUI Auto Unlock Script

[Service]
Type=simple
ExecStart=/usr/bin/python3 -u %h/Github/Pessoal/Mi-comunnity_desbloqueador/auto_unlock.py
Restart=on-failure
RestartSec=60

[Install]
WantedBy=default.target
```

2. Activa e inicia el servicio:
```bash
systemctl --user daemon-reload
systemctl --user enable --now miui-unlock.service
```

El script se quedará inactivo y esperará la hora correcta para dispararse. Siempre que coloques un nuevo token en `token.txt`, solo tienes que ejecutar `systemctl --user restart miui-unlock.service` para recargar.

---
**Aviso Legal:**
Esta herramienta ha sido creada para uso y estudio personal. No hay garantías de funcionamiento debido a los cambios constantes en los servidores de Xiaomi. Úsalo bajo tu propio riesgo.
