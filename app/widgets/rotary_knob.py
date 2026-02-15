import math
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, PushMatrix, PopMatrix, Rotate
from kivy.properties import NumericProperty, ObjectProperty, ListProperty
from kivy.metrics import dp

class RotaryKnob(Widget):
    angle = NumericProperty(0)
    on_volume_change = ObjectProperty(None)
    knob_color = ListProperty([0.3, 0.3, 0.3, 1])
    indicator_color = ListProperty([0.8, 0.2, 0.2, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            PushMatrix()
            self.rot = Rotate(origin=self.center, angle=0)
        with self.canvas:
            Color(0.1, 0.1, 0.1, 1)
            self.bg_ellipse = Ellipse(pos=self.pos, size=self.size)
            self.color_instr = Color(*self.knob_color)
            self.knob_ellipse = Ellipse(pos=(self.x + 5, self.y + 5), size=(self.width - 10, self.height - 10))
            self.ind_color_instr = Color(*self.indicator_color)
            self.indicator = Line(points=[], width=2)
        with self.canvas.after:
            PopMatrix()
        
        self.bind(pos=self._update_canvas, size=self._update_canvas, angle=self._update_rotation, knob_color=self._update_colors, indicator_color=self._update_colors)

    def _update_colors(self, *args):
        self.color_instr.rgba = self.knob_color
        self.ind_color_instr.rgba = self.indicator_color

    def _update_canvas(self, *args):
        self.bg_ellipse.pos = self.pos
        self.bg_ellipse.size = self.size
        self.knob_ellipse.pos = (self.x + dp(10), self.y + dp(10))
        self.knob_ellipse.size = (self.width - dp(20), self.height - dp(20))
        self.rot.origin = self.center
        self._update_indicator()

    def _update_rotation(self, *args):
        self.rot.angle = self.angle
        self._update_indicator()

    def _update_indicator(self, *args):
        rad = math.radians(self.angle + 90)
        r = (self.width / 2) - dp(15)
        cx, cy = self.center
        px = cx + r * math.cos(rad)
        py = cy + r * math.sin(rad)
        self.indicator.points = [cx, cy, px, py]

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            self._update_angle(touch)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self._update_angle(touch)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            return True
        return super().on_touch_up(touch)

    def _update_angle(self, touch):
        dx = touch.x - self.center_x
        dy = touch.y - self.center_y
        new_angle = math.degrees(math.atan2(dy, dx)) - 90
        diff = new_angle - self.angle
        if diff > 180: diff -= 360
        if diff < -180: diff += 360
        self.angle = new_angle
        if self.on_volume_change:
            if diff > 2: self.on_volume_change("VolumeUp")
            elif diff < -2: self.on_volume_change("VolumeDown")

class VolumeDisk(RotaryKnob):
    """Uma versão maior e mais estilizada para o modo paisagem."""
    def _update_canvas(self, *args):
        self.bg_ellipse.pos = self.pos
        self.bg_ellipse.size = self.size
        # Estilo disco
        self.knob_ellipse.pos = (self.x + dp(5), self.y + dp(5))
        self.knob_ellipse.size = (self.width - dp(10), self.height - dp(10))
        self.rot.origin = self.center
        self._update_indicator()

class Joystick(Widget):
    """Joystick direcional para navegação no menu."""
    on_move = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0.2, 0.2, 0.2, 1)
            self.outer = Ellipse(pos=self.pos, size=self.size)
            Color(0.4, 0.4, 0.4, 1)
            self.inner = Ellipse(pos=(self.center_x-dp(25), self.center_y-dp(25)), size=(dp(50), dp(50)))
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self.outer.pos = self.pos
        self.outer.size = self.size
        self.inner.pos = (self.center_x-dp(25), self.center_y-dp(25))

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            self._handle_move(touch)
            return True
    
    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self._handle_move(touch)
            return True

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self.inner.pos = (self.center_x-dp(25), self.center_y-dp(25))
            return True

    def _handle_move(self, touch):
        dx = touch.x - self.center_x
        dy = touch.y - self.center_y
        # Limita o movimento visual
        dist = math.sqrt(dx**2 + dy**2)
        max_dist = self.width/2 - dp(25)
        if dist > max_dist:
            dx = dx * max_dist / dist
            dy = dy * max_dist / dist
        self.inner.pos = (self.center_x + dx - dp(25), self.center_y + dy - dp(25))
        
        # Detecta direção para o comando
        if dist > dp(20):
            angle = math.degrees(math.atan2(dy, dx))
            if -45 <= angle <= 45: self.on_move("CursorRight")
            elif 45 < angle <= 135: self.on_move("CursorUp")
            elif -135 <= angle < -45: self.on_move("CursorDown")
            else: self.on_move("CursorLeft")
