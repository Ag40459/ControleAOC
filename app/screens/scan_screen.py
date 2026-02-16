from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar
from kivy.metrics import dp
from kivy.app import App
from kivy.graphics import Color, Rectangle
from app.utils.themes import theme_manager
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.utils.network import get_local_ip_address, scan_single_ip
from kivy.clock import Clock

class ScanScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'scan_screen'
        self._bg_rect = None

    def on_enter(self):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        with self.canvas.before:
            self.canvas.before.clear()
            Color(*theme_manager.bg_color)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        layout.add_widget(Label(text='CONTROLE AOC PRO', font_size='24sp', bold=True, color=theme_manager.primary_color, size_hint_y=None, height=dp(50)))
        
        theme_box = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))
        for t in theme_manager.themes.keys():
            btn = Button(text=t, font_size='12sp', background_color=theme_manager.primary_color if theme_manager.theme_name == t else [0.3, 0.3, 0.3, 1])
            btn.bind(on_press=lambda x, n=t: self._change_theme(n))
            theme_box.add_widget(btn)
        layout.add_widget(theme_box)

        self.status_label = Label(text='Pronto para buscar', color=theme_manager.text_color, size_hint_y=None, height=dp(30))
        layout.add_widget(self.status_label)
        self.pb = ProgressBar(max=254, size_hint_y=None, height=dp(10))
        layout.add_widget(self.pb)
        
        self.scan_btn = Button(text='BUSCAR TV', size_hint_y=None, height=dp(50), background_color=theme_manager.primary_color, bold=True)
        self.scan_btn.bind(on_press=self.start_scan)
        layout.add_widget(self.scan_btn)
        
        self.tv_list = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        self.tv_list.bind(minimum_height=self.tv_list.setter('height'))
        scroll = ScrollView()
        scroll.add_widget(self.tv_list)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def _change_theme(self, name):
        theme_manager.set_theme(name)
        self.build_ui()

    def _update_rect(self, instance, value):
        if self._bg_rect:
            self._bg_rect.pos = instance.pos
            self._bg_rect.size = instance.size

    def start_scan(self, instance):
        self.scan_btn.disabled = True
        self.tv_list.clear_widgets()
        threading.Thread(target=self._scan_thread, daemon=True).start()

    def _scan_thread(self):
        local_ip = get_local_ip_address()
        prefix = ".".join(local_ip.split('.')[:3]) + "."
        with ThreadPoolExecutor(max_workers=50) as ex:
            futures = {ex.submit(scan_single_ip, f"{prefix}{i}"): i for i in range(1, 255)}
            for i, f in enumerate(as_completed(futures)):
                res = f.result()
                if res: Clock.schedule_once(lambda dt, r=res: self.add_tv(r[0], r[1]), 0)
                Clock.schedule_once(lambda dt, v=i: setattr(self.pb, 'value', v), 0)
        Clock.schedule_once(lambda dt: setattr(self.scan_btn, 'disabled', False), 0)

    def add_tv(self, ip, name):
        btn = Button(text=f"{name} ({ip})", size_hint_y=None, height=dp(60))
        btn.bind(on_press=lambda x: App.get_running_app().connect_to_tv(ip))
        self.tv_list.add_widget(btn)
