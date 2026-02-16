from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.app import App
from kivy.graphics import Color, Rectangle
from app.utils.themes import theme_manager

class RemoteLandscapeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'remote_landscape'
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

        # Layout Principal com Barra Superior e Conteúdo
        root_layout = BoxLayout(orientation='vertical', padding=dp(5), spacing=dp(5))
        
        # BARRA SUPERIOR (Landscape)
        top_bar = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        display_btn = Button(background_color=theme_manager.display_bg, size_hint_x=0.8)
        display_btn.bind(on_press=lambda x: app.show_rename_popup())
        display_content = BoxLayout(orientation='horizontal', padding=dp(5), spacing=dp(10))
        display_content.add_widget(Label(text=app.tv_name, bold=True, color=theme_manager.display_text, font_size='14sp'))
        display_content.add_widget(Label(text=app.tv_ip if app.tv_ip else "BUSCAR TV", color=theme_manager.display_text, font_size='12sp'))
        display_btn.add_widget(display_content)
        
        pwr_btn = Button(text='OFF', size_hint_x=0.2, background_color=theme_manager.accent_color, bold=True)
        pwr_btn.bind(on_press=lambda x: app.send_command("Standby"))
        
        top_bar.add_widget(display_btn)
        top_bar.add_widget(pwr_btn)
        root_layout.add_widget(top_bar)

        # CONTEÚDO (Colunas)
        main_layout = BoxLayout(orientation='horizontal', spacing=dp(15))
        
        # COLUNA ESQUERDA (Canais e Home/Back)
        left_col = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_x=0.25)
        left_col.add_widget(Button(text="CH +", font_size='20sp', bold=True, on_press=lambda x: app.send_command("ChannelUp")))
        left_col.add_widget(Button(text="HOME", background_color=theme_manager.primary_color, bold=True, on_press=lambda x: app.send_command("Home")))
        left_col.add_widget(Button(text="VOLTAR", background_color=[0.4, 0.4, 0.4, 1], on_press=lambda x: app.send_command("Back")))
        left_col.add_widget(Button(text="CH -", font_size='20sp', bold=True, on_press=lambda x: app.send_command("ChannelDown")))
        main_layout.add_widget(left_col)
        
        # COLUNA CENTRAL (Navegação Direcional)
        mid_col = GridLayout(cols=3, spacing=dp(5), size_hint_x=0.5)
        mid_col.add_widget(Button(text="MENU", on_press=lambda x: app.send_command("Menu")))
        mid_col.add_widget(Button(text="UP", font_size='20sp', bold=True, on_press=lambda x: app.send_command("CursorUp")))
        mid_col.add_widget(Button(text="INFO", on_press=lambda x: app.send_command("Info")))
        
        mid_col.add_widget(Button(text="LEFT", font_size='20sp', bold=True, on_press=lambda x: app.send_command("CursorLeft")))
        mid_col.add_widget(Button(text="OK", font_size='24sp', bold=True, background_color=theme_manager.primary_color, on_press=lambda x: app.send_command("Confirm")))
        mid_col.add_widget(Button(text="RIGHT", font_size='20sp', bold=True, on_press=lambda x: app.send_command("CursorRight")))
        
        mid_col.add_widget(Button(text="TECLADO", on_press=lambda x: app.show_numeric_keyboard()))
        mid_col.add_widget(Button(text="DOWN", font_size='20sp', bold=True, on_press=lambda x: app.send_command("CursorDown")))
        mid_col.add_widget(Button(text="NETFLIX", background_color=[0.9, 0.1, 0.1, 1], bold=True, on_press=lambda x: app.show_netflix_search()))
        main_layout.add_widget(mid_col)
        
        # COLUNA DIREITA (Volume - Destaque)
        right_col = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_x=0.25)
        right_col.add_widget(Button(text="VOL +", font_size='24sp', bold=True, background_color=theme_manager.primary_color, on_press=lambda x: app.send_command("VolumeUp")))
        right_col.add_widget(Button(text="MUTE", background_color=[0.5, 0.5, 0.5, 1], on_press=lambda x: app.send_command("Mute")))
        right_col.add_widget(Button(text="VOL -", font_size='24sp', bold=True, background_color=theme_manager.primary_color, on_press=lambda x: app.send_command("VolumeDown")))
        main_layout.add_widget(right_col)
        
        root_layout.add_widget(main_layout)
        self.add_widget(root_layout)
