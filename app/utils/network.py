import socket
import requests
import json

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
                return (ip_address, name)
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
