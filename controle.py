import socket
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import threading
import math

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar
from kivy.uix.anchorlayout import AnchorLayout
from kivy.graphics import Color, Ellipse, Line, PushMatrix, PopMatrix, Rotate
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ListProperty, ObjectProperty, StringProperty

# --- Funções auxiliares de rede ---
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

# --- Widgets Customizados ---

class RotaryKnob(Widget):
    """Um botão de volume giratório interativo para o modo paisagem."""
    angle = NumericProperty(0)
    value = NumericProperty(50)
    on_volume_change = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            PushMatrix()
            self.rot = Rotate(origin=self.center, angle=0)
        with self.canvas:
            # Sombra/Fundo do botão
            Color(0.1, 0.1, 0.1, 1)
            self.bg_ellipse = Ellipse(pos=self.pos, size=self.size)
            # Corpo do botão
            Color(0.3, 0.3, 0.3, 1)
            self.knob_ellipse = Ellipse(pos=(self.x + 5, self.y + 5), size=(self.width - 10, self.height - 10))
            # Indicador de posição
            Color(0.8, 0.2, 0.2, 1)
            self.indicator = Line(points=[], width=2)
        with self.canvas.after:
            PopMatrix()
        
        self.bind(pos=self._update_canvas, size=self._update_canvas, angle=self._update_rotation)

    def _update_canvas(self, *args):
        self.bg_ellipse.pos = self.pos
        self.bg_ellipse.size = self.size
        self.knob_ellipse.pos = (self.x + dp(10), self.y + dp(10))
        self.knob_ellipse.size = (self.width - dp(20), self.height - dp(20))
        self.rot.origin = self.center
        self._update_indicator()

    def _update_rotation(self, *args):
        self.rot.angle = self.angle
        self._update_indicator()

    def _update_indicator(self, *args):
        # Desenha uma linha indicadora do centro para a borda baseada no ângulo
        rad = math.radians(self.angle + 90)
        r = (self.width / 2) - dp(15)
        cx, cy = self.center
        px = cx + r * math.cos(rad)
        py = cy + r * math.sin(rad)
        self.indicator.points = [cx, cy, px, py]

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            self._update_angle(touch)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self._update_angle(touch)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            return True
        return super().on_touch_up(touch)

    def _update_angle(self, touch):
        dx = touch.x - self.center_x
        dy = touch.y - self.center_y
        new_angle = math.degrees(math.atan2(dy, dx)) - 90
        
        # Lógica para detectar sentido de rotação e limitar
        diff = new_angle - self.angle
        if diff > 180: diff -= 360
        if diff < -180: diff += 360
        
        self.angle = new_angle
        
        if self.on_volume_change:
            if diff > 0:
                self.on_volume_change("VolumeUp")
            elif diff < 0:
                self.on_volume_change("VolumeDown")

# --- Telas ---

class ScanScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'scan_screen'
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        layout.add_widget(Label(text='CONTROLE AOC', font_size='32sp', bold=True, color=(0.2, 0.6, 1, 1), size_hint_y=None, height=dp(60)))
        
        self.status_label = Label(text='Pronto para buscar sua TV', size_hint_y=None, height=dp(40))
        layout.add_widget(self.status_label)
        
        self.progress_bar = ProgressBar(max=254, value=0, size_hint_y=None, height=dp(15))
        layout.add_widget(self.progress_bar)
        
        self.scan_btn = Button(text='BUSCAR TV NA REDE', size_hint_y=None, height=dp(60), background_color=(0.1, 0.4, 0.8, 1), bold=True)
        self.scan_btn.bind(on_press=self.start_scan)
        layout.add_widget(self.scan_btn)
        
        manual_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        self.ip_input = TextInput(text='192.168.1.', multiline=False, font_size='18sp', padding=[dp(10), dp(10)])
        manual_box.add_widget(self.ip_input)
        connect_btn = Button(text='CONECTAR', size_hint_x=0.4, background_color=(0.2, 0.8, 0.2, 1))
        connect_btn.bind(on_press=self.manual_connect)
        manual_box.add_widget(connect_btn)
        layout.add_widget(manual_box)
        
        layout.add_widget(Label(text='TVs Encontradas:', size_hint_y=None, height=dp(30), halign='left'))
        
        scroll = ScrollView()
        self.tv_list = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        self.tv_list.bind(minimum_height=self.tv_list.setter('height'))
        scroll.add_widget(self.tv_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)

    def start_scan(self, instance):
        self.scan_btn.disabled = True
        self.status_label.text = "Buscando TVs na rede local..."
        self.tv_list.clear_widgets()
        self.progress_bar.value = 0
        threading.Thread(target=self._scan_thread, daemon=True).start()

    def _scan_thread(self):
        local_ip = get_local_ip_address()
        prefix = ".".join(local_ip.split('.')[:3]) + "."
        
        with ThreadPoolExecutor(max_workers=60) as executor:
            futures = {executor.submit(scan_single_ip, f"{prefix}{i}"): i for i in range(1, 255)}
            for i, future in enumerate(as_completed(futures)):
                result = future.result()
                if result:
                    Clock.schedule_once(lambda dt, r=result: self.add_tv_entry(r[0], r[1]), 0)
                Clock.schedule_once(lambda dt, v=i+1: self._update_progress(v), 0)
        
        Clock.schedule_once(self._scan_finished, 0)

    def _update_progress(self, val):
        self.progress_bar.value = val

    def _scan_finished(self, dt):
        self.scan_btn.disabled = False
        if not self.tv_list.children:
            self.status_label.text = "Nenhuma TV encontrada. Tente o IP manual."
        else:
            self.status_label.text = "Busca finalizada!"

    def add_tv_entry(self, ip, name):
        btn = Button(text=f"{name}\n({ip})", size_hint_y=None, height=dp(70), background_color=(0.3, 0.3, 0.3, 1), halign='center')
        btn.bind(on_press=lambda x: App.get_running_app().connect_to_tv(ip))
        self.tv_list.add_widget(btn)

    def manual_connect(self, instance):
        ip = self.ip_input.text.strip()
        if ip:
            App.get_running_app().connect_to_tv(ip)

class RemotePortraitScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'remote_portrait'
        self.buttons = {}

    def on_enter(self):
        self.build_ui()
        App.get_running_app().verify_supported_keys(self)

    def build_ui(self):
        self.clear_widgets()
        app = App.get_running_app()
        
        # Design inspirado em controle real
        main_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(8))
        
        # Barra de Status
        status_bar = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        back_btn = Button(text='< BUSCAR', size_hint_x=0.3, background_color=(0.7, 0.2, 0.2, 1))
        back_btn.bind(on_press=lambda x: app.go_to_scan())
        status_bar.add_widget(back_btn)
        self.status_lbl = Label(text=f"TV: {app.tv_ip}", bold=True, color=(0, 1, 0, 1))
        status_bar.add_widget(self.status_lbl)
        main_layout.add_widget(status_bar)

        # Botões de Topo (Power, Source)
        top_row = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(20))
        pwr = self._create_btn("Power", "Standby", (0.8, 0.1, 0.1, 1))
        src = self._create_btn("Fonte", "Source", (0.2, 0.2, 0.2, 1))
        top_row.add_widget(pwr)
        top_row.add_widget(src)
        main_layout.add_widget(top_row)

        # Teclado Numérico (Compacto)
        num_grid = GridLayout(cols=3, spacing=dp(5), size_hint_y=None, height=dp(180))
        for i in range(1, 10):
            num_grid.add_widget(self._create_btn(str(i), f"Digit{i}"))
        num_grid.add_widget(self._create_btn("-/--", "DigitDash"))
        num_grid.add_widget(self._create_btn("0", "Digit0"))
        num_grid.add_widget(self._create_btn("Teclado", "Keyboard", (0.2, 0.5, 0.8, 1)))
        main_layout.add_widget(num_grid)

        # Navegação (Pad Direcional)
        nav_box = AnchorLayout(size_hint_y=None, height=dp(180))
        nav_grid = GridLayout(cols=3, spacing=dp(2), size=(dp(180), dp(180)), size_hint=(None, None))
        nav_grid.add_widget(Widget())
        nav_grid.add_widget(self._create_btn("▲", "CursorUp"))
        nav_grid.add_widget(Widget())
        nav_grid.add_widget(self._create_btn("◀", "CursorLeft"))
        nav_grid.add_widget(self._create_btn("OK", "Confirm", (0.1, 0.5, 0.1, 1)))
        nav_grid.add_widget(self._create_btn("▶", "CursorRight"))
        nav_grid.add_widget(Widget())
        nav_grid.add_widget(self._create_btn("▼", "CursorDown"))
        nav_grid.add_widget(Widget())
        nav_box.add_widget(nav_grid)
        main_layout.add_widget(nav_box)

        # Menu, Home, Back, Info
        menu_row = GridLayout(cols=4, spacing=dp(5), size_hint_y=None, height=dp(50))
        menu_row.add_widget(self._create_btn("Menu", "Menu"))
        menu_row.add_widget(self._create_btn("Home", "Home"))
        menu_row.add_widget(self._create_btn("Voltar", "Back"))
        menu_row.add_widget(self._create_btn("Info", "Info"))
        main_layout.add_widget(menu_row)

        # Volume e Canal
        vol_chan_row = BoxLayout(spacing=dp(20), size_hint_y=None, height=dp(120))
        
        vol_box = BoxLayout(orientation='vertical', spacing=dp(5))
        vol_box.add_widget(self._create_btn("VOL +", "VolumeUp"))
        vol_box.add_widget(self._create_btn("MUTE", "Mute", (0.5, 0.5, 0.5, 1)))
        vol_box.add_widget(self._create_btn("VOL -", "VolumeDown"))
        
        chan_box = BoxLayout(orientation='vertical', spacing=dp(5))
        chan_box.add_widget(self._create_btn("CH +", "ChannelUp"))
        chan_box.add_widget(Label(text="CANAL", font_size='12sp'))
        chan_box.add_widget(self._create_btn("CH -", "ChannelDown"))
        
        vol_chan_row.add_widget(vol_box)
        vol_chan_row.add_widget(chan_box)
        main_layout.add_widget(vol_chan_row)

        self.add_widget(main_layout)

    def _create_btn(self, text, cmd, color=None):
        btn = Button(text=text, background_color=color if color else (0.2, 0.2, 0.2, 1), bold=True)
        btn.bind(on_press=lambda x: App.get_running_app().send_command(cmd))
        self.buttons[cmd] = btn
        return btn

class RemoteLandscapeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'remote_landscape'

    def on_enter(self):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        app = App.get_running_app()
        
        layout = GridLayout(cols=3, padding=dp(20), spacing=dp(30))
        
        # Coluna Esquerda: Canais e Mute
        left_col = BoxLayout(orientation='vertical', spacing=dp(15))
        left_col.add_widget(Button(text="CANAL +", font_size='24sp', on_press=lambda x: app.send_command("ChannelUp")))
        left_col.add_widget(Button(text="MUTE", font_size='20sp', background_color=(0.5, 0.5, 0.5, 1), on_press=lambda x: app.send_command("Mute")))
        left_col.add_widget(Button(text="CANAL -", font_size='24sp', on_press=lambda x: app.send_command("ChannelDown")))
        layout.add_widget(left_col)
        
        # Coluna Central: Botão de Volume Giratório
        mid_col = BoxLayout(orientation='vertical', spacing=dp(10))
        mid_col.add_widget(Label(text="VOLUME", font_size='24sp', bold=True))
        self.knob = RotaryKnob(size_hint=(None, None), size=(dp(200), dp(200)), pos_hint={'center_x': 0.5})
        self.knob.on_volume_change = app.send_command
        anchor = AnchorLayout()
        anchor.add_widget(self.knob)
        mid_col.add_widget(anchor)
        layout.add_widget(mid_col)
        
        # Coluna Direita: Navegação e Voltar
        right_col = BoxLayout(orientation='vertical', spacing=dp(15))
        right_col.add_widget(Button(text="HOME", font_size='20sp', on_press=lambda x: app.send_command("Home")))
        right_col.add_widget(Button(text="VOLTAR AO SCAN", font_size='18sp', background_color=(0.7, 0.2, 0.2, 1), on_press=lambda x: app.go_to_scan()))
        right_col.add_widget(Button(text="POWER", font_size='20sp', background_color=(0.8, 0.1, 0.1, 1), on_press=lambda x: app.send_command("Standby")))
        layout.add_widget(right_col)
        
        self.add_widget(layout)

# --- App Principal ---

class RemoteControlApp(App):
    tv_ip = StringProperty("")
    tv_port = 1925
    supported_keys = ListProperty([])

    def build(self):
        self.title = "Controle AOC Pro"
        self.sm = ScreenManager(transition=FadeTransition())
        self.sm.add_widget(ScanScreen())
        self.sm.add_widget(RemotePortraitScreen())
        self.sm.add_widget(RemoteLandscapeScreen())
        
        Window.bind(on_size=self._on_resize)
        return self.sm

    def _on_resize(self, window, width, height):
        if self.sm.current == 'scan_screen':
            return
        
        if width > height:
            if self.sm.current != 'remote_landscape':
                self.sm.current = 'remote_landscape'
        else:
            if self.sm.current != 'remote_portrait':
                self.sm.current = 'remote_portrait'

    def go_to_scan(self):
        self.sm.current = 'scan_screen'

    def connect_to_tv(self, ip):
        self.tv_ip = ip
        # Testa conexão antes de mudar
        threading.Thread(target=self._test_connection, daemon=True).start()

    def _test_connection(self):
        try:
            url = f"http://{self.tv_ip}:{self.tv_port}/1/system"
            res = requests.get(url, timeout=2)
            if res.status_code == 200:
                Clock.schedule_once(lambda dt: self._switch_to_remote(), 0)
            else:
                self._show_error(f"TV recusou conexão (Erro {res.status_code})")
        except:
            self._show_error("Não foi possível conectar à TV.")

    def _switch_to_remote(self):
        if Window.width > Window.height:
            self.sm.current = 'remote_landscape'
        else:
            self.sm.current = 'remote_portrait'

    def _show_error(self, msg):
        Clock.schedule_once(lambda dt: Popup(title="Erro", content=Label(text=msg), size_hint=(0.8, 0.3)).open(), 0)

    def verify_supported_keys(self, screen):
        threading.Thread(target=self._fetch_keys, args=(screen,), daemon=True).start()

    def _fetch_keys(self, screen):
        # Tenta descobrir comandos comentados ou suportados pela API
        # Algumas TVs AOC/Philips usam endpoints diferentes para listar recursos
        try:
            # Endpoint comum para estrutura de menus/comandos
            url = f"http://{self.tv_ip}:{self.tv_port}/1/menuitems/settings/structure"
            res = requests.get(url, timeout=2)
            if res.status_code == 200:
                data = res.text
                # Se encontrar referências a chaves no JSON, marca como suportado
                # Esta é uma verificação heurística simples
                found = []
                for cmd in screen.buttons.keys():
                    if cmd in data:
                        found.append(cmd)
                self.supported_keys = found
                Clock.schedule_once(lambda dt: self._update_ui_keys(screen), 0)
        except:
            pass

    def _update_ui_keys(self, screen):
        if not self.supported_keys: return
        for cmd, btn in screen.buttons.items():
            if cmd not in self.supported_keys and cmd not in ["Standby", "Source", "Confirm", "Back", "Home"]:
                # Desabilita botões que parecem não ser suportados (com cautela)
                # btn.disabled = True 
                # btn.opacity = 0.5
                # Comentado para não quebrar botões que funcionam mas não aparecem na estrutura
                pass

    def send_command(self, cmd):
        if cmd == "Keyboard":
            # Abre o teclado do sistema (simulação)
            return
            
        def _send():
            try:
                url = f"http://{self.tv_ip}:{self.tv_port}/1/input/key"
                requests.post(url, json={'key': cmd}, timeout=1)
            except:
                pass
        threading.Thread(target=_send, daemon=True).start()

if __name__ == '__main__':
    RemoteControlApp().run()
