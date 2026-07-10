# MIUI/HyperOS Auto Unlock Sniper 🎯

Um bot metralhadora assíncrono projetado para contornar o caótico sistema de cotas diárias de desbloqueio de Bootloader da Xiaomi (MIUI/HyperOS).

## O Problema
A Xiaomi liberou um sistema de cota na MIUI Community Global. A vaga zera exatamente às **00:00:00 (Horário de Pequim)**. No entanto, por causa de milhões de bots mundialmente:
1. Se você enviar sua requisição 1 milissegundo depois, a cota já esgotou.
2. O servidor sofre um colapso (DDoS natural) à meia-noite, causando lentidão e rejeitando handshakes TLS. Scripts comuns que enviam a requisição exato na meia-noite acabam sofrendo de Timeouts e perdem a vaga.

## A Solução (Como este script domina o servidor)
Este bot utiliza três artifícios técnicos letais para garantir a vaga:
1. **NTP Timeshift Compensation (Compensação de Ping)**: O script sincroniza milimetricamente com os servidores NTP e mede o atraso de rede (ping) em relação à China (geralmente ~351ms). A requisição é disparada com o tempo *adiantado*, fazendo com que os dados pousem no servidor da Xiaomi em exatos `00:00:00.000`.
2. **TLS Pre-Warm (Pré-Aquecimento de Túnel)**: O maior gargalo não é o ping, mas sim o *Handshake TLS* (Aperto de mão de criptografia) que consome ~1 segundo na primeira requisição e trava o script no horário de pico. Esse script resolve isso conectando silenciosamente ao servidor **10 segundos antes** da meia-noite, abrindo e mantendo "vivas" dezenas de conexões.
3. **Metralhadora Multithread**: No exato milissegundo planejado, o script libera 50 threads que descarregam dezenas de requisições através dos túneis abertos sem a necessidade de negociar o TLS, atropelando o servidor imune a lags síncronos.

## Requisitos
- Linux (testado em distribuições rodando `systemd`)
- Python 3.x
- Firefox / Chrome (para captura do token)

## Instalação
1. Clone este repositório no seu computador:
   ```bash
   git clone https://github.com/SEU_USUARIO/miui-auto-unlock.git ~/Desbloqueio_MIUI
   ```
2. Instale as bibliotecas Python se necessário (o script auto-instala se você rodá-lo, mas garanta que pip está instalado).
3. O `timeshift.txt` vem configurado com `351.0` ms por padrão, ajuste se souber o ping exato do seu servidor.

## Como Usar

### 1. Pegando o seu Token
Você precisa copiar o token `new_bbs_serviceToken` da comunidade Xiaomi global para o arquivo `token.txt`.
- Acesse `https://new-ams.c.mi.com/global` pelo navegador (no PC ou celular).
- Faça login na conta.
- Abra o painel de desenvolvedor (F12) > Storage > Cookies.
- Copie o valor do cookie `new_bbs_serviceToken` e cole dentro do arquivo `token.txt`. 

### 2. Automatizando com o Sistema (Recomendado)
O bot funciona melhor se você configurá-lo como um Serviço nativo do Sistema para que ele rode 100% autônomo.
Crie um serviço de usuário do systemd em `~/.config/systemd/user/miui-unlock.service` com o seguinte conteúdo (Lembre de trocar o caminho se não estiver em Desbloqueio_MIUI):

```ini
[Unit]
Description=MIUI Auto Unlock Script

[Service]
Type=simple
ExecStart=/usr/bin/python3 -u %h/Desbloqueio_MIUI/auto_unlock.py
Restart=on-failure
RestartSec=60

[Install]
WantedBy=default.target
```
Rode os seguintes comandos para ativá-lo:
```bash
systemctl --user daemon-reload
systemctl --user enable --now miui-unlock.service
```

### 3. Lembretes (Opcional)
Se precisar ser lembrado todo dia às 12:00 de colocar um token novo, inclua um Timer Systemd apontando para o arquivo `lembrete.sh`.

## Aviso Legal
Esta ferramenta tem propósitos de pesquisa educacional para análise de tráfego assíncrono. Não me responsabilizo por proibições da conta efetuadas pela própria fabricante.
