import threading
import requests
import json
import os
import re
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.recycleview import RecycleView
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import StringProperty, ListProperty, DictProperty
from kivy.metrics import dp

from app.screens.scan_screen import ScanScreen
from app.screens.remote_portrait import RemotePortraitScreen
from app.screens.remote_landscape import RemoteLandscapeScreen
from app.utils.network import send_tv_command, send_tv_text, save_custom_name, get_custom_name
from app.utils.themes import theme_manager

class NetflixSearchPopup(Popup):
    def __init__(self, categories, **kwargs):
        super().__init__(**kwargs)
        self.title = "Buscar Categorias Netflix"
        self.size_hint = (0.9, 0.9)
        self.categories = categories # List of dicts: {'name': ..., 'code': ...}
        
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Campo de Busca
        self.search_input = TextInput(
            hint_text="Pesquisar (ex: terror, ação, anime)...",
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            font_size='18sp',
            background_color=[0.15, 0.15, 0.15, 1],
            foreground_color=[1, 1, 1, 1],
            cursor_color=theme_manager.primary_color
        )
        self.search_input.bind(text=self.filter_categories)
        layout.add_widget(self.search_input)
        
        # Lista de Resultados
        self.rv = RecycleView()
        self.rv_layout = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.rv_layout.bind(minimum_height=self.rv_layout.setter('height'))
        self.rv.add_widget(self.rv_layout)
        layout.add_widget(self.rv)
        
        # Botão Fechar
        close_btn = Button(text="VOLTAR AO CONTROLE", size_hint_y=None, height=dp(50), background_color=[0.6, 0.2, 0.2, 1], bold=True)
        close_btn.bind(on_release=self.dismiss)
        layout.add_widget(close_btn)
        
        self.content = layout
        self.update_list(self.categories[:50]) # Mostrar apenas os primeiros 50 inicialmente para performance

    def filter_categories(self, instance, value):
        if not value:
            self.update_list(self.categories[:50])
            return
            
        # Lógica de busca inteligente: ignorar maiúsculas/minúsculas e procurar em qualquer parte do texto
        search_terms = value.lower().split()
        filtered = []
        for c in self.categories:
            cat_name = c['name'].lower()
            # Verifica se todos os termos digitados estão presentes no nome da categoria (em qualquer ordem)
            if all(term in cat_name for term in search_terms):
                filtered.append(c)
        
        self.update_list(filtered[:100]) # Limitar a 100 resultados para manter fluidez

    def update_list(self, items):
        self.rv_layout.clear_widgets()
        for item in items:
            btn = Button(
                text=item['name'],
                size_hint_y=None,
                height=dp(55),
                background_color=[0.25, 0.25, 0.25, 1],
                halign='center',
                valign='middle'
            )
            btn.bind(size=btn.setter('text_size'))
            btn.bind(on_release=lambda x, it=item: self.show_code_modal(it))
            self.rv_layout.add_widget(btn)

    def show_code_modal(self, item):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        content.add_widget(Label(
            text=f"Código para:\n[b]{item['name']}[/b]",
            markup=True,
            halign='center',
            font_size='18sp'
        ))
        
        code_label = Label(
            text=str(item['code']),
            font_size='56sp',
            bold=True,
            color=theme_manager.primary_color
        )
        content.add_widget(code_label)
        
        msg_label = Label(
            text="Digite este código no campo de\nbusca do seu aplicativo Netflix.",
            halign='center',
            font_size='14sp',
            color=[0.7, 0.7, 0.7, 1]
        )
        content.add_widget(msg_label)
        
        btn = Button(
            text="FECHAR",
            size_hint_y=None,
            height=dp(60),
            background_color=theme_manager.primary_color,
            bold=True
        )
        content.add_widget(btn)
        
        popup = Popup(
            title="Código da Categoria",
            content=content,
            size_hint=(0.85, 0.6),
            auto_dismiss=True
        )
        btn.bind(on_release=popup.dismiss)
        popup.open()

class RemoteControlApp(App):
    tv_ip = StringProperty("")
    tv_name = StringProperty("TV AOC")
    tv_port = 1925
    supported_keys = ListProperty([])
    netflix_categories = ListProperty([])

    def build(self):
        self.title = "Controle AOC Pro"
        self.load_netflix_categories()
        self.sm = ScreenManager(transition=FadeTransition())
        self.sm.add_widget(ScanScreen())
        self.sm.add_widget(RemotePortraitScreen())
        self.sm.add_widget(RemoteLandscapeScreen())
        Window.bind(on_size=self._on_resize)
        return self.sm

    def load_netflix_categories(self):
        json_path = 'assets/netflix_codes_full.json'
        if not os.path.exists(json_path):
            json_path = '/home/ubuntu/ControleAOC_New/assets/netflix_codes_full.json'
            
        try:
            if os.path.exists(json_path):
                with open(json_path, mode='r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.netflix_categories = [
                        {'name': f"{item.get('category', '')} - {item.get('subcategory', '')}", 'code': item.get('code', '')}
                        for item in data
                    ]
            else:
                print("Arquivo JSON não encontrado.")
        except Exception as e:
            print(f"Erro ao carregar categorias: {e}")
            self.netflix_categories = []

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

    def show_netflix_search(self):
        if not self.netflix_categories:
            self.load_netflix_categories()
        if self.netflix_categories:
            NetflixSearchPopup(self.netflix_categories).open()
        else:
            self._show_error("Lista de categorias não encontrada.")

    def send_command(self, cmd):
        threading.Thread(target=send_tv_command, args=(self.tv_ip, self.tv_port, cmd), daemon=True).start()

    def send_text(self, text):
        threading.Thread(target=send_tv_text, args=(self.tv_ip, self.tv_port, text), daemon=True).start()

if __name__ == '__main__':
    RemoteControlApp().run()
