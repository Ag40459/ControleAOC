from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.app import App
from kivy.graphics import Color, Rectangle
from app.widgets.rotary_knob import RotaryKnob, Joystick
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

        main_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        # Barra Superior: Voltar e Power
        top_bar = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        back_btn = Button(text='<', size_hint_x=None, width=dp(50), background_color=theme_manager.primary_color)
        back_btn.bind(on_press=lambda x: app.go_to_scan())
        top_bar.add_widget(back_btn)
        
        # Display Digital
        display_box = Button(background_color=theme_manager.display_bg, size_hint_x=1)
        display_box.bind(on_press=lambda x: app.show_rename_popup())
        display_layout = BoxLayout(orientation='vertical', padding=dp(5))
        self.tv_name_lbl = Label(text=app.tv_name, bold=True, color=theme_manager.display_text, font_size='14sp')
        self.tv_ip_lbl = Label(text=app.tv_ip, color=theme_manager.display_text, font_size='12sp')
        display_layout.add_widget(self.tv_name_lbl)
        display_layout.add_widget(self.tv_ip_lbl)
        display_box.add_widget(display_layout)
        top_bar.add_widget(display_box)
        
        pwr_btn = Button(text='OFF', size_hint_x=None, width=dp(60), background_color=theme_manager.accent_color, bold=True)
        pwr_btn.bind(on_press=lambda x: app.send_command("Standby"))
        top_bar.add_widget(pwr_btn)
        main_layout.add_widget(top_bar)

        # Meio: Joystick e Volume (Ergonomia)
        mid_layout = BoxLayout(spacing=dp(20))
        
        # Lado Esquerdo: Joystick
        joy_box = BoxLayout(orientation='vertical', spacing=dp(10))
        joy_box.add_widget(Label(text="NAVEGAÇÃO", font_size='10sp', color=theme_manager.text_color))
        self.joystick = Joystick(size_hint=(None, None), size=(dp(160), dp(160)), pos_hint={'center_x': 0.5})
        self.joystick.on_move = app.send_command
        joy_box.add_widget(self.joystick)
        
        ok_btn = Button(text="OK", size_hint=(None, None), size=(dp(60), dp(60)), pos_hint={'center_x': 0.5}, background_color=theme_manager.primary_color, bold=True)
        ok_btn.bind(on_press=lambda x: app.send_command("Confirm"))
        joy_box.add_widget(ok_btn)
        mid_layout.add_widget(joy_box)
        
        # Lado Direito: Volume (Botão Giratório)
        vol_box = BoxLayout(orientation='vertical', spacing=dp(10))
        vol_box.add_widget(Label(text="VOLUME", font_size='10sp', color=theme_manager.text_color))
        self.knob = RotaryKnob(size_hint=(None, None), size=(dp(140), dp(140)), pos_hint={'center_x': 0.5})
        self.knob.on_volume_change = app.send_command
        self.knob.knob_color = [0.2, 0.2, 0.2, 1]
        self.knob.indicator_color = theme_manager.primary_color
        vol_box.add_widget(self.knob)
        
        mute_btn = Button(text="MUTE", size_hint=(None, None), size=(dp(80), dp(45)), pos_hint={'center_x': 0.5}, background_color=[0.5, 0.5, 0.5, 1])
        mute_btn.bind(on_press=lambda x: app.send_command("Mute"))
        vol_box.add_widget(mute_btn)
        mid_layout.add_widget(vol_box)
        
        main_layout.add_widget(mid_layout)

        # Parte Inferior: Home, Voltar, Canais e Teclado
        bottom_grid = GridLayout(cols=3, spacing=dp(15), size_hint_y=None, height=dp(140))
        
        home_btn = Button(text="HOME", background_color=theme_manager.primary_color, bold=True)
        home_btn.bind(on_press=lambda x: app.send_command("Home"))
        bottom_grid.add_widget(home_btn)
        
        chan_up = Button(text="CH +")
        chan_up.bind(on_press=lambda x: app.send_command("ChannelUp"))
        bottom_grid.add_widget(chan_up)
        
        back_btn_main = Button(text="VOLTAR", background_color=[0.4, 0.4, 0.4, 1])
        back_btn_main.bind(on_press=lambda x: app.send_command("Back"))
        bottom_grid.add_widget(back_btn_main)
        
        key_btn = Button(text="123", background_color=theme_manager.primary_color)
        key_btn.bind(on_press=lambda x: app.show_numeric_keyboard())
        bottom_grid.add_widget(key_btn)
        
        chan_down = Button(text="CH -")
        chan_down.bind(on_press=lambda x: app.send_command("ChannelDown"))
        bottom_grid.add_widget(chan_down)
        
        src_btn = Button(text="FONTE")
        src_btn.bind(on_press=lambda x: app.send_command("Source"))
        bottom_grid.add_widget(src_btn)
        
        main_layout.add_widget(bottom_grid)
        self.add_widget(main_layout)
