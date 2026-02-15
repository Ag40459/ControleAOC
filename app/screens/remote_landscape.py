from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.app import App
from app.widgets.rotary_knob import RotaryKnob

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
        left_col = BoxLayout(orientation='vertical', spacing=dp(15))
        left_col.add_widget(Button(text="CANAL +", font_size='24sp', on_press=lambda x: app.send_command("ChannelUp")))
        left_col.add_widget(Button(text="MUTE", font_size='20sp', background_color=(0.5, 0.5, 0.5, 1), on_press=lambda x: app.send_command("Mute")))
        left_col.add_widget(Button(text="CANAL -", font_size='24sp', on_press=lambda x: app.send_command("ChannelDown")))
        layout.add_widget(left_col)
        mid_col = BoxLayout(orientation='vertical', spacing=dp(10))
        mid_col.add_widget(Label(text="VOLUME", font_size='24sp', bold=True))
        self.knob = RotaryKnob(size_hint=(None, None), size=(dp(200), dp(200)), pos_hint={'center_x': 0.5})
        self.knob.on_volume_change = app.send_command
        anchor = AnchorLayout()
        anchor.add_widget(self.knob)
        mid_col.add_widget(anchor)
        layout.add_widget(mid_col)
        right_col = BoxLayout(orientation='vertical', spacing=dp(15))
        right_col.add_widget(Button(text="HOME", font_size='20sp', on_press=lambda x: app.send_command("Home")))
        right_col.add_widget(Button(text="VOLTAR AO SCAN", font_size='18sp', background_color=(0.7, 0.2, 0.2, 1), on_press=lambda x: app.go_to_scan()))
        right_col.add_widget(Button(text="POWER", font_size='20sp', background_color=(0.8, 0.1, 0.1, 1), on_press=lambda x: app.send_command("Standby")))
        layout.add_widget(right_col)
        self.add_widget(layout)
