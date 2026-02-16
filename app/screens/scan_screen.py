import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.app import App
from kivy.graphics import Color, Rectangle
from app.utils.network import get_local_ip_address, scan_single_ip
from app.utils.themes import theme_manager

class ScanScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'scan_screen'
        theme_manager.bind(bg_color=self._update_bg)
        self.build_ui()

    def _update_bg(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*theme_manager.bg_color)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Cabeçalho e Temas
        header = BoxLayout(size_hint_y=None, height=dp(50))
        header.add_widget(Label(text='CONTROLE AOC', font_size='24sp', bold=True, color=theme_manager.primary_color))
        layout.add_widget(header)
        
        theme_box = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))
        theme_box.add_widget(Label(text="Tema:", color=theme_manager.text_color, size_hint_x=0.3))
        for t_name in theme_manager.themes.keys():
            btn = Button(text=t_name, font_size='12sp', background_color=theme_manager.primary_color if theme_manager.theme_name == t_name else [0.3, 0.3, 0.3, 1])
            btn.bind(on_press=lambda x, n=t_name: theme_manager.set_theme(n))
            theme_box.add_widget(btn)
        layout.add_widget(theme_box)

        self.status_label = Label(text='Pronto para buscar sua TV', size_hint_y=None, height=dp(30), color=theme_manager.text_color)
        layout.add_widget(self.status_label)
        
        self.progress_bar = ProgressBar(max=254, value=0, size_hint_y=None, height=dp(10))
        layout.add_widget(self.progress_bar)
        
        self.scan_btn = Button(text='BUSCAR TV NA REDE', size_hint_y=None, height=dp(50), background_color=theme_manager.primary_color, bold=True)
        self.scan_btn.bind(on_press=self.start_scan)
        layout.add_widget(self.scan_btn)
        
        manual_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45), spacing=dp(10))
        self.ip_input = TextInput(text='192.168.1.', multiline=False, font_size='16sp')
        manual_box.add_widget(self.ip_input)
        connect_btn = Button(text='CONECTAR', size_hint_x=0.4, background_color=[0.2, 0.8, 0.2, 1])
        connect_btn.bind(on_press=self.manual_connect)
        manual_box.add_widget(connect_btn)
        layout.add_widget(manual_box)
        
        layout.add_widget(Label(text='TVs Encontradas:', size_hint_y=None, height=dp(25), color=theme_manager.text_color))
        
        scroll = ScrollView()
        self.tv_list = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
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
            self.status_label.text = "Nenhuma TV encontrada."
        else:
            self.status_label.text = "Busca finalizada!"

    def add_tv_entry(self, ip, name):
        btn = Button(text=f"{name} ({ip})", size_hint_y=None, height=dp(60), background_color=[0.2, 0.2, 0.2, 1])
        btn.bind(on_press=lambda x: App.get_running_app().connect_to_tv(ip))
        self.tv_list.add_widget(btn)

    def manual_connect(self, instance):
        ip = self.ip_input.text.strip()
        if ip: App.get_running_app().connect_to_tv(ip)
