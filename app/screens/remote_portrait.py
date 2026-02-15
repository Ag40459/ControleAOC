from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.app import App

class RemotePortraitScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'remote_portrait'
        self.buttons = {}

    def on_enter(self):
        self.build_ui()
        App.get_running_app().verify_supported_keys(self)

    def build_ui(self):
        self.clear_widgets()
        app = App.get_running_app()
        main_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(8))
        status_bar = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        back_btn = Button(text='< BUSCAR', size_hint_x=0.3, background_color=(0.7, 0.2, 0.2, 1))
        back_btn.bind(on_press=lambda x: app.go_to_scan())
        status_bar.add_widget(back_btn)
        self.status_lbl = Label(text=f"TV: {app.tv_ip}", bold=True, color=(0, 1, 0, 1))
        status_bar.add_widget(self.status_lbl)
        main_layout.add_widget(status_bar)
        top_row = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(20))
        top_row.add_widget(self._create_btn("Power", "Standby", (0.8, 0.1, 0.1, 1)))
        top_row.add_widget(self._create_btn("Fonte", "Source", (0.2, 0.2, 0.2, 1)))
        main_layout.add_widget(top_row)
        num_grid = GridLayout(cols=3, spacing=dp(5), size_hint_y=None, height=dp(180))
        for i in range(1, 10): num_grid.add_widget(self._create_btn(str(i), f"Digit{i}"))
        num_grid.add_widget(self._create_btn("-/--", "DigitDash"))
        num_grid.add_widget(self._create_btn("0", "Digit0"))
        num_grid.add_widget(self._create_btn("Teclado", "Keyboard", (0.2, 0.5, 0.8, 1)))
        main_layout.add_widget(num_grid)
        nav_box = AnchorLayout(size_hint_y=None, height=dp(180))
        nav_grid = GridLayout(cols=3, spacing=dp(2), size=(dp(180), dp(180)), size_hint=(None, None))
        nav_grid.add_widget(Widget())
        nav_grid.add_widget(self._create_btn("▲", "CursorUp"))
        nav_grid.add_widget(Widget())
        nav_grid.add_widget(self._create_btn("◀", "CursorLeft"))
        nav_grid.add_widget(self._create_btn("OK", "Confirm", (0.1, 0.5, 0.1, 1)))
        nav_grid.add_widget(self._create_btn("▶", "CursorRight"))
        nav_grid.add_widget(Widget())
        nav_grid.add_widget(self._create_btn("▼", "CursorDown"))
        nav_grid.add_widget(Widget())
        nav_box.add_widget(nav_grid)
        main_layout.add_widget(nav_box)
        menu_row = GridLayout(cols=4, spacing=dp(5), size_hint_y=None, height=dp(50))
        for t, c in [("Menu", "Menu"), ("Home", "Home"), ("Voltar", "Back"), ("Info", "Info")]:
            menu_row.add_widget(self._create_btn(t, c))
        main_layout.add_widget(menu_row)
        vol_chan_row = BoxLayout(spacing=dp(20), size_hint_y=None, height=dp(120))
        vol_box = BoxLayout(orientation='vertical', spacing=dp(5))
        vol_box.add_widget(self._create_btn("VOL +", "VolumeUp"))
        vol_box.add_widget(self._create_btn("MUTE", "Mute", (0.5, 0.5, 0.5, 1)))
        vol_box.add_widget(self._create_btn("VOL -", "VolumeDown"))
        chan_box = BoxLayout(orientation='vertical', spacing=dp(5))
        chan_box.add_widget(self._create_btn("CH +", "ChannelUp"))
        chan_box.add_widget(Label(text="CANAL", font_size='12sp'))
        chan_box.add_widget(self._create_btn("CH -", "ChannelDown"))
        vol_chan_row.add_widget(vol_box)
        vol_chan_row.add_widget(chan_box)
        main_layout.add_widget(vol_chan_row)
        self.add_widget(main_layout)

    def _create_btn(self, text, cmd, color=None):
        btn = Button(text=text, background_color=color if color else (0.2, 0.2, 0.2, 1), bold=True)
        btn.bind(on_press=lambda x: App.get_running_app().send_command(cmd))
        self.buttons[cmd] = btn
        return btn
