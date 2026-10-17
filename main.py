#Імпорти
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
from kivy.properties import NumericProperty 

if platform != 'android':
    Window.size = (800,600)
    Window.top =100
    Window.left=400

#Змінні
SPELLS_FREQUANCY = 0.0055
SPELL_SPEED = dp(6)
DRAGON_SPEED = dp(7)
FIREBALL_SPEED = dp(10)
ENEMY_SPEED = dp(1.5)
FPS = 60
BG_SPEED = dp(1)
# === Клас Екрану Меню ===
class MainScreen(MDScreen):
    def go_game(self):
        self.manager.current = 'game'

# === Клас Екрану Гри ===
class GameScreen(MDScreen):
    
    wave = NumericProperty(1)
    kills = NumericProperty(0)
    #Коннструктор класу
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.eventKeys = {}
        self.fireBalls = []
        self.enemies_spells =[]
        self.enemies = []
        self.heals = []
        self.dragon_hp = 100
        self.chance = 40  
        self.game_over = False
        self.is_paused = False
        Clock.schedule_interval(self.update,1/FPS)
        Clock.schedule_interval(self.spawn_enemy,2.5)
        Clock.schedule_interval(self.start_next_wave,1/FPS)

        self.sound = None

        self.sound = SoundLoader.load('assets/sounds/bg_music.wav')
        self.fire_sound = SoundLoader.load('assets/sounds/fire_sound.wav')
        self.button_sound = SoundLoader.load("assets/sounds/ui_sound_cl.wav")
        self.comeback_sound = SoundLoader.load("assets/sounds/ui_sound_deni.wav")
        

        self.sound.volume = 0.15
    # Оновлення гри при вході
    def on_enter(self):
        if self.sound:
            self.sound.loop = True
            self.sound.play()
        self.reset_game()
        self.start_next_wave()

    #Метод ресету гри    
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
            self.wave = 1
            self.kills = 0
            for heal in self.heals[:]:
                if heal.parent:
                    heal.parent.remove_widget(heal)

            self.heals.clear()            
            lbl = self.ids.waves_label
            lbl.pos_hint={"center_x": 0.1}
            anim1 = Animation(opacity = 0.75,pos_hint={"center_x": 0.5},duration=0.8)
            anim2 = Animation(pos_hint={"center_x": 0.99},opacity=0, duration=0.8)
            anim = anim1+ anim2
            anim.start(lbl)
            

            if 'health_bar' in self.ids:
                self.ids.health_bar.value = self.dragon_hp
            if 'hp_label' in self.ids:
                self.ids.hp_label.text = str(self.dragon_hp)
            if 'game_over_label' in self.ids:
                self.ids.game_over_label.opacity = 0
            if 'pause_menu' in self.ids:
                self.ids.pause_menu.opacity = 0
                self.ids.pause_menu.disabled = True

    # Метод атаки ворогів
    def enemy_shot(self,enemy):
        enemy_spell = EnemySpell(pos= (enemy.center_x- 25,enemy.center_y + 10))
        self.enemies_spells.append(enemy_spell)
        self.ids.front.add_widget(enemy_spell)

    # Метод руху ворогів
    def move_enemy(self,dt):
        enemy = self.ids.enemy
        enemy.x = (randint(0,int(Window.width- dp(30))))

    # Метод появи ворогів
    def spawn_enemy(self,dt):
        if self.manager.current != 'game' or self.game_over == True or self.is_paused == True:
            return
        new_enemy = Enemy()
        self.enemies.append(new_enemy)

        self.ids.back.add_widget(new_enemy) 

    sound = SoundLoader.load('assets/bg_music')

    #Метод появи хілок
    def spawn_heal(self):
        print('HEAL!!!!!!!!!!!!!!!!!!!!!!')
        if self.manager.current != 'game' or self.game_over == True or self.is_paused == True:
            return
        heal = Heal()
        self.heals.append(heal)
        self.ids.back.add_widget(heal)
    #Метод руху хілок
    def move_enemy(self):
            heal = self.ids.heal
            heal.x = (randint(0,int(Window.width- dp(50))))
    
    # Методи Реалізації хвиль гри
    def start_next_wave(self, dt=0):
        global SPELLS_FREQUANCY,SPELL_SPEED,FIREBALL_SPEED,ENEMY_SPEED,BG_SPEED

        if self.kills == 10:
            if self.wave == 3:
                self.win_game()
            self.wave += 1
            self.kills = 0
            self.ids.waves_label.text = f'Wave {self.wave}'

            
            lbl = self.ids.waves_label
            lbl.pos_hint={"center_x": 0.1}

            anim1 = Animation(opacity = 0.75,pos_hint={"center_x": 0.5},duration=0.5)
            anim2 = Animation(pos_hint={"center_x": 0.99},opacity=0, duration=0.5)
            anim = anim1+ anim2
            anim.start(lbl)
        
        
        
        if self.wave == 1:
            
            SPELLS_FREQUANCY = 0.0055
            ENEMY_SPEED = dp(1)
            BG_SPEED = dp(1)
        if self.wave == 2:
            #make text anim
            
            SPELLS_FREQUANCY = 0.0075
            ENEMY_SPEED = dp(2)
            BG_SPEED = dp(2)
        if self.wave == 3:
            #make text anim
            SPELLS_FREQUANCY = 0.01
            ENEMY_SPEED = dp(2.5)
            BG_SPEED = dp(2.5)
   
    
    # Метод оновленя гри
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
            if enemy.top > 0 and random() < SPELLS_FREQUANCY: 
                self.enemy_shot(enemy)

            if enemy.y <= 0:
                self.ids.back.remove_widget(enemy)
                self.update_health(10)
                if enemy in self.enemies:
                    self.enemies.remove(enemy)
                continue

            for ball in self.fireBalls[:]:
                x_hit = abs(enemy.center_x - ball.center_x - dp(15))
                y_hit = abs(enemy.center_y - ball.center_y)
                max_allowed_distance_x = dp(65) 
                max_allowed_distance_y = dp(60)

                if x_hit <= max_allowed_distance_x and y_hit <= max_allowed_distance_y:
                    self.ids.back.remove_widget(enemy)
                    self.kills += 1

                    if enemy in self.enemies:
                        self.enemies.remove(enemy)

                    self.ids.front.remove_widget(ball)

                    if ball in self.fireBalls:
                        self.fireBalls.remove(ball)
                    if random() < (self.chance / 100):
                        self.spawn_heal()    
                    break 

        for heal in self.heals[:]:
            if heal.y <= 0:
                self.heals.remove(heal)
                heal.parent.remove_widget(heal)
            heal.y -= dp(3)
            dragon = self.ids.dragon
            
            dragon_top_y = dragon.y + dp(45)


            x_hit = abs(self.ids.dragon.center_x - heal.center_x)
            y_hit = abs(dragon_top_y - heal.center_y)

            max_allowed_distance_x = dp(65) 
            max_allowed_distance_y = dp(80)

            if x_hit <= max_allowed_distance_x and y_hit <= max_allowed_distance_y:
                self.heals.remove(heal)
                heal.parent.remove_widget(heal)

                self.heal_health()
                

            if self.ids.dragon.x < 0:
                self.ids.dragon.x = 0
            elif self.ids.dragon.right > Window.width:
                self.ids.dragon.right = Window.width

    # Метод оновлення HP
    def update_health(self, damage):
        health_bar = self.ids.health_bar
        self.dragon_hp = max(0, self.dragon_hp - damage)
        self.ids.hp_label.text = str(self.dragon_hp)
        anim = Animation(value=self.dragon_hp, duration=0.1, transition="out_quad")
        anim.stop(health_bar)
        anim.start(health_bar)
        
        if self.dragon_hp == 0:
            self.lose_game()

    def heal_health(self,):
        health_bar = self.ids.health_bar
        self.dragon_hp = min(100, self.dragon_hp + 20)
        self.ids.hp_label.text = str(self.dragon_hp)
        anim = Animation(value=self.dragon_hp, duration=0.1, transition="out_quad")
        anim.stop(health_bar)
        anim.start(health_bar)
    # Метод програшу в грі
    def win_game(self):
    
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

        self.ids.win_label.opacity = 1
        Clock.schedule_once(lambda dt: self.go_menu(), 3)

    def lose_game(self):
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


    # Метод паузи гри
    def pause(self):
        self.is_paused = True
        self.ids.pause_menu.opacity = 0.75
        self.ids.pause_menu.disabled = False
        if self.sound:
            self.sound.stop()

    # Метод продовження до гри
    def resume(self):
        self.is_paused = False
        self.ids.pause_menu.opacity = 0
        self.ids.pause_menu.disabled = True
        if self.sound:
            self.sound.play()

    # Метод руху дракона в ліво
    def moveLeft(self):
        self.ids.dragon.pos[0] -= DRAGON_SPEED

    # Метод руху дракона в право
    def moveRight(self):
        self.ids.dragon.pos[0] += DRAGON_SPEED

    # Метод атаки дракона
    def shot(self):
        self.fire_sound.play()
        shot = Shot(pos =(self.ids.dragon.center_x - 18, self.ids.dragon.center_y + 50))
        self.fireBalls.append(shot)
        self.ids.front.add_widget(shot)

    # Методи кнопок
    def pressKey(self,key):
        self.eventKeys[key] = True

    def releaseKey(self,key):
        self.eventKeys[key] = False

    # Вихід в меню
    def go_menu(self):
        self.manager.current = 'main'
        self.ids.pause_menu.opacity = 0
        self.is_paused = False
        if self.sound:
            self.sound.stop()
    def play_sound(sound):
        if sound:
            sound.play()

# Клас Ворогів
class Enemy(Image):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.size_hint = None,None
        self.size = (dp(150), dp(150))
        space = dp(20)
        min_x = int(space)
        max_x = int(Window.width - self.size[0] - space)
        self.frames = []
        self.idx = 0
        if max_x <= min_x:
            spawn_x = min_x
        else:
            spawn_x = randint(min_x, max_x)

        self.pos = (spawn_x, Window.height)
        
        try:
            img_load = ImageLoader.load('assets/images/enemy_sheet.png')
                
            if img_load:
                tex = img_load.texture
            else:
                tex = None
                
            if not tex:
                from kivy.core.image import Image as CoreImage
                tex = CoreImage('assets/images/enemy_sheet.png').texture
    
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
            self.anim_event = Clock.schedule_interval(self.update_enemy, 1.0 / 12.0)
        else:
            self.source = 'assets/images/enemy_sheet.png'
    
        # Оновлення фреймів анімації
    def update_enemy(self, dt):
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
#=== Клас Дракона ===
class Dragon(Image):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.size_hint = (None, None)
        self.size = (dp(150), dp(150))
        self.frames = []
        self.fly_sound = SoundLoader.load('assets/sounds/fly.wav')
        
        try:
            img_load = ImageLoader.load('assets/images/dragon_sheet.png')
            
            if img_load:
                tex = img_load.texture
            else:
                tex = None
            
            if not tex:
                from kivy.core.image import Image as CoreImage
                tex = CoreImage('assets/images/dragon_sheet.png').texture

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
            self.source = 'assets/images/enemy_sheet.png'

    # Оновлення фреймів анімації
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

class Heal(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.size_hint = (None, None)
        self.size = (dp(40), dp(40))
        max_x = max(0, int(Window.width - self.width))
        self.x = randint(0, max_x)
        self.y = Window.height
# Класи Атак
class Shot(Image):
    ...
class EnemySpell(Image):
    ...
# === Клас екрану паузи ===
class Pause(MDScreen):
    def __init__(self,**kwargs):
            super().__init__(**kwargs)
#=== Клас програми ===
class GameApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        self.is_paused = False
        sm = MDScreenManager()
        sm.add_widget(MainScreen(name ="main"))
        sm.add_widget(GameScreen(name ="game"))

        return sm

app = GameApp()
app.run()