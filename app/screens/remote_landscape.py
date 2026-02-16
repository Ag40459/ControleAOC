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
        self.display_label = None
        # Vincula a atualização à mudança de qualquer propriedade do tema
        theme_manager.bind(bg_color=self._update_canvas)
        theme_manager.bind(primary_color=self._update_canvas)

    def on_enter(self):
        self._update_canvas()
        self.update_display_text()

    def update_display_text(self, *args):
        if not self.display_label: return
        app = App.get_running_app()
        if app.tv_ip:
            self.display_label.text = f"CONECTADO: {app.tv_name} ({app.tv_ip})"
        else:
            self.display_label.text = "NÃO CONECTADO"

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*theme_manager.bg_color)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        app = App.get_running_app()
        
        main_layout = BoxLayout(orientation='horizontal', padding=dp(10), spacing=dp(15))
        
        # COLUNA ESQUERDA (Canais e Home/Back + Display)
        left_col = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_x=0.25)
        
        # Display estático na arte superior esquerda (Landscape)
        display_btn = Button(background_color=theme_manager.display_bg, size_hint_y=0.2)
        display_btn.bind(on_press=lambda x: app.show_rename_popup())
        self.display_label = Label(
            text="Carregando...", 
            bold=True, 
            color=theme_manager.display_text, 
            font_size='12sp',
            halign='left',
            valign='middle'
        )
        self.display_label.bind(size=self.display_label.setter('text_size'))
        display_btn.add_widget(self.display_label)
        left_col.add_widget(display_btn)
        
        left_col.add_widget(Button(text="CH +", font_size='20sp', bold=True, on_press=lambda x: app.send_command("ChannelUp")))
        left_col.add_widget(Button(text="HOME", background_color=theme_manager.primary_color, bold=True, on_press=lambda x: app.send_command("Home")))
        left_col.add_widget(Button(text="VOLTAR", background_color=[0.4, 0.4, 0.4, 1], on_press=lambda x: app.send_command("Back")))
        left_col.add_widget(Button(text="CH -", font_size='20sp', bold=True, on_press=lambda x: app.send_command("ChannelDown")))
        main_layout.add_widget(left_col)
        
        # COLUNA CENTRAL (Navegação Direcional)
        mid_col = GridLayout(cols=3, spacing=dp(5), size_hint_x=0.5)
        mid_col.add_widget(Button(text="MENU", on_press=lambda x: app.send_command("Menu")))
        mid_col.add_widget(Button(text="▲", font_size='30sp', bold=True, on_press=lambda x: app.send_command("CursorUp")))
        mid_col.add_widget(Button(text="OFF", background_color=theme_manager.accent_color, on_press=lambda x: app.send_command("Standby")))
        
        mid_col.add_widget(Button(text="◀", font_size='30sp', bold=True, on_press=lambda x: app.send_command("CursorLeft")))
        mid_col.add_widget(Button(text="OK", font_size='24sp', bold=True, background_color=theme_manager.primary_color, on_press=lambda x: app.send_command("Confirm")))
        mid_col.add_widget(Button(text="▶", font_size='30sp', bold=True, on_press=lambda x: app.send_command("CursorRight")))
        
        mid_col.add_widget(Button(text="123", on_press=lambda x: app.show_numeric_keyboard()))
        mid_col.add_widget(Button(text="▼", font_size='30sp', bold=True, on_press=lambda x: app.send_command("CursorDown")))
        mid_col.add_widget(Button(text="BUSCAR", on_press=lambda x: app.go_to_scan()))
        main_layout.add_widget(mid_col)
        
        # COLUNA DIREITA (Volume - Destaque)
        right_col = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_x=0.25)
        right_col.add_widget(Button(text="VOL +", font_size='24sp', bold=True, background_color=theme_manager.primary_color, on_press=lambda x: app.send_command("VolumeUp")))
        right_col.add_widget(Button(text="MUTE", background_color=[0.5, 0.5, 0.5, 1], on_press=lambda x: app.send_command("Mute")))
        right_col.add_widget(Button(text="VOL -", font_size='24sp', bold=True, background_color=theme_manager.primary_color, on_press=lambda x: app.send_command("VolumeDown")))
        main_layout.add_widget(right_col)
        
        self.add_widget(main_layout)
