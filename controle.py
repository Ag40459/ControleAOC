import socket
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import threading

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.metrics import dp # Importar para usar em size_hint
from kivy.uix.scrollview import ScrollView # Para a lista de TVs encontradas

# --- Funções auxiliares para o scan de rede ---
def get_local_ip_address():
    """
    Tenta obter o endereço IP local da máquina.
    Isso é feito conectando-se a um endereço externo (não envia dados,
    apenas usa a tabela de roteamento para descobrir o IP da interface).
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
       
        # Use um IP público conhecido (como o DNS do Google) para encontrar a interface de saída
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1' # Fallback se não conseguir determinar o IP
    finally:
        s.close()
    return IP

def scan_single_ip(ip_address, tv_port=1925, timeout=1):
    """
    Tenta se conectar a um potencial IP de TV e enviar um comando de teste.
    Retorna o endereço IP se a conexão l(
   for bem-sucedida (status 200), caso contrário, None.
    """
    url = f"http://{ip_address}:{tv_port}/1/input/key"
    headers = {'Content-Type': 'application/json'}
    # Envia um comando inofensivo para testar a conexão, como "VolumeDown"
    data = json.dumps({'key': 'VolumeDown'})

    try:
        response = requests.post(url, data=data, headers=headers, timeout=timeout)
        if response.status_code == 200:
            return ip_address
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        # Ignora timeouts e erros de conexão, pois são esperados para IPs que não são TVs
        pass
    except Exception as e:
        # print(f"  [-] Erro inesperado ao testar {ip_address}: {e}") # Para depuração
        pass
    return None

# --- Telas Kivy ---

class ScanScreen(Screen):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app_instance = app_instance
        self.name = 'scan_screen'
        self.build_ui()

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        title = Label(text='Encontrar TV AOC', size_hint_y=None, height=dp(40),
                     font_size=dp(20), bold=True)
        main_layout.add_widget(title)

        self.scan_status_label = Label(text='Pressione "Escanear Rede" para procurar TVs.',
                                       size_hint_y=None, height=dp(30), color=(1, 1, 1, 1))
        main_layout.add_widget(self.scan_status_label)

        scan_btn = Button(text='Escanear Rede', size_hint_y=None, height=dp(50))
        scan_btn.bind(on_press=self.start_scan)
        main_layout.add_widget(scan_btn)

        main_layout.add_widget(Label(text='Ou insira o IP manualmente:', size_hint_y=None, height=dp(30)))
        manual_ip_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        self.manual_ip_input = TextInput(text='192.168.1.106', multiline=False, size_hint_x=0.7)
        manual_ip_layout.add_widget(self.manual_ip_input)
        connect_manual_btn = Button(text='Conectar', size_hint_x=None, width=dp(80))
        connect_manual_btn.bind(on_press=self.connect_manual_ip)
        manual_ip_layout.add_widget(connect_manual_btn)
        main_layout.add_widget(manual_ip_layout)

        main_layout.add_widget(Label(text='TVs Encontradas:', size_hint_y=None, height=dp(30)))
        
        # Usar ScrollView para a lista de TVs
        scroll_view = ScrollView(size_hint=(1, 1))
        self.found_tvs_layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None)
        self.found_tvs_layout.bind(minimum_height=self.found_tvs_layout.setter('height')) # Ajusta altura do layout interno
        scroll_view.add_widget(self.found_tvs_layout)
        main_layout.add_widget(scroll_view)

        self.add_widget(main_layout)

    def update_scan_status(self, text, color=(1, 1, 1, 1)):
        self.scan_status_label.text = text
        self.scan_status_label.color = color

    def start_scan(self, instance):
        self.update_scan_status("Escaneando rede... Aguarde.", (1, 1, 0, 1)) # Amarelo
        self.found_tvs_layout.clear_widgets() # Limpa resultados anteriores

        threading.Thread(target=self._run_scan_in_background, daemon=True).start()

    def _run_scan_in_background(self):
        start_time = time.time()
        local_ip = get_local_ip_address()
        Clock.schedule_once(lambda dt: self.update_scan_status(f"Seu IP local detectado: {local_ip}"), 0)

        network_prefix = ''
        if local_ip == '127.0.0.1':
            Clock.schedule_once(lambda dt: self.update_scan_status("Não foi possível determinar o IP da rede local automaticamente. Usando prefixo comum (192.168.1.X).", (1, 0.5, 0, 1)), 0)
            network_prefix = '192.168.1.' # Fallback comum
        else:
            parts = local_ip.split('.')
            if len(parts) == 4:
                network_prefix = ".".join(parts[:3]) + "."
            else:
                # LINHA 119 CORRIGIDA AQUI:
                Clock.schedule_once(lambda dt: self.update_scan_status("Formato de IP local inesperado. Usando prefixo comum (192.168.1.X).", (1, 0.5, 0, 1)), 0)
                network_prefix = '192.168.1.' # Fallback comum

        Clock.schedule_once(lambda dt: self.update_scan_status(f"Varrendo IPs de {network_prefix}1 a {network_prefix}254...", (0, 1, 1, 1)), 0)
        found_tvs = []

        with ThreadPoolExecutor(max_workers=70) as executor:
            future_to_ip = {executor.submit(scan_single_ip, f"{network_prefix}{i}"): f"{network_prefix}{i}" for i in range(1, 255)}

            for future in as_completed(future_to_ip):
                ip = future_to_ip[future]
                result = future.result()
                if result:
                    found_tvs.append(result)
                    # Atualiza a UI no thread principal
                    Clock.schedule_once(lambda dt, tv_ip=result: self.add_found_tv_button(tv_ip), 0)

        end_time = time.time()
        duration = end_time - start_time

        if found_tvs:
            Clock.schedule_once(lambda dt: self.update_scan_status(f"Scan Concluído! {len(found_tvs)} TV(s) encontrada(s) em {duration:.2f} segundos.", (0, 1, 0, 1)), 0)
        else:
            Clock.schedule_once(lambda dt: self.update_scan_status(f"Scan Concluído! Nenhuma TV AOC compatível encontrada em {duration:.2f} segundos.", (1, 0, 0, 1)), 0)

    def add_found_tv_button(self, tv_ip):
        btn = Button(text=f"TV em: {tv_ip}", size_hint_y=None, height=dp(40))
        btn.bind(on_press=lambda instance: self.select_tv_and_go_to_remote(tv_ip))
        self.found_tvs_layout.add_widget(btn)

    def connect_manual_ip(self, instance):
        ip = self.manual_ip_input.text.strip()
        if ip:
            self.select_tv_and_go_to_remote(ip)
        else:
            self.update_scan_status("Por favor, insira um IP válido.", (1, 0, 0, 1))

    def select_tv_and_go_to_remote(self, tv_ip):
        self.app_instance.tv_ip = tv_ip
        # Atualiza o label de IP na tela do controle remoto
        if self.app_instance.sm.has_screen('remote_control_screen'):
            remote_screen = self.app_instance.sm.get_screen('remote_control_screen')
            if remote_screen.app_instance.ip_display_label: # Verifica se o label existe
                remote_screen.app_instance.ip_display_label.text = tv_ip
        self.app_instance.sm.current = 'remote_control_screen'
        # Opcional: Tentar testar a conexão imediatamente ao mudar de tela
        Clock.schedule_once(lambda dt: self.app_instance.test_connection_on_load(), 0)


class RemoteControlScreen(Screen):
    """
    Tela principal do controle remoto.
    """
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app_instance = app_instance # Referência à instância principal do App
        self.name = 'remote_control_screen'
        self.build_ui()

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # Botão para voltar à tela de scan
        back_btn = Button(text='< Voltar ao Scan', size_hint_y=None, height=dp(40), size_hint_x=None, width=dp(150))
        back_btn.bind(on_press=self.go_back_to_scan)
        main_layout.add_widget(back_btn)

        # Título
        title = Label(text='Controle Remoto TV AOC', size_hint_y=None, height=dp(40),
                     font_size=dp(20), bold=True)
        main_layout.add_widget(title)

        # Status da conexão (referência para o app_instance)
        self.app_instance.status_label = Label(text='Status: Desconectado', size_hint_y=None, height=dp(30),
                                 color=(1, 0.5, 0, 1))
        main_layout.add_widget(self.app_instance.status_label)

        # Configuração IP (agora apenas exibe, o IP é definido pelo scan/entrada manual)
        config_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        config_layout.add_widget(Label(text='IP da TV:', size_hint_x=None, width=dp(80)))
        self.app_instance.ip_display_label = Label(text=self.app_instance.tv_ip, size_hint_x=0.7)
        config_layout.add_widget(self.app_instance.ip_display_label)
        test_btn = Button(text='Testar', size_hint_x=None, width=dp(80))
        test_btn.bind(on_press=self.app_instance.test_connection)
        config_layout.add_widget(test_btn)
        main_layout.add_widget(config_layout)

        # Botões principais
        top_buttons = GridLayout(cols=3, size_hint_y=None, height=dp(120), spacing=dp(5)) # Aumentei a altura para caber 6 botões
        for label in ["Power", "Fonte", "Menu", "Home", "Info", "Voltar"]:
            btn = Button(text=label)
            btn.bind(on_press=self.app_instance.send_key)
            top_buttons.add_widget(btn)
        main_layout.add_widget(top_buttons)

        # Controles direcionais
        dir_layout = GridLayout(cols=3, size_hint_y=None, height=dp(120), spacing=dp(5))
        dir_layout.add_widget(Label())
        up_btn = Button(text="⬆")
        up_btn.bind(on_press=self.app_instance.send_key)
        dir_layout.add_widget(up_btn)
        dir_layout.add_widget(Label())

        left_btn = Button(text="⬅")
        left_btn.bind(on_press=self.app_instance.send_key)
        dir_layout.add_widget(left_btn)
        ok_btn = Button(text="OK", background_color=(0.2, 0.8, 0.2, 1))
        ok_btn.bind(on_press=self.app_instance.send_key)
        dir_layout.add_widget(ok_btn)
        right_btn = Button(text="➡")
        right_btn.bind(on_press=self.app_instance.send_key)
        dir_layout.add_widget(right_btn)

        dir_layout.add_widget(Label())
        down_btn = Button(text="⬇")
        down_btn.bind(on_press=self.app_instance.send_key)
        dir_layout.add_widget(down_btn)
        dir_layout.add_widget(Label())
        main_layout.add_widget(dir_layout)

        # Volume e Canal
        vol_layout = GridLayout(cols=2, size_hint_y=None, height=dp(60), spacing=dp(5))
        for label in ["Volume +", "Volume -", "Canal +", "Canal -"]:
            btn = Button(text=label)
            btn.bind(on_press=self.app_instance.send_key)
            vol_layout.add_widget(btn)
        main_layout.add_widget(vol_layout)

        # Mute
        mute_btn = Button(text="Mute", size_hint_y=None, height=dp(50),
                         background_color=(0.8, 0.2, 0.2, 1))
        mute_btn.bind(on_press=self.app_instance.send_key)
        main_layout.add_widget(mute_btn)

        # Teclado numérico
        num_btn = Button(text="Teclado Numérico", size_hint_y=None, height=dp(50))
        num_btn.bind(on_press=self.app_instance.show_numeric_keyboard)
        main_layout.add_widget(num_btn)

        self.add_widget(main_layout)

    def go_back_to_scan(self, instance):
        self.app_instance.sm.current = 'scan_screen'


class RemoteControlApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tv_ip = "192.168.1.106" # IP inicial, será atualizado pelo scan ou entrada manual
        self.tv_port = 1925
        self.status_label = None # Será atribuído na RemoteControlScreen
        self.ip_display_label = None # Será atribuído na RemoteControlScreen

        self.keys = {
            "Power": "Standby",
            "Fonte": "Source",
            "Menu": "Menu",
            "Home": "Home",
            "Info": "Info",
            "Voltar": "Back",
            "⬆": "CursorUp",
            "⬇": "CursorDown",
            "⬅": "CursorLeft",
            "➡": "CursorRight",
            "OK": "Confirm",
            "Volume +": "VolumeUp",
            "Volume -": "VolumeDown",
            "Canal +": "ChannelUp",
            "Canal -": "ChannelDown",
            "Mute": "Mute"
        }

        self.numeric_keys = {
            "1": "Digit1", "2": "Digit2", "3": "Digit3",
            "4": "Digit4", "5": "Digit5", "6": "Digit6",
            "7": "Digit7", "8": "Digit8", "9": "Digit9",
            "0": "Digit0", "-/--": "DigitDash"
        }

    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(ScanScreen(app_instance=self))
        self.sm.add_widget(RemoteControlScreen(app_instance=self))
        return self.sm

    def update_status(self, text, color):
        if self.status_label:
            self.status_label.text = f"Status: {text}"
            self.status_label.color = color

    def test_connection(self, instance=None): # instance pode ser None se chamado na inicialização
        self.update_status("Testando...", (1, 1, 0, 1)) # Amarelo

        def test_in_thread():
            try:
                url = f"http://{self.tv_ip}:{self.tv_port}/1/input/key"
                headers = {'Content-Type': 'application/json'}
                data = json.dumps({'key': 'VolumeDown'})

                response = requests.post(url, data=data, headers=headers, timeout=3)

                if response.status_code == 200:
                    Clock.schedule_once(lambda dt: self.update_status("Conectado", (0, 1, 0, 1)), 0)
                else:
                    Clock.schedule_once(lambda dt: self.update_status(f"Erro de comunicação ({response.status_code})", (1, 0, 0, 1)), 0)

            except requests.exceptions.Timeout:
                Clock.schedule_once(lambda dt: self.update_status("Timeout - TV não responde", (1, 0, 0, 1)), 0)
            except requests.exceptions.ConnectionError:
                Clock.schedule_once(lambda dt: self.update_status("Erro de conexão", (1, 0, 0, 1)), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self.update_status(f"Erro: {str(e)[:50]}...", (1, 0, 0, 1)), 0)

        threading.Thread(target=test_in_thread, daemon=True).start()

    def test_connection_on_load(self):
        # Chamado quando a tela do controle remoto é carregada após a seleção do IP
        self.test_connection()

    def send_key(self, instance):
        key_name = instance.text
        if key_name in self.keys:
            key = self.keys[key_name]
        else:
            key = key_name # Para casos como "OK", "⬆", etc.

        def send_in_thread():
            try:
                url = f"http://{self.tv_ip}:{self.tv_port}/1/input/key"
                headers = {'Content-Type': 'application/json'}
                data = json.dumps({'key': key})

                response = requests.post(url, data=data, headers=headers, timeout=2)

                if response.status_code == 200:
                    Clock.schedule_once(lambda dt: self.update_status(f"Enviado: {key_name}", (0, 1, 0, 1)), 0)
                else:
                    Clock.schedule_once(lambda dt: self.update_status(f"Erro ao enviar {key_name} ({response.status_code})", (1, 0, 0, 1)), 0)

            except Exception as e:
                Clock.schedule_once(lambda dt: self.update_status(f"Falha ao enviar {key_name}: {str(e)[:50]}...", (1, 0, 0, 1)), 0)

        threading.Thread(target=send_in_thread, daemon=True).start()

    def send_numeric_key(self, instance):
        key = self.numeric_keys.get(instance.text, instance.text) # Usa o valor do dicionário ou o próprio texto

        def send_in_thread():
            try:
                url = f"http://{self.tv_ip}:{self.tv_port}/1/input/key"
                headers = {'Content-Type': 'application/json'}
                data = json.dumps({'key': key})

                response = requests.post(url, data=data, headers=headers, timeout=2)

                if response.status_code == 200:
                    Clock.schedule_once(lambda dt: self.update_status(f"Enviado: {instance.text}", (0, 1, 0, 1)), 0)
                else:
                    Clock.schedule_once(lambda dt: self.update_status(f"Erro ao enviar {instance.text} ({response.status_code})", (1, 0, 0, 1)), 0)

            except Exception as e:
                Clock.schedule_once(lambda dt: self.update_status(f"Falha ao enviar {instance.text}: {str(e)[:50]}...", (1, 0, 0, 1)), 0)

        threading.Thread(target=send_in_thread, daemon=True).start()

    def show_numeric_keyboard(self, instance):
        content = BoxLayout(orientation='vertical', spacing=dp(10))

        num_layout = GridLayout(cols=3, spacing=dp(5))
        # Adiciona os botões numéricos e o "-/--"
        for num in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "-/--", "0"]:
            btn = Button(text=num, size_hint=(None, None), size=(dp(80), dp(80)))
            btn.bind(on_press=self.send_numeric_key)
            num_layout.add_widget(btn)

        content.add_widget(num_layout)

        close_btn = Button(text="Fechar", size_hint_y=None, height=dp(40))
        content.add_widget(close_btn)

        popup = Popup(title="Teclado Numérico", content=content,
                      size_hint=(None, None), size=(dp(300), dp(400)))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

if __name__ == '__main__':
    RemoteControlApp().run()
