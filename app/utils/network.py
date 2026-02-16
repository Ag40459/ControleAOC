import socket
import requests
import json
import os

# Caminho para salvar nomes personalizados das TVs
DATA_FILE = "tv_data.json"

def get_local_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def scan_single_ip(ip_address, tv_port=1925, timeout=1):
    url = f"http://{ip_address}:{tv_port}/1/system"
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            try:
                data = response.json()
                name = data.get('name', ip_address)
                # Verifica se temos um nome personalizado salvo
                custom_name = get_custom_name(ip_address)
                return (ip_address, custom_name if custom_name else name)
            except:
                return (ip_address, ip_address)
    except:
        pass
    return None

def send_tv_command(ip, port, cmd):
    try:
        url = f"http://{ip}:{port}/1/input/key"
        requests.post(url, json={'key': cmd}, timeout=1)
        return True
    except:
        return False

def send_tv_text(ip, port, text):
    """
    Envia texto para a TV. Tenta o endpoint de texto e, se falhar, 
    pode ser expandido para outros métodos.
    """
    try:
        # Tenta o endpoint de texto do JointSpace (comum em modelos mais novos)
        url = f"http://{ip}:{port}/1/input/text"
        res = requests.post(url, json={'text': text}, timeout=1)
        if res.status_code == 200:
            return True
        
        # Se falhar, tenta enviar como tecla individual (fallback)
        # Nota: Algumas TVs aceitam o caractere diretamente no campo 'key'
        url_key = f"http://{ip}:{port}/1/input/key"
        requests.post(url_key, json={'key': text}, timeout=1)
        return True
    except:
        return False

def save_custom_name(ip, name):
    data = {}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
        except: pass
    data[ip] = name
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f)
    except: pass

def get_custom_name(ip):
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                return data.get(ip)
        except: pass
    return None
