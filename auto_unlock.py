#!/usr/bin/env python3
import hashlib
import json
import random
import time
from datetime import datetime, timezone, timedelta
from typing import Tuple, Callable, Optional, Dict
import urllib.parse
import sys
import os
import linecache

try:
    import urllib3
    import requests
    import ntplib
    import pytz
except ImportError:
    print("Instalando dependências...")
    os.system(sys.executable + " -m pip install requests ntplib pytz urllib3 --break-system-packages")
    os.execv(sys.executable, [sys.executable] + sys.argv)

# ---------------------------------------------------------
# CONSTANTS & CONFIGURATION
# ---------------------------------------------------------
BEIJING_TZ = pytz.timezone("Asia/Shanghai")
NTP_SERVERS = (
    "pool.ntp.org",
    "time.google.com",
    "ntp.aliyun.com"
)

APP_VERSION_CODE = '500411'
APP_VERSION_NAME = '5.4.11'
USER_AGENT = 'okhttp/4.12.0'
BASE_URL = "https://sgp-api.buy.mi.com/bbs/api/global"

# Garante que ele busque os arquivos na MESMA pasta do script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token.txt")
TIMESHIFT_FILE = os.path.join(SCRIPT_DIR, "timeshift.txt")

# ---------------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------------
def generate_device_id(rand_val: float, timestamp: float) -> str:
    data = f"{rand_val}-{timestamp}"
    return hashlib.sha1(data.encode('utf-8')).hexdigest().upper()

def build_headers(cookie_value: str, device_id: str, content_length: int = 0) -> Dict[str, str]:
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept-Encoding': 'gzip, deflate, br',
        'User-Agent': USER_AGENT,
        'Connection': 'keep-alive',
        'Cookie': f"new_bbs_serviceToken={cookie_value};versionCode={APP_VERSION_CODE};versionName={APP_VERSION_NAME};deviceId={device_id};"
    }
    if content_length > 0:
        headers['Content-Length'] = str(content_length)
    return headers

def fetch_ntp_time(server: str) -> Optional[datetime]:
    try:
        client = ntplib.NTPClient()
        response = client.request(server, version=3, timeout=2)
        return datetime.fromtimestamp(response.tx_time, timezone.utc)
    except Exception:
        return None

def fetch_http_time() -> Optional[datetime]:
    try:
        response = requests.get("http://worldtimeapi.org/api/timezone/Asia/Shanghai", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return datetime.fromisoformat(data['datetime'].replace('Z', '+00:00'))
    except Exception:
        return None

def get_beijing_time() -> datetime:
    print("[Tempo] Sincronizando horário exato de Pequim...")
    for server in NTP_SERVERS:
        ntp_time = fetch_ntp_time(server)
        if ntp_time:
            bj_time = ntp_time.astimezone(BEIJING_TZ)
            print(f"[Tempo NTP] {server}: {bj_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
            return bj_time
            
    http_time = fetch_http_time()
    if http_time:
        bj_time = http_time.astimezone(BEIJING_TZ)
        print(f"[Tempo HTTP] WorldTimeAPI: {bj_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
        return bj_time
        
    print("[Aviso] Usando hora do sistema local como fallback.")
    return datetime.now(timezone.utc).astimezone(BEIJING_TZ)

def check_account_status(pool: urllib3.PoolManager, cookie: str, device_id: str) -> Tuple[bool, str]:
    url = f"{BASE_URL}/user/bl-switch/state"
    headers = build_headers(cookie, device_id)
    try:
        response = pool.request('GET', url, headers=headers)
        data = json.loads(response.data.decode('utf-8'))
        
        if data.get("code") == 100004:
            return False, "Token/Cookie expirado. É necessário colar um novo no token.txt!"
            
        payload = data.get("data", {})
        is_pass = payload.get("is_pass")
        btn_state = payload.get("button_state")
        
        if is_pass == 4:
            if btn_state == 1:
                return True, "Conta 100% pronta para envio."
            elif btn_state in (2, 3):
                return True, f"Modo Restrito (Estado {btn_state}). O script continuará e fará o envio mesmo assim (Modo Automático)."
        elif is_pass == 1:
            return False, "O desbloqueio já foi aprovado anteriormente!"
            
        return False, f"Estado desconhecido: {data}"
    except Exception as e:
        return False, f"Erro checando status: {e}"

def wait_until(target_time: datetime, get_current_time: Callable[[], datetime]):
    print(f"\n[Aguardando] O script ficará dormente até exatamente: {target_time.strftime('%Y-%m-%d %H:%M:%S.%f')} (Fuso de Pequim)")
    print("Você pode ir dormir. O computador fará o envio automático no milissegundo correto.")
    
    while True:
        now = get_current_time()
        diff = (target_time - now).total_seconds()
        
        if diff > 10:
            time.sleep(5)  # Dorme mais longo para não gastar CPU
        elif diff > 1:
            time.sleep(0.5)
        elif diff > 0:
            pass # Busy-wait no último segundo para precisão absoluta (milissegundo)
        else:
            break

def main():
    print("=== Auto-Unlock MIUI/HyperOS (Pasta Dedicada) ===")
    
    try:
        if not os.path.exists(TOKEN_FILE):
            print(f"[Erro] O arquivo {TOKEN_FILE} não existe!")
            return

        raw_token = linecache.getline(TOKEN_FILE, 2).strip()
        if not raw_token:
            print("[Erro] Token não encontrado na linha 2 do arquivo token.txt.")
            print("Verifique se o token foi colado corretamente.")
            return
            
        cookie_value = raw_token.strip()
        
        try:
            offset_ms = float(linecache.getline(TIMESHIFT_FILE, 1).strip())
        except:
            offset_ms = 0.0
            
        device_id = generate_device_id(random.random(), time.time())
        
        pool = urllib3.PoolManager(maxsize=50)

        # Verificação inicial
        print("\nVerificando status inicial...")
        try:
            r = pool.request('GET', f"{BASE_URL}/user/bl-switch/state", headers=build_headers(cookie_value, device_id))
            r_data = json.loads(r.data.decode('utf-8'))
            if r_data.get("code") == 100004:
                print("Status: Token/Cookie expirado. É necessário colar um novo no token.txt!")
                print("Execução interrompida por não estar apta (token expirado ou já aprovada).")
                return
            print("Status: Conta 100% pronta para envio.")
        except Exception as e:
            print(f"Status: Erro checando status: {e}")
            return
            
        start_bj_time = get_beijing_time()
        start_local_time = time.time()
        
        def get_synced_time() -> datetime:
            return start_bj_time + timedelta(seconds=(time.time() - start_local_time))
            
        # Calcula a meta
        next_day = start_bj_time + timedelta(days=1)
        midnight = next_day.replace(hour=0, minute=0, second=0, microsecond=0)
        target_time = midnight - timedelta(milliseconds=offset_ms)
        
        # Inicia a espera até 10 segundos antes para o Pre-Warm
        warmup_time = target_time - timedelta(seconds=10)
        if (warmup_time - get_synced_time()).total_seconds() > 0:
            wait_until(warmup_time, get_synced_time)
            
        print("\n[PRE-WARM] Aquecendo conexões TLS para eliminar atraso de handshake...")
        # Cria 20 conexões simultâneas e as mantém vivas (keep-alive)
        import concurrent.futures
        def warmup_req(_):
            try:
                pool.request('GET', f"{BASE_URL}/user/bl-switch/state", headers=build_headers(cookie_value, device_id), timeout=2.0)
            except:
                pass
                
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            for i in range(20):
                executor.submit(warmup_req, i)
                
        # Agora aguarda o milissegundo final
        wait_until(target_time, get_synced_time)
        
        print("\n[DISPARO] Enviando chuva de solicitações para garantir...")
        body = b'{"is_retry":true}'
        
        import concurrent.futures
        
        def send_req(i):
            now = get_synced_time()
            url = f"{BASE_URL}/apply/bl-auth"
            headers = build_headers(cookie_value, device_id, len(body))
            try:
                # Diminuindo o timeout para as threads não ficarem presas à toa
                response = pool.request('POST', url, headers=headers, body=body, preload_content=False, timeout=urllib3.Timeout(connect=2.0, read=2.0))
                data = response.read()
                response.release_conn()
                
                result = json.loads(data.decode('utf-8'))
                code = result.get("code")
                r_data = result.get("data", {})
                
                print(f"[{now.strftime('%H:%M:%S.%f')}] Req {i+1}: Code {code}")
                
                if code == 0:
                    apply_result = r_data.get("apply_result")
                    if apply_result == 1:
                        print(f"\n[SUCESSO ABSOLUTO Req {i+1}] Solicitação aprovada com sucesso!")
                        return True
                    elif apply_result in (3, 4):
                        print(f"[{now.strftime('%H:%M:%S.%f')}] Req {i+1}: Limite esgotado.")
                elif code == 100003:
                    print(f"\n[PENDENTE Req {i+1}] Resposta 100003. Foi enviado e provavelmente aprovado na fila.")
                    return True
            except Exception as e:
                print(f"Falha na requisição {i+1}: {e}")
            return False

        # Dispara as 200 requisições usando múltiplas threads para não travar
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = []
            for i in range(200):
                futures.append(executor.submit(send_req, i))
                time.sleep(0.01) # Espaça os tiros a cada 10 milissegundos
            
            # Aguarda terminar ou acha um sucesso
            for future in concurrent.futures.as_completed(futures):
                if future.result():
                    break
                    
        print("\n=== Rotina Concluída ===")
        
    except Exception as e:
        print(f"\n[ERRO FATAL] Ocorreu um erro na automação: {e}")

if __name__ == "__main__":
    main()
