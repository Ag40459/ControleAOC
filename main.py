import threading
import requests
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import StringProperty, ListProperty
from kivy.metrics import dp

from app.screens.scan_screen import ScanScreen
from app.screens.remote_portrait import RemotePortraitScreen
from app.screens.remote_landscape import RemoteLandscapeScreen
from app.utils.network import send_tv_command, save_custom_name, get_custom_name
from app.utils.themes import theme_manager

class RemoteControlApp(App):
    tv_ip = StringProperty("")
    tv_name = StringProperty("TV AOC")
    tv_port = 1925

    def build(self):
        self.title = "Controle AOC Pro"
        self.sm = ScreenManager(transition=FadeTransition())
        self.sm.add_widget(ScanScreen())
        self.sm.add_widget(RemotePortraitScreen())
        self.sm.add_widget(RemoteLandscapeScreen())
        
        # Sincroniza o texto do display quando as propriedades mudam
        self.bind(tv_ip=self._update_screens_text)
        self.bind(tv_name=self._update_screens_text)
        
        Window.bind(on_size=self._on_resize)
        return self.sm

    def _update_screens_text(self, *args):
        for screen_name in ['remote_portrait', 'remote_landscape']:
            screen = self.sm.get_screen(screen_name)
            if hasattr(screen, 'update_display_text'):
                screen.update_display_text()

    def _on_resize(self, window, width, height):
        if self.sm.current == 'scan_screen': return
        self.sm.current = 'remote_landscape' if width > height else 'remote_portrait'

    def go_to_scan(self):
        self.sm.current = 'scan_screen'

    def connect_to_tv(self, ip):
        self.tv_ip = ip
        custom = get_custom_name(ip)
        self.tv_name = custom if custom else "TV AOC"
        threading.Thread(target=self._test_connection, daemon=True).start()

    def _test_connection(self):
        try:
            url = f"http://{self.tv_ip}:{self.tv_port}/1/system"
            res = requests.get(url, timeout=2)
            if res.status_code == 200:
                if not get_custom_name(self.tv_ip):
                    try: self.tv_name = res.json().get('name', "TV AOC")
                    except: pass
                Clock.schedule_once(lambda dt: self._switch_to_remote(), 0)
            else: self._show_error(f"Erro {res.status_code}")
        except: self._show_error("Falha na conexão")

    def _switch_to_remote(self):
        self.sm.current = 'remote_landscape' if Window.width > Window.height else 'remote_portrait'

    def _show_error(self, msg):
        Clock.schedule_once(lambda dt: Popup(title="Erro", content=Label(text=msg), size_hint=(0.8, 0.3)).open(), 0)

    def show_rename_popup(self):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        txt = TextInput(text=self.tv_name, multiline=False, font_size='18sp')
        content.add_widget(txt)
        btn = Button(text="SALVAR", size_hint_y=None, height=dp(50), background_color=theme_manager.primary_color)
        content.add_widget(btn)
        popup = Popup(title="Renomear TV", content=content, size_hint=(0.8, 0.4))
        def save(x):
            self.tv_name = txt.text
            save_custom_name(self.tv_ip, txt.text)
            popup.dismiss()
        btn.bind(on_press=save)
        popup.open()

    def show_numeric_keyboard(self):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        grid = GridLayout(cols=3, spacing=5)
        keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "-/--", "0", "OK"]
        for k in keys:
            cmd = f"Digit{k}" if k.isdigit() else ("DigitDash" if k == "-/--" else "Confirm")
            btn = Button(text=k, font_size='20sp')
            btn.bind(on_press=lambda x, c=cmd: self.send_command(c))
            grid.add_widget(btn)
        content.add_widget(grid)
        close = Button(text="FECHAR", size_hint_y=None, height=dp(50))
        content.add_widget(close)
        popup = Popup(title="Teclado Numérico", content=content, size_hint=(0.9, 0.7))
        close.bind(on_press=popup.dismiss)
        popup.open()

    def show_qwerty_keyboard(self):
        """Cria um teclado alfanumérico QWERTY estilo computador."""
        content = BoxLayout(orientation='vertical', padding=dp(5), spacing=dp(5))
        
        rows = [
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L", "Ç"],
            ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "BACK"]
        ]
        
        for row in rows:
            row_layout = BoxLayout(spacing=dp(2))
            for key in row:
                cmd = f"Digit{key}" if key.isdigit() else key
                # Nota: Algumas TVs AOC podem não suportar letras diretas via DigitX. 
                # Se não funcionar, usaremos o mapeamento padrão de entrada.
                btn = Button(text=key, font_size='14sp')
                btn.bind(on_press=lambda x, k=key: self.send_command(k))
                row_layout.add_widget(btn)
            content.add_widget(row_layout)
        
        # Linha de Espaço e OK
        last_row = BoxLayout(spacing=dp(5), size_hint_y=None, height=dp(50))
        space_btn = Button(text="ESPAÇO", size_hint_x=2)
        space_btn.bind(on_press=lambda x: self.send_command("Space"))
        ok_btn = Button(text="OK", background_color=theme_manager.primary_color)
        ok_btn.bind(on_press=lambda x: self.send_command("Confirm"))
        close_btn = Button(text="FECHAR")
        
        last_row.add_widget(space_btn)
        last_row.add_widget(ok_btn)
        last_row.add_widget(close_btn)
        content.add_widget(last_row)
        
        popup = Popup(title="Teclado Alfanumérico", content=content, size_hint=(0.98, 0.6))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def send_command(self, cmd):
        # Mapeamento para garantir compatibilidade com busca (Netflix/YouTube)
        if cmd == "BACK": cmd = "Back"
        elif cmd == "Space": cmd = "Space"
        
        threading.Thread(target=send_tv_command, args=(self.tv_ip, self.tv_port, cmd), daemon=True).start()

if __name__ == '__main__':
    RemoteControlApp().run()
