from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.app import App
from kivy.graphics import Color, Rectangle
from app.widgets.rotary_knob import VolumeDisk, Joystick
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

        layout = GridLayout(cols=3, padding=dp(20), spacing=dp(30))
        
        # Coluna Esquerda: Joystick e Home
        left_col = BoxLayout(orientation='vertical', spacing=dp(15))
        left_col.add_widget(Label(text="NAVEGAÇÃO", color=theme_manager.text_color, font_size='12sp'))
        self.joystick = Joystick(size_hint=(None, None), size=(dp(150), dp(150)), pos_hint={'center_x': 0.5})
        self.joystick.on_move = app.send_command
        left_col.add_widget(self.joystick)
        
        home_btn = Button(text="HOME", size_hint_y=None, height=dp(50), background_color=theme_manager.primary_color)
        home_btn.bind(on_press=lambda x: app.send_command("Home"))
        left_col.add_widget(home_btn)
        layout.add_widget(left_col)
        
        # Coluna Central: Canais, OK e Back
        mid_col = BoxLayout(orientation='vertical', spacing=dp(10))
        mid_col.add_widget(Button(text="CH +", on_press=lambda x: app.send_command("ChannelUp")))
        mid_col.add_widget(Button(text="OK", background_color=theme_manager.primary_color, bold=True, on_press=lambda x: app.send_command("Confirm")))
        mid_col.add_widget(Button(text="CH -", on_press=lambda x: app.send_command("ChannelDown")))
        mid_col.add_widget(Button(text="VOLTAR", background_color=[0.4, 0.4, 0.4, 1], on_press=lambda x: app.send_command("Back")))
        layout.add_widget(mid_col)
        
        # Coluna Direita: Disco de Volume
        right_col = BoxLayout(orientation='vertical', spacing=dp(10))
        right_col.add_widget(Label(text="VOLUME", color=theme_manager.text_color, font_size='14sp', bold=True))
        self.disk = VolumeDisk(size_hint=(None, None), size=(dp(180), dp(180)), pos_hint={'center_x': 0.5})
        self.disk.on_volume_change = app.send_command
        self.disk.indicator_color = theme_manager.primary_color
        right_col.add_widget(self.disk)
        
        btn_box = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(50))
        mute_btn = Button(text="MUTE", background_color=[0.5, 0.5, 0.5, 1])
        mute_btn.bind(on_press=lambda x: app.send_command("Mute"))
        btn_box.add_widget(mute_btn)
        
        pwr_btn = Button(text="OFF", background_color=theme_manager.accent_color)
        pwr_btn.bind(on_press=lambda x: app.send_command("Standby"))
        btn_box.add_widget(pwr_btn)
        right_col.add_widget(btn_box)
        
        layout.add_widget(right_col)
        self.add_widget(layout)
