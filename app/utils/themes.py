from kivy.event import EventDispatcher
from kivy.properties import ListProperty, StringProperty

class ThemeManager(EventDispatcher):
    bg_color = ListProperty([0.05, 0.05, 0.05, 1])
    primary_color = ListProperty([0.2, 0.6, 1, 1])
    accent_color = ListProperty([0.8, 0.2, 0.2, 1])
    text_color = ListProperty([1, 1, 1, 1])
    display_bg = ListProperty([0.1, 0.2, 0.1, 1])
    display_text = ListProperty([0, 1, 0, 1])
    theme_name = StringProperty("Escuro")

    themes = {
        "Escuro": {
            "bg": [0.05, 0.05, 0.05, 1],
            "primary": [0.2, 0.6, 1, 1],
            "accent": [0.8, 0.2, 0.2, 1],
            "display_bg": [0.1, 0.2, 0.1, 1],
            "display_text": [0, 1, 0, 1],
            "text": [1, 1, 1, 1]
        },
        "Azul Oceano": {
            "bg": [0, 0.1, 0.2, 1],
            "primary": [0, 0.5, 0.8, 1],
            "accent": [1, 0.4, 0, 1],
            "display_bg": [0, 0.2, 0.3, 1],
            "display_text": [0.5, 1, 1, 1],
            "text": [1, 1, 1, 1]
        },
        "Moderno": {
            "bg": [0.9, 0.9, 0.9, 1],
            "primary": [0.2, 0.2, 0.2, 1],
            "accent": [0.1, 0.6, 0.4, 1],
            "display_bg": [0.8, 0.8, 0.8, 1],
            "display_text": [0.2, 0.2, 0.2, 1],
            "text": [0.1, 0.1, 0.1, 1]
        }
    }

    def set_theme(self, name):
        if name in self.themes:
            t = self.themes[name]
            # Usamos o fatiamento [:] ou a criação de nova lista para garantir que o Kivy detecte a mudança
            self.bg_color = list(t["bg"])
            self.primary_color = list(t["primary"])
            self.accent_color = list(t["accent"])
            self.display_bg = list(t["display_bg"])
            self.display_text = list(t["display_text"])
            self.text_color = list(t.get("text", [1, 1, 1, 1]))
            self.theme_name = name

# Instância global
theme_manager = ThemeManager()
