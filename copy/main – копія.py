
from kivymd.app import MDApp
from kivymd.uix.widget import MDWidget
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivy import platform
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp, sp
from random import randint
from kivy.uix.image import Image

if platform != 'android':
    Window.size = (800,600)
    Window.top =100
    Window.left=400

DRAGON_SPEED = dp(7)
FIREBALL_SPEED = dp(10)
FPS = 60

# === Main Screen Class ===
class MainScreen(MDScreen):
    def go_game(self):
        self.manager.current = 'game'

class GameScreen(MDScreen):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.eventKeys = {}
        self.fireBalls = []
        self.enemies = []

        Clock.schedule_interval(self.update,1/FPS)
        Clock.schedule_interval(self.spawn_enemy,2.5)
        

    def move_enemy(self,dt):
        enemy = self.ids.enemy
        enemy.x = (randint(0,int(Window.width- dp(30))))

    def spawn_enemy(self,dt):
        if self.manager.current == 'game':
            new_enemy = Enemy()
            self.enemies.append(new_enemy)

            self.ids.back.add_widget(new_enemy)       
    def update(self,dt):
        for key in self.eventKeys:
            if self.eventKeys[key] == True:
                if key == 'left':
                    self.moveLeft()
                if key == 'right':
                    self.moveRight()
                if key == 'shot':
                    self.shot()
                    self.eventKeys[key] = False

        for ball in self.fireBalls:
            ball.y += FIREBALL_SPEED
            if ball.y > Window.height:
                self.ids.front.remove_widget(ball)
                self.fireBalls.remove(ball)

        if self.manager.current == 'game':
            for enemy in self.enemies[:]:
                enemy.y -= dp(1)
                
                if enemy.y <= -dp(80):
                    self.ids.back.remove_widget(enemy)
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)
                    continue
                for ball in self.fireBalls[:]:
                    y_hit = enemy.y <= ball.y <= (enemy.y + dp(80))
                    x_hit = enemy.x <= ball.x <= (enemy.x + dp(60))

                    if x_hit and y_hit:
                        self.ids.back.remove_widget(enemy)
                        if enemy in self.enemies:
                            self.enemies.remove(enemy)
                        self.ids.front.remove_widget(ball)
                        if ball in self.fireBalls:
                            self.fireBalls.remove(ball)    
                        break 

        if self.ids.dragon.x >= Window.width - self.ids.dragon.width:
            self.ids.dragon.x = Window.width - self.ids.dragon.width
        elif self.ids.dragon.x <= 0:
            self.ids.dragon.x = 0


    def pause(self):
        pass

    def moveLeft(self):
        try:
            self.ids.dragon.pos[0] -= DRAGON_SPEED
        except:
            pass

    def moveRight(self):
        try:
            self.ids.dragon.pos[0] += DRAGON_SPEED
        except:
            pass

    def shot(self):
        try:
            shot = Shot(pos =(self.ids.dragon.center_x - 18, self.ids.dragon.center_y + 50))
            self.fireBalls.append(shot)
            self.ids.front.add_widget(shot)
        except:
            pass
    def pressKey(self,key):
        self.eventKeys[key] = True

    def releaseKey(self,key):
        self.eventKeys[key] = False

    def exit_to_menu(self):
        self.manager.current = 'main'


class Enemy(Image):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.size_hint = None,None
        self.size = (dp(150), dp(150))
        self.pos = (randint(0,int(Window.width- dp(60))), Window.height)


class Shot(Image):
    ...

class Pause(MDScreen):
    def __init__(self,**kwargs):
            super().__init__(**kwargs)
            
        #Зробити екран паузи...

class GameApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        self.is_paused = False
        sm = MDScreenManager()
        sm.add_widget(MainScreen(name ="main"))
        sm.add_widget(GameScreen(name = 'game'))

        return sm

    
app = GameApp()
app.run()