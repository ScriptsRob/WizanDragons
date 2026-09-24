from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage

class FlyingDragonAnimation(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        tex = CoreImage('assets/dragon_shit.png').texture
        w, h = tex.width / 4, tex.height / 4
        
        self.frames = [tex.get_region(c*w, r*h, w, h) for r in reversed(range(4)) for c in range(4) if not (r == 1 and c == 0)]
        self.idx = 0
        
        with self.canvas:
            self.rect = Rectangle(texture=self.frames[0], size=(200, 200),
                                  pos=(Window.width/2 - 100, Window.height/2 - 100))
            
        Clock.schedule_interval(self.update, 1.0 / 12.0)
        
    def update(self, dt):
        self.idx = (self.idx + 1) % len(self.frames)
        self.rect.texture = self.frames[self.idx]

class DragonApp(App):
    def build(self):
        return FlyingDragonAnimation()

if __name__ == '__main__':
    DragonApp().run()
