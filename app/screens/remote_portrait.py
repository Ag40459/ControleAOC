from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.app import App
from kivy.graphics import Color, Rectangle
from app.utils.themes import theme_manager

class RemotePortraitScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'remote_portrait'
        theme_manager.bind(bg_color=self._update_ui)

    def on_enter(self):
        self.build_ui()

    def _update_ui(self, *args):
        if self.parent: self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        app = App.get_running_app()
        
        with self.canvas.before:
            Color(*theme_manager.bg_color)
            self.rect = Rectangle(pos=self.pos, size=self.size)

        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # BARRA SUPERIOR (Display e Power) - Movido para o topo
        top_bar = BoxLayout(size_hint_y=None, height=dp(70), spacing=dp(10))
        
        # Display de IP (Clicável para renomear)
        display_btn = Button(background_color=theme_manager.display_bg, size_hint_x=0.8)
        display_btn.bind(on_press=lambda x: app.show_rename_popup())
        display_content = BoxLayout(orientation='vertical', padding=dp(5))
        display_content.add_widget(Label(text=app.tv_name, bold=True, color=theme_manager.display_text, font_size='16sp'))
        display_content.add_widget(Label(text=app.tv_ip if app.tv_ip else "BUSCAR TV", color=theme_manager.display_text, font_size='12sp'))
        display_btn.add_widget(display_content)
        top_bar.add_widget(display_btn)
        
        pwr_btn = Button(text='OFF', size_hint_x=0.2, background_color=theme_manager.accent_color, bold=True)
        pwr_btn.bind(on_press=lambda x: app.send_command("Standby"))
        top_bar.add_widget(pwr_btn)
        main_layout.add_widget(top_bar)

        # ÁREA DE NAVEGAÇÃO (Central - Botões Grandes)
        nav_layout = GridLayout(cols=3, spacing=dp(5), size_hint_y=0.4)
        
        # Mapeamento de setas comuns para evitar caracteres quebrados
        arrows = {
            "UP": "UP",
            "DOWN": "DOWN",
            "LEFT": "LEFT",
            "RIGHT": "RIGHT"
        }
        
        # Linha 1
        nav_layout.add_widget(Button(text="VOLTAR", background_color=[0.4, 0.4, 0.4, 1], on_press=lambda x: app.send_command("Back")))
        nav_layout.add_widget(Button(text=arrows["UP"], font_size='20sp', bold=True, on_press=lambda x: app.send_command("CursorUp")))
        nav_layout.add_widget(Button(text="HOME", background_color=theme_manager.primary_color, bold=True, on_press=lambda x: app.send_command("Home")))
        
        # Linha 2
        nav_layout.add_widget(Button(text=arrows["LEFT"], font_size='20sp', bold=True, on_press=lambda x: app.send_command("CursorLeft")))
        nav_layout.add_widget(Button(text="OK", font_size='24sp', bold=True, background_color=theme_manager.primary_color, on_press=lambda x: app.send_command("Confirm")))
        nav_layout.add_widget(Button(text=arrows["RIGHT"], font_size='20sp', bold=True, on_press=lambda x: app.send_command("CursorRight")))
        
        # Linha 3
        nav_layout.add_widget(Button(text="MENU", on_press=lambda x: app.send_command("Menu")))
        nav_layout.add_widget(Button(text=arrows["DOWN"], font_size='20sp', bold=True, on_press=lambda x: app.send_command("CursorDown")))
        nav_layout.add_widget(Button(text="INFO", on_press=lambda x: app.send_command("Info")))
        
        main_layout.add_widget(nav_layout)

        # ÁREA DE CONTROLE INFERIOR (Volume à Direita e Canais à Esquerda)
        control_layout = BoxLayout(spacing=dp(15), size_hint_y=0.4)
        
        # Canais (Esquerda)
        chan_box = BoxLayout(orientation='vertical', spacing=dp(5))
        chan_up = Button(text="CH +", font_size='20sp', bold=True)
        chan_up.bind(on_press=lambda x: app.send_command("ChannelUp"))
        chan_down = Button(text="CH -", font_size='20sp', bold=True)
        chan_down.bind(on_press=lambda x: app.send_command("ChannelDown"))
        chan_box.add_widget(chan_up)
        chan_box.add_widget(chan_down)
        control_layout.add_widget(chan_box)
        
        # Botões de Utilidade (Centro)
        util_box = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_x=0.6)
        
        mute_btn = Button(text="MUTE", background_color=[0.5, 0.5, 0.5, 1])
        mute_btn.bind(on_press=lambda x: app.send_command("Mute"))
        
        key_btn = Button(text="TECLADO", background_color=theme_manager.primary_color)
        key_btn.bind(on_press=lambda x: app.show_numeric_keyboard())
        
        netflix_btn = Button(text="NETFLIX CAT", background_color=[0.9, 0.1, 0.1, 1], bold=True)
        netflix_btn.bind(on_press=lambda x: app.show_netflix_search())
        
        scan_btn = Button(text="BUSCAR TV", font_size='12sp')
        scan_btn.bind(on_press=lambda x: app.go_to_scan())
        
        util_box.add_widget(mute_btn)
        util_box.add_widget(key_btn)
        util_box.add_widget(netflix_btn)
        util_box.add_widget(scan_btn)
        control_layout.add_widget(util_box)
        
        # VOLUME (Direita - Grande destaque)
        vol_box = BoxLayout(orientation='vertical', spacing=dp(5))
        vol_up = Button(text="VOL +", font_size='22sp', bold=True, background_color=theme_manager.primary_color)
        vol_up.bind(on_press=lambda x: app.send_command("VolumeUp"))
        vol_down = Button(text="VOL -", font_size='22sp', bold=True, background_color=theme_manager.primary_color)
        vol_down.bind(on_press=lambda x: app.send_command("VolumeDown"))
        vol_box.add_widget(vol_up)
        vol_box.add_widget(vol_down)
        control_layout.add_widget(vol_box)
        
        main_layout.add_widget(control_layout)
        self.add_widget(main_layout)
