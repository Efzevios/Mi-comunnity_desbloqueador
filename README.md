[Português](README.md) | [English](README-en.md) | [Español](README-es.md)

# MIUI Auto Unlock
Script em Python para automatizar a solicitação de desbloqueio do Bootloader na Xiaomi Community (MIUI/HyperOS).
O script roda de forma automática, contornando o limite diário de vagas que reseta às 00:00:00 (horário de Pequim). Ele lida automaticamente com compensação de ping e abre múltiplas threads para não perder a janela de tempo.

## Requisitos
- Linux (Systemd)
- Python 3.x
- Navegador logado na Xiaomi Community Global para pegar o token

## Instalação

1. Clone o repositório no seu computador:
   ```bash
   git clone https://github.com/SEU_USUARIO/miui-auto-unlock.git ~/Github/Pessoal/Mi-comunnity_desbloqueador
   ```
2. O script instala as dependências Python automaticamente (requests, ntplib, pytz, urllib3) caso você não as tenha.

## Como Usar

### 1. Obtendo o Token de Sessão
Para que o script funcione, ele precisa estar autenticado na sua conta.
1. Acesse o site oficial: `https://new-ams.c.mi.com/global` e faça o login.
2. Abra as Ferramentas de Desenvolvedor (F12) no navegador.
3. Vá na aba **Storage** (Armazenamento) > **Cookies**.
4. Procure pelo cookie chamado `new_bbs_serviceToken`.
5. Copie o valor desse cookie e cole-o dentro do arquivo `token.txt` na pasta do script, substituindo o texto `COLE_SEU_TOKEN_AQUI`.

*(Nota: O token costuma expirar em cerca de 24 horas, portanto é recomendado atualizar o token diariamente antes da meia-noite da China - 13:00 no horário de Brasília).*

### 2. Configurando o Timeshift
O arquivo `timeshift.txt` serve para compensar o seu Ping (latência) de comunicação até a China, disparando o script um pouco antes para que ele chegue no servidor no milissegundo exato.
O valor padrão que deixamos é `351.0` (em milissegundos). Você pode alterar esse arquivo se souber o ping exato do seu servidor, mas o padrão costuma funcionar bem para conexões normais.

### 3. Rodando o Script

Você pode rodar manualmente:
```bash
python3 auto_unlock.py
```

Ou, para não precisar deixar o terminal aberto, recomendo configurar o script como um serviço do sistema para rodar em segundo plano:

1. Crie o arquivo de serviço em `~/.config/systemd/user/miui-unlock.service` com o conteúdo abaixo:

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

2. Ative e inicie o serviço:
```bash
systemctl --user daemon-reload
systemctl --user enable --now miui-unlock.service
```

O script ficará dormindo e aguardará o horário correto para disparar. Sempre que você colocar um token novo no `token.txt`, basta rodar `systemctl --user restart miui-unlock.service` para recarregar.

---
**Aviso Legal:**
Esta ferramenta foi feita para uso e estudo próprio. Não há garantias de funcionamento devido a mudanças constantes nos servidores da Xiaomi. Use por sua conta e risco.
