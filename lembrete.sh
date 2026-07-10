#!/bin/bash

# Garante que as variáveis gráficas estejam disponíveis
export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$(id -u)/bus"
export WAYLAND_DISPLAY=${WAYLAND_DISPLAY:-wayland-1}
export DISPLAY=${DISPLAY:-:0}

if zenity --question --title="Lembrete: Desbloqueio MIUI" \
    --text="Falta pouco para as 13:00!\n\nVocê precisa pegar o novo token da MIUI Community para garantir que o script funcione hoje.\n\nDeseja abrir o site agora?" \
    --ok-label="Abrir Firefox" \
    --cancel-label="Mais Tarde"; then
    
    firefox "https://new-ams.c.mi.com/global"
fi
