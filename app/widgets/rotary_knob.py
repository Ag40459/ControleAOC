import math
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, PushMatrix, PopMatrix, Rotate
from kivy.properties import NumericProperty, ObjectProperty
from kivy.metrics import dp

class RotaryKnob(Widget):
    angle = NumericProperty(0)
    on_volume_change = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            PushMatrix()
            self.rot = Rotate(origin=self.center, angle=0)
        with self.canvas:
            Color(0.1, 0.1, 0.1, 1)
            self.bg_ellipse = Ellipse(pos=self.pos, size=self.size)
            Color(0.3, 0.3, 0.3, 1)
            self.knob_ellipse = Ellipse(pos=(self.x + 5, self.y + 5), size=(self.width - 10, self.height - 10))
            Color(0.8, 0.2, 0.2, 1)
            self.indicator = Line(points=[], width=2)
        with self.canvas.after:
            PopMatrix()
        
        self.bind(pos=self._update_canvas, size=self._update_canvas, angle=self._update_rotation)

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
            if diff > 0: self.on_volume_change("VolumeUp")
            elif diff < 0: self.on_volume_change("VolumeDown")
