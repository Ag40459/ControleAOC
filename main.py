import threading
import requests
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import StringProperty, ListProperty

from app.screens.scan_screen import ScanScreen
from app.screens.remote_portrait import RemotePortraitScreen
from app.screens.remote_landscape import RemoteLandscapeScreen
from app.utils.network import send_tv_command

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
        if self.sm.current == 'scan_screen': return
        if width > height:
            if self.sm.current != 'remote_landscape': self.sm.current = 'remote_landscape'
        else:
            if self.sm.current != 'remote_portrait': self.sm.current = 'remote_portrait'

    def go_to_scan(self):
        self.sm.current = 'scan_screen'

    def connect_to_tv(self, ip):
        self.tv_ip = ip
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
        self.sm.current = 'remote_landscape' if Window.width > Window.height else 'remote_portrait'

    def _show_error(self, msg):
        Clock.schedule_once(lambda dt: Popup(title="Erro", content=Label(text=msg), size_hint=(0.8, 0.3)).open(), 0)

    def verify_supported_keys(self, screen):
        threading.Thread(target=self._fetch_keys, args=(screen,), daemon=True).start()

    def _fetch_keys(self, screen):
        try:
            url = f"http://{self.tv_ip}:{self.tv_port}/1/menuitems/settings/structure"
            res = requests.get(url, timeout=2)
            if res.status_code == 200:
                data = res.text
                found = [cmd for cmd in screen.buttons.keys() if cmd in data]
                self.supported_keys = found
        except: pass

    def send_command(self, cmd):
        if cmd == "Keyboard": return
        threading.Thread(target=send_tv_command, args=(self.tv_ip, self.tv_port, cmd), daemon=True).start()

if __name__ == '__main__':
    RemoteControlApp().run()
