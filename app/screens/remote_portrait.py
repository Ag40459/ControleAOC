from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from app.utils.themes import theme_manager

class RemotePortraitScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'remote_portrait'
        self.marquee_offset = 0
        self.display_label = None
        self._bg_rect = None
        # Não buildamos no init para evitar erros de contexto
    
    def on_enter(self):
        self.build_ui()
        Clock.schedule_interval(self.update_marquee, 0.2)

    def on_leave(self):
        Clock.unschedule(self.update_marquee)

    def update_marquee(self, dt):
        if not self.display_label: return
        app = App.get_running_app()
        full_text = f" CONECTADO: {app.tv_name} ({app.tv_ip})  ***  "
        if len(full_text) < 20:
            self.display_label.text = full_text
            return
        self.marquee_offset = (self.marquee_offset + 1) % len(full_text)
        display_part = full_text[self.marquee_offset:] + full_text[:self.marquee_offset]
        self.display_label.text = display_part[:25]

    def build_ui(self):
        self.clear_widgets()
        app = App.get_running_app()
        
        # Fundo sólido via canvas
        with self.canvas.before:
            self.canvas.before.clear()
            Color(*theme_manager.bg_color)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        
        # Vincula o redimensionamento do fundo
        self.bind(pos=self._update_rect, size=self._update_rect)

        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Barra Superior
        top_bar = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        display_btn = Button(background_color=theme_manager.display_bg, size_hint_x=0.8)
        display_btn.bind(on_press=lambda x: app.show_rename_popup())
        self.display_label = Label(text="Conectando...", bold=True, color=theme_manager.display_text, font_size='18sp')
        display_btn.add_widget(self.display_label)
        top_bar.add_widget(display_btn)
        
        pwr_btn = Button(text='OFF', size_hint_x=0.2, background_color=theme_manager.accent_color, bold=True)
        pwr_btn.bind(on_press=lambda x: app.send_command("Standby"))
        top_bar.add_widget(pwr_btn)
        main_layout.add_widget(top_bar)

        # Navegação
        nav_layout = GridLayout(cols=3, spacing=dp(5), size_hint_y=0.4)
        for txt, cmd, color in [
            ("VOLTAR", "Back", [0.4, 0.4, 0.4, 1]), ("UP", "CursorUp", None), ("HOME", "Home", theme_manager.primary_color),
            ("LEFT", "CursorLeft", None), ("OK", "Confirm", theme_manager.primary_color), ("RIGHT", "CursorRight", None),
            ("MENU", "Menu", None), ("DOWN", "CursorDown", None), ("INFO", "Info", None)
        ]:
            btn = Button(text=txt, bold=True, background_color=color if color else [0.2, 0.2, 0.2, 1])
            btn.bind(on_press=lambda x, c=cmd: app.send_command(c))
            nav_layout.add_widget(btn)
        main_layout.add_widget(nav_layout)

        # Inferior
        bot_layout = BoxLayout(spacing=dp(15), size_hint_y=0.4)
        
        # CH
        ch_box = BoxLayout(orientation='vertical', spacing=dp(5))
        ch_up = Button(text="CH +", bold=True, on_press=lambda x: app.send_command("ChannelUp"))
        ch_down = Button(text="CH -", bold=True, on_press=lambda x: app.send_command("ChannelDown"))
        ch_box.add_widget(ch_up)
        ch_box.add_widget(ch_down)
        bot_layout.add_widget(ch_box)
        
        # Utils
        util_box = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_x=0.6)
        util_box.add_widget(Button(text="MUTE", on_press=lambda x: app.send_command("Mute")))
        kb_row = BoxLayout(spacing=dp(5))
        kb_row.add_widget(Button(text="123", background_color=theme_manager.primary_color, on_press=lambda x: app.show_numeric_keyboard()))
        kb_row.add_widget(Button(text="ABC", background_color=theme_manager.primary_color, on_press=lambda x: app.show_qwerty_keyboard()))
        util_box.add_widget(kb_row)
        util_box.add_widget(Button(text="BUSCAR", font_size='12sp', on_press=lambda x: app.go_to_scan()))
        bot_layout.add_widget(util_box)
        
        # VOL
        vol_box = BoxLayout(orientation='vertical', spacing=dp(5))
        vol_box.add_widget(Button(text="VOL +", bold=True, background_color=theme_manager.primary_color, on_press=lambda x: app.send_command("VolumeUp")))
        vol_box.add_widget(Button(text="VOL -", bold=True, background_color=theme_manager.primary_color, on_press=lambda x: app.send_command("VolumeDown")))
        bot_layout.add_widget(vol_box)
        
        main_layout.add_widget(bot_layout)
        self.add_widget(main_layout)

    def _update_rect(self, instance, value):
        if self._bg_rect:
            self._bg_rect.pos = instance.pos
            self._bg_rect.size = instance.size
