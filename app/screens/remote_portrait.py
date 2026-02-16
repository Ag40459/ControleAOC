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
        # Vincula a atualização à mudança de qualquer propriedade do tema
        theme_manager.bind(bg_color=self._update_canvas)
        theme_manager.bind(primary_color=self._update_canvas)

    def on_enter(self):
        self._update_canvas()

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*theme_manager.bg_color)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        app = App.get_running_app()
        
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # BARRA SUPERIOR (Display e Power)
        top_bar = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        
        display_btn = Button(background_color=theme_manager.display_bg, size_hint_x=0.8)
        display_btn.bind(on_press=lambda x: app.show_rename_popup())
        display_content = BoxLayout(orientation='vertical', padding=dp(5))
        display_content.add_widget(Label(text=app.tv_name, bold=True, color=theme_manager.display_text, font_size='16sp'))
        display_content.add_widget(Label(text=app.tv_ip, color=theme_manager.display_text, font_size='12sp'))
        display_btn.add_widget(display_content)
        top_bar.add_widget(display_btn)
        
        pwr_btn = Button(text='OFF', size_hint_x=0.2, background_color=theme_manager.accent_color, bold=True)
        pwr_btn.bind(on_press=lambda x: app.send_command("Standby"))
        top_bar.add_widget(pwr_btn)
        main_layout.add_widget(top_bar)

        # ÁREA DE NAVEGAÇÃO
        nav_layout = GridLayout(cols=3, spacing=dp(5), size_hint_y=0.4)
        
        # Linha 1
        nav_layout.add_widget(Button(text="VOLTAR", background_color=[0.4, 0.4, 0.4, 1], on_press=lambda x: app.send_command("Back")))
        nav_layout.add_widget(Button(text="▲", font_size='30sp', bold=True, on_press=lambda x: app.send_command("CursorUp")))
        nav_layout.add_widget(Button(text="HOME", background_color=theme_manager.primary_color, bold=True, on_press=lambda x: app.send_command("Home")))
        
        # Linha 2
        nav_layout.add_widget(Button(text="◀", font_size='30sp', bold=True, on_press=lambda x: app.send_command("CursorLeft")))
        nav_layout.add_widget(Button(text="OK", font_size='24sp', bold=True, background_color=theme_manager.primary_color, on_press=lambda x: app.send_command("Confirm")))
        nav_layout.add_widget(Button(text="▶", font_size='30sp', bold=True, on_press=lambda x: app.send_command("CursorRight")))
        
        # Linha 3
        nav_layout.add_widget(Button(text="MENU", on_press=lambda x: app.send_command("Menu")))
        nav_layout.add_widget(Button(text="▼", font_size='30sp', bold=True, on_press=lambda x: app.send_command("CursorDown")))
        nav_layout.add_widget(Button(text="INFO", on_press=lambda x: app.send_command("Info")))
        
        main_layout.add_widget(nav_layout)

        # ÁREA DE CONTROLE INFERIOR
        control_layout = BoxLayout(spacing=dp(15), size_hint_y=0.4)
        
        # Canais
        chan_box = BoxLayout(orientation='vertical', spacing=dp(5))
        chan_box.add_widget(Button(text="CH +", font_size='20sp', bold=True, on_press=lambda x: app.send_command("ChannelUp")))
        chan_box.add_widget(Button(text="CH -", font_size='20sp', bold=True, on_press=lambda x: app.send_command("ChannelDown")))
        control_layout.add_widget(chan_box)
        
        # Utilidade
        util_box = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_x=0.6)
        util_box.add_widget(Button(text="MUTE", background_color=[0.5, 0.5, 0.5, 1], on_press=lambda x: app.send_command("Mute")))
        util_box.add_widget(Button(text="TECLADO (123)", background_color=theme_manager.primary_color, on_press=lambda x: app.show_numeric_keyboard()))
        util_box.add_widget(Button(text="BUSCAR TV", font_size='12sp', on_press=lambda x: app.go_to_scan()))
        control_layout.add_widget(util_box)
        
        # VOLUME (Direita)
        vol_box = BoxLayout(orientation='vertical', spacing=dp(5))
        vol_box.add_widget(Button(text="VOL +", font_size='22sp', bold=True, background_color=theme_manager.primary_color, on_press=lambda x: app.send_command("VolumeUp")))
        vol_box.add_widget(Button(text="VOL -", font_size='22sp', bold=True, background_color=theme_manager.primary_color, on_press=lambda x: app.send_command("VolumeDown")))
        control_layout.add_widget(vol_box)
        
        main_layout.add_widget(control_layout)
        self.add_widget(main_layout)
