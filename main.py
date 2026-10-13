
from kivymd.app import MDApp
from kivymd.uix.widget import MDWidget
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivy import platform
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp, sp
from random import randint,random
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.animation import Animation 
from kivy.core.audio import SoundLoader
from kivy.graphics import Rectangle
from kivy.core.image import ImageLoader
from kivymd.app import MDApp as App


if platform != 'android':
    Window.size = (800,600)
    Window.top =100
    Window.left=400

SPELL_SPEED = dp(6)
DRAGON_SPEED = dp(7)
FIREBALL_SPEED = dp(10)
ENEMY_SPEED = dp(1)
FPS = 60
BG_SPEED = dp(1)

# === Main Screen Class ===
class MainScreen(MDScreen):
    def go_game(self):
        self.manager.current = 'game'

class GameScreen(MDScreen):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.eventKeys = {}
        self.fireBalls = []
        self.enemies_spells =[]
        self.enemies = []
        self.kills = 0
        self.dragon_hp = 100
        self.game_over = False
        self.is_paused = False
        self.wave = None
        Clock.schedule_interval(self.update,1/FPS)
        Clock.schedule_interval(self.spawn_enemy,2.5)

        self.sound = None

        self.sound = SoundLoader.load('assets/sounds/bg_music.wav')
        self.fire_sound = SoundLoader.load('assets/sounds/fire_sound.wav')
        self.button_sound = SoundLoader.load("assets/sounds/ui_sound_cl.wav")
        self.comeback_sound = SoundLoader.load("assets/sounds/ui_sound_deni.wav")
        

        self.sound.volume = 0.15

    def on_enter(self):
        if self.sound:
            self.sound.loop = True
            self.sound.play()
        self.reset_game()
        
    def reset_game(self):
            for item in self.enemies + self.fireBalls + self.enemies_spells:
                if item.parent:
                    item.parent.remove_widget(item)

            self.enemies.clear()
            self.fireBalls.clear()
            self.enemies_spells.clear()
            
            self.dragon_hp = 100
            self.score = 0
            self.game_over = False
            self.is_paused = False

            if 'health_bar' in self.ids:
                self.ids.health_bar.value = self.dragon_hp
            if 'hp_label' in self.ids:
                self.ids.hp_label.text = str(self.dragon_hp)
            if 'game_over_label' in self.ids:
                self.ids.game_over_label.opacity = 0
            if 'pause_menu' in self.ids:
                self.ids.pause_menu.opacity = 0
                self.ids.pause_menu.disabled = True

    def enemy_shot(self,enemy):
        enemy_spell = EnemySpell(pos= (enemy.center_x- 25,enemy.center_y + 10))
        self.enemies_spells.append(enemy_spell)
        self.ids.front.add_widget(enemy_spell)

    def move_enemy(self,dt):
        enemy = self.ids.enemy
        enemy.x = (randint(0,int(Window.width- dp(30))))

    def spawn_enemy(self,dt):
        if self.manager.current != 'game' or self.game_over == True or self.is_paused == True:
            return
        new_enemy = Enemy()
        self.enemies.append(new_enemy)

        self.ids.back.add_widget(new_enemy) 

    sound = SoundLoader.load('assets/bg_music')
    def win(self):
        pass
    def start_next_wave(self,wave):
        self.wave += 1


    def update(self,dt):
        if self.manager.current != 'game' or self.game_over == True or self.is_paused == True:
            return

        self.ids.bg1.x = 0
        self.ids.bg2.x = 0
        self.ids.bg1.size = (self.width, self.height)
        self.ids.bg2.size = (self.width, self.height)


        self.ids.bg1.y -= BG_SPEED
        self.ids.bg2.y -= BG_SPEED

        self.ids.bg2.height = self.ids.bg1.height

        if self.ids.bg1.y <= - self.ids.bg1.height:
            self.ids.bg1.y = self.ids.bg2.top


        if self.ids.bg2.y <= - self.ids.bg2.height:
                    self.ids.bg2.y = self.ids.bg1.top
        for key in self.eventKeys:
            if self.eventKeys[key] == True:
                if key == 'left':
                    self.moveLeft()
                if key == 'right':
                    self.moveRight()
                if key == 'shot':
                    self.shot()
                    self.eventKeys[key] = False

        for spell in self.enemies_spells[:]:
            dragon_top_y = self.ids.dragon.center_y + dp(45)


            x_hit = abs(self.ids.dragon.center_x - spell.center_x)
            y_hit = abs(dragon_top_y - spell.center_y)

            max_allowed_distance_x = dp(65) 
            max_allowed_distance_y = dp(10)

            spell.y -= SPELL_SPEED
            if x_hit <= max_allowed_distance_x and y_hit <= max_allowed_distance_y:
                self.enemies_spells.remove(spell)
                self.ids.front.remove_widget(spell)
                self.update_health(10)

            elif spell.y <= 0:
                if spell in self.enemies_spells:
                    self.enemies_spells.remove(spell)
                    self.ids.front.remove_widget(spell)
            
        for ball in self.fireBalls[:]:
            ball.y += FIREBALL_SPEED
            if ball.y > Window.height:
                self.ids.front.remove_widget(ball)
                if ball in self.fireBalls:
                    self.fireBalls.remove(ball)


        for enemy in self.enemies[:]:
            enemy.y -= ENEMY_SPEED
            if enemy.top > 0 and random() < 0.0035: 
                self.enemy_shot(enemy)

            if enemy.y <= 0:
                self.ids.back.remove_widget(enemy)
                if enemy in self.enemies:
                    self.enemies.remove(enemy)
                continue

            for ball in self.fireBalls[:]:
                x_hit = abs(enemy.center_x - ball.center_x - dp(15))
                y_hit = abs(enemy.center_y - ball.center_y)
                max_allowed_distance_x = dp(40) 
                max_allowed_distance_y = dp(40)

                if x_hit <= max_allowed_distance_x and y_hit <= max_allowed_distance_y:
                    self.ids.back.remove_widget(enemy)

                    if enemy in self.enemies:
                        self.enemies.remove(enemy)

                    self.ids.front.remove_widget(ball)

                    if ball in self.fireBalls:
                        self.fireBalls.remove(ball)    
                    break 

        if self.ids.dragon.x < 0:
            self.ids.dragon.x = 0
        elif self.ids.dragon.right > Window.width:
            self.ids.dragon.right = Window.width

    def update_health(self, damage):
        health_bar = self.ids.health_bar
        self.dragon_hp = max(0, self.dragon_hp - damage)
        self.ids.hp_label.text = str(self.dragon_hp)
        anim = Animation(value=self.dragon_hp, duration=0.1, transition="out_quad")
        anim.stop(health_bar)
        anim.start(health_bar)
        if self.dragon_hp == 0:
            self.end_game()
        
    def end_game(self):
        if self.sound:
            self.sound.stop()
        self.game_over = True
        for enemy in self.enemies[:]:
            self.enemies.remove(enemy)
            self.ids.back.remove_widget(enemy)

        for ball in self.fireBalls[:]:
            self.ids.front.remove_widget(ball)
            self.fireBalls.remove(ball) 
        for spell in self.enemies_spells[:]:
            self.enemies_spells.remove(spell)
            self.ids.front.remove_widget(spell)

        self.ids.game_over_label.opacity = 1
        Clock.schedule_once(lambda dt: self.go_menu(), 3)


    
    def pause(self):
        self.is_paused = True
        self.ids.pause_menu.opacity = 0.75
        self.ids.pause_menu.disabled = False
        if self.sound:
            self.sound.stop()

    def resume(self):
        self.is_paused = False
        self.ids.pause_menu.opacity = 0
        self.ids.pause_menu.disabled = True
        if self.sound:
            self.sound.play()
    def moveLeft(self):
        self.ids.dragon.pos[0] -= DRAGON_SPEED

    def moveRight(self):
        try:
            self.ids.dragon.pos[0] += DRAGON_SPEED
        except:
            pass

    def shot(self):
        self.fire_sound.play()
        shot = Shot(pos =(self.ids.dragon.center_x - 18, self.ids.dragon.center_y + 50))
        self.fireBalls.append(shot)
        self.ids.front.add_widget(shot)

    def pressKey(self,key):
        self.eventKeys[key] = True

    def releaseKey(self,key):
        self.eventKeys[key] = False

    def exit_to_menu(self):
        self.manager.current = 'main'

    def go_menu(self):
        self.manager.current = 'main'
        self.ids.pause_menu.opacity = 0
        self.is_paused = False
        if self.sound:
            self.sound.stop()
    def play_sound(sound):
        if sound:
            sound.play()

class Enemy(Image):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.size_hint = None,None
        self.size = (dp(150), dp(150))
        space = dp(20)
        min_x = int(space)
        max_x = int(Window.width - self.size[0] - space)
        
        if max_x <= min_x:
            spawn_x = min_x
        else:
            spawn_x = randint(min_x, max_x)

        self.pos = (spawn_x, Window.height)

class Dragon(Image):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(150), dp(150))
        self.frames = []
        self.fly_sound = SoundLoader.load('assets/sounds/fly.wav')
        
        try:
            img_load = ImageLoader.load('assets/dragon_sheet.png')
            
            if img_load:
                tex = img_load.texture
            else:
                tex = None
            
            if not tex:
                from kivy.core.image import Image as CoreImage
                tex = CoreImage('assets/dragon_sheet.png').texture

            if tex:
                w, h = tex.width / 4, tex.height / 4
                self.frames = []
                for r in reversed(range(4)):
                    for c in range(4):
                        if not (r == 1 and c == 0):
                            self.frames.append(tex.get_region(c * w, r * h, w, h))
        except Exception:
            pass

        self.idx = 0
        
        if self.frames:
            self.texture = self.frames[0]
            Clock.schedule_interval(self.update_dragon, 1.0 / 12.0)
        else:
            self.source = 'assets/enemy.png'
    def update_dragon(self, dt):
        app = App.get_running_app()
        if app and hasattr(app.root, 'get_screen'):
            try:
                game_screen = app.root.get_screen('game')
                if game_screen.is_paused or game_screen.game_over:
                    return
            except Exception:
                pass    
        if self.frames:
            self.idx = (self.idx + 1) % len(self.frames)
            self.texture = self.frames[self.idx]
class Shot(Image):
    ...
class EnemySpell(Image):
    ...
class Pause(MDScreen):
    def __init__(self,**kwargs):
            super().__init__(**kwargs)

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