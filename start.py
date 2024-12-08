################################################
# Programmeerimine I
# 2024/2025 sügissemester
#
# Projekt
# Teema: 2d mäng (platformer)
#
# Autorid: Evelina Kortel, Marta Laine
#
# mõningane eeskuju: Super Mario
#
# Lisakommentaar (nt käivitusjuhend):
# See on esimene mängu projekt, mistõttu võib koodis esineda mõningaid vigu. 
# Mängu käivitamiseks soovitame kasutada debugi režiimi, et tuvastada ja parandada võimalikud probleemid.
# Projekt ja instructioon võib leida githabis https://github.com/ev1ina/game1/tree/main
#
#
##################################################

import pygame
import os
import random
import csv
import button

# Algseadistused
pygame.init()

# Määrab ekraani suuruse
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

# Skrollimise piir
SCROLL_THRESH = 200

# Loo ekraan ja lisa pealkiri
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Rocky')

# Seadistab kaadrisageduse
clock = pygame.time.Clock()
FPS = 60

# Mängu muutujad
GRAVITY = 0.75 # Gravitatsiooni konstant
ROWS = 16 # Maailma ridade arv
COLS = 150  # Maailma veergude arv
TILE_SIZE = SCREEN_HEIGHT // ROWS  # Plaadi suurus
TILE_TYPES = 19 # Plaadi tüüpide arv
MAX_LEVELS = 3 # Maksimaalne tasemete arv
level = 0 # Alustatakse esimeselt tasemelt
srtart_game = False # Kontrollib, kas mäng on alanud


# Mängija liikumise muutujad
moving_left = False
moving_right = False
shoot = False

# Ekraani ja tausta skrollimise muutujad
screen_scroll = 0
bg_scroll = 0

# Plaatide pildid
# Loob tühi nimekiri, kuhu lisatakse plaatide pildid
img_list = []
for x in range(1,TILE_TYPES+1):
    img = pygame.image.load(f'rocky/01. Rocky Level/tiles/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)


# Nõel (dagger) pilt
# Laadib ja skaleerib nõela pildi
dagger_img = pygame.image.load('rocky/Sprites/Gino Character/PNG/dagger/1.png').convert_alpha()
dagger_img2 = pygame.transform.scale(dagger_img, (int(dagger_img.get_width() * 1.5), int(dagger_img.get_height() * 1.5)))

# Esemed (kasti pildid)
diamond_box_img = pygame.image.load('rocky/Collectible/Diamond/1.png').convert_alpha()
dag1_box_img = pygame.image.load('rocky/Collectible/Dag/1.png').convert_alpha()
dag_box_img = pygame.transform.scale(dag1_box_img, (int(dag1_box_img.get_width() * 2), int(dag1_box_img.get_height() * 2)))
heart_box_img = pygame.image.load('rocky/Collectible/Heart/1.png').convert_alpha()

# Tausta pildid
back_list = []
for x in range(1,9):
	img = pygame.image.load(f'rocky/01. Rocky Level/{x}.png').convert_alpha()
	back_list.append(img)

# Menüünupud
start_img = pygame.image.load('rocky/buttons/start_btn.png').convert_alpha()
exit_img = pygame.image.load('rocky/buttons//exit_btn.png').convert_alpha()
restart_img = pygame.image.load('rocky/buttons//restart_btn.png').convert_alpha()

# Objektide pildid (nimekirja vormingus
item_boxes ={
    "Health"    : heart_box_img,
    "Ammo"      : dag_box_img,
    "Diamond"   : diamond_box_img
}





# Värvid
BG = (0, 73, 100) # Taustavärv
RED = (255, 0, 0) 
WHITE = (1, 40, 55) # Tume sinine
GREEN = (0, 255, 0) 
BLACK = (0, 0, 0)

# Taustapildi seadistamine
background_startmenu = pygame.image.load('rocky/01. Rocky Level/backgroundgame.png').convert_alpha()
scaled_background = pygame.transform.scale(background_startmenu, (800, 640))

# Teksti stiil
font = pygame.font.SysFont('Futura', 30)

# Funktsioon teksti joonistamiseks
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Funktsioon tausta joonistamiseks
def draw_bg():
    """Joonistab liikuva tausta."""
    screen.fill(GREEN)
    width = back_list[1].get_width()
    for x in range(4):
        screen.blit(back_list[0], ((x * width) - bg_scroll * 0.5, 0))
        for i in range(1, len(back_list)):
            screen.blit(back_list[i], ((x * width) - bg_scroll * (0.5 + i * 0.1), SCREEN_HEIGHT - back_list[i].get_height() + 100))

# Funktsioon taseme taastamiseks
def reset_level():
    """Lähtestab mängumaailma taseme."""
    enemy_group.empty()
    dagger_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    cristall_group.empty()
    exit_group.empty()

    """ Puhas tile list"""
    data = []
    for r in range(ROWS):
        r= [-1] * COLS
        data.append(r)

    return data


# Mängija klass (peategelane)
class Main_character(pygame.sprite.Sprite):
    """Mängija klass, mis hõlmab kõiki peategelase omadusi ja tegevusi."""
    def __init__(self, char_type, x, y, scale, speed, ammo):
        pygame.sprite.Sprite.__init__(self)
        # Mängija omadused
        self.alive = True # Kontrollib, kas mängija on elus
        self.char_type = char_type # Tegelase tüüp
        self.speed = speed # Liikumise kiirus
        self.ammo = ammo # Algne laskemoon
        self.diamondes = 0 # Kogutud teemantide arv
        self.start_ammo = ammo # Algne laskemoon varuks
        self.shoot_cooldown = 0 # Aeg, mis peab mööduma enne järgmist lasku
        self.health = 100 # Mängija algne tervisepunktide arv
        self.max_health =self.health # Mängija maksimaalne tervis
        self.direction = 1 # Suund (1 - paremale, -1 - vasakule)
        self.vel_y = 0 # Vertikaalne kiirus (hüpped ja kukkumine)
        self.jump = False # Kas mängija hüppab
        self.is_throwing = False # Kas mängija sooritab rünnaku
        self.in_air = True # Kas mängija on õhus
        self.flip = False # Pööramine vasakule/paremale
        self.is_hit = False # Kas mängija saab kahju
        self.animation_list = [] # Animatsioonide loend
        self.frame_index = 0 # Praeguse animatsiooni kaadri indeks
        self.action = 0 # Praegune tegevus (nt 0 - Idle, 1 - Run jne)
        self.update_time = pygame.time.get_ticks() # Aeg animatsiooni uuendamiseks
        self.damage_cooldown = 1000  # Kahjustuste ajavahemik (ms)
        self.last_damage_time = pygame.time.get_ticks()  # Viimase kahju saamise aeg

        # Laadime mängija animatsioonid
        animation_types = ['Idle','Run','Jump', 'Throw attack', 'Death', 'Hit']
        for animation in animation_types:
            temp_list = []
            num_of_frames =  len(os.listdir(f'rocky/Sprites/{self.char_type}/PNG/{animation}/small'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'rocky/Sprites/{self.char_type}/PNG/{animation}/small/{i+1}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                #img_mask = pygame.mask.from_surface(img)
                #mask_image = img_mask.to_surface()
                temp_list.append(img)
            self.animation_list.append(temp_list)
        
        # Määrame mängija algse pildi ja positsiooni
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y) 
        self.width = self.image.get_width()
        self.height = self.image.get_height()


    def update(self):
        """Uuendame animatsiooni ja kontrollime, kas mängija on elus"""
        self.update_animation()
        self.check_alive()

         # Uuendame laske cooldown'i
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # Sooritame viske "Throw attack" animatsiooni keskel
        if self.action == 3: # Kontrollime, kas tegevus on "Throw attack"
            if self.frame_index == len(self.animation_list[3]) // 2 and self.shoot_cooldown == 0 and self.ammo > 0:
                self.shoot() # Käivitame viske
            elif self.frame_index == len(self.animation_list[3]) - 1:
                self.is_throwing = False
                self.update_action(0)  # Naaseme Idle olekusse

       # Kontrollime kokkupõrkeid vaenlastega
        if self.alive:
            for enemy in enemy_group:
                if enemy.alive and self.rect.colliderect(enemy.rect): # Kokkupõrge vaenlasega
                    self.take_damage(10)
                    break

        # Määrame mängija positsiooni vastavalt suunale
        if self.direction == 1:  # Paremale
            self.rect.topleft = (self.rect.x, self.rect.y)
        else:  # Vasakule
            self.rect.topleft = (self.rect.x , self.rect.y)  # Adjust the x-value for left-facing


    def take_damage(self, damage):
        current_time = pygame.time.get_ticks()
        # Kontrollime, kas piisavalt aega on möödunud, et kahju võtta
        if current_time - self.last_damage_time > self.damage_cooldown:
            self.health -= damage
            self.last_damage_time = current_time  # Uuendame viimast kahju aega
            self.is_hit = True  # Märgime, et tegelane võtab kahju
            # Kui tervis on suurem kui 0, alustame "Hit" animatsiooni
            if self.is_hit:
                self.update_action(5)  # 5 - "Hit" animatsioon



    def move(self, moving_left, moving_right):
        # Lähtestame liikumise muutujad
        screen_scroll = 0
        dx = 0
        dy = 0

        # Kontrollime, kas mängija liigub vasakule või paremale
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1

        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # Kontrollime hüpet
        if self.jump == True and self.in_air == False:
            self.vel_y = -16 # Hüppe kiirus
            self.jump = False
            self.in_air = True

        # Rakendame gravitatsiooni
        self.vel_y += GRAVITY
        if self.vel_y > 10: # Piirame maksimaalse langemiskiiruse
            self.vel_y = 10
        dy += self.vel_y 

        # Kontrollime kokkupõrkeid takistustega
        for tile in world.obstavle_list:
            # Kontrollime horisontaalset kokkupõrget
            if tile [1].colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                dx = 0
            # Kontrollime vertikaalset kokkupõrget
            if tile [1].colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                #kas on põrand, i.e hüppame
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy =  tile[1].bottom - self.rect.top
                    # Kui mängija langeb
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy =  tile[1].top - self.rect.bottom


         # Kontrollime kokkupõrget kristallidega
        if pygame.sprite.spritecollide(self, cristall_group, False):
            self.take_damage(10)


       # Kontrollime taseme lõppu
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False) and player.diamondes >= 3:
            level_complete = True

        # Kas mängija kukkus kaardilt välja
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0


        # Takistame mängijal ekraanilt välja liikuda
        if self.rect.left +dx <0 or self.rect.right +dx > SCREEN_WIDTH:
                dx = 0

        # Uuendame mängija positsiooni
        self.rect.x += dx
        self.rect.y += dy


         # Uuendame kaamera liikumist
        if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
            or self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx):
            self.rect.x -= dx
            screen_scroll =  -dx

        return screen_scroll, level_complete


        


    def shoot(self):
        # Kontrollime, kas lask on võimalik
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 15 # Laskude vaheline aeg
            dagger = Dagger(self.rect.centerx + (0.1 *self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            dagger_group.add(dagger) # Lisame noa gruppi
            self.ammo -= 1





        

    def update_animation(self):
        ANIMATION_COOLDOWN = 100  # Animatsiooni kiirus

        # Kontrollime, et kaadri indeks ei läheks üle animatsioonide arvu
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = len(self.animation_list[self.action]) - 1

        # Määrame praeguse animatsiooni kaadri
        self.image = self.animation_list[self.action][self.frame_index]

        # Kontrollime, kas piisavalt aega on möödunud
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

           # Kui "Hit" animatsioon on lõppenud, naaseme "Idle" animatsioonile
            if self.action == 5 and self.frame_index >= len(self.animation_list[5]):
                self.update_action(0)  # 0 - "Idle" animatsioon
                self.is_hit = False   # Lõpetame kahju oleku

            # Kui "Death" animatsioon on lõppenud, peatame animatsiooni viimasele kaadrile
            elif self.action == 4 and self.frame_index >= len(self.animation_list[4]) - 1:
                self.frame_index = len(self.animation_list[4]) - 1  # Peatame viimasele kaadrile

            # Ülejäänud tegevused, nagu Run või Idle, jätkuvad loopitult
            elif self.frame_index >= len(self.animation_list[self.action]):
                self.frame_index = 0  # Taaskäivita animatsioon

                

    def update_action(self, new_action):
         # Kontrollime, kas uus tegevus erineb praegusest
        if new_action != self.action:
            self.action = new_action
            # Uendame animatsiooni seadistused
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        # Kontrollime, kas mängija tervis on otsas
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(4)  # Käivitame "Death" animatsiooni



    def draw(self):
          # Joonistame mängija ekraanile ja pöörame vastavalt suunale
         screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        # Draw the collision rectangle for debugging
        # pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)  # Red outline for collision rect


                  



class Enemy02(pygame.sprite.Sprite):
    """Vaenlase klass, mis kirjeldab liikumist, animatsioone ja AI käitumist."""
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.char_type = char_type
        self.in_air = True
        self.vel_y = 0
        self.direction = 1
        self.speed = speed
        self.attack_speed = speed
        self.alive = True
        self.health = 100
        self.is_hit = False  # Kontrollib, kas vaenlane on tabamuse saanud
        self.action = 0  # 0 - Idle, 1 - Run, 2 - Attack, 3 - Hit, 4 - Death
        self.frame_index = 0
        self.flip = False
        self.animation_list = []
        self.update_time = pygame.time.get_ticks()
        self.move_counter = 0
        self.idling = False
        self.idle_counter = 0
        self.vision = pygame.Rect(0, 0, 70, 20) # Nägemise ala (ristkülik)
                
        # Laadime kõik vaenlase animatsioonid
        animation_types = ['Idle', 'Run', 'Attack', 'Hit', 'Death']
        for animation in animation_types:
            temp_list = []
            folder_path = f'rocky/Sprites/{self.char_type}/PNG/{animation}'
            if os.path.exists(folder_path):
                num_of_frames = len(os.listdir(folder_path))
                for i in range(num_of_frames):
                    img = pygame.image.load(f'{folder_path}/{i+1}.png').convert_alpha()
                    img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                    temp_list.append(img)
            self.animation_list.append(temp_list)

        # Määrame algse pildi ja positsiooni
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        """Uuendab animatsioone ja kontrollib, kas vaenlane on elus."""
        self.update_animation()
        self.check_alive()


    def move(self, moving_left, moving_right):
        """Kontrollib vaenlase liikumist."""
        dx = 0
        dy = 0

        # Kui liigub vasakule või paremale
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1

        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # Rakendame gravitatsiooni
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # Kontrollime kokkupõrkeid objektidega
        for tile in world.obstavle_list:
            # X-suunaline kokkupõrge
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                dx = 0
            # Y-suunaline kokkupõrge
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                if self.vel_y < 0:  # Kui hüppab
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:  # Kui kukub
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        
    
        # Uuenda vaenlase positsiooni
        self.rect.x += dx
        self.rect.y += dy
        




    def ai(self):
        """Vaenlase tehisintellekti (AI) loogika."""
        if self.alive and player.alive:
            if not self.idling and random.randint(1, 200) == 1:
                self.update_action(0)  # Idle
                self.idling = True
                self.idle_counter = 50

            self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
            if self.vision.colliderect(player.rect):
                self.update_action(2)  # Attack

                # liigub kiirem kui mängijat näeb
                if abs(player.rect.centerx - self.rect.centerx) > 10:
                    if player.rect.centerx < self.rect.centerx:
                        self.move(True, False)
                    elif player.rect.centerx > self.rect.centerx:
                        self.move(False, True)
                # tagasi tava kiirusele
                self.attack_speed = self.speed
                self.is_hit = False


                if pygame.time.get_ticks() - self.update_time > 1000:  # Cooldown for attack
                    self.update_action(0)  # Tagasi Idle

        

            if not self.idling: # Kui vaenlane liigub
                if self.direction == 1:
                    ai_moving_right = True
                else:
                    ai_moving_right = False
                ai_moving_left = not ai_moving_right
                self.move(ai_moving_left, ai_moving_right)
                self.move_counter += 1

                if self.move_counter > TILE_SIZE * 2: # Muuda suunda
                    self.direction *= -1
                    self.move_counter *= -1
            else:
                self.idle_counter -= 1
                if self.idle_counter <= 0:
                    self.idling = False

            self.rect.x += screen_scroll


    def update_animation(self):
        """Uuendab vaenlase animatsioone vastavalt tegevusele."""
        ANIMATION_COOLDOWN = 100
        if len(self.animation_list[self.action]) > 0:
            self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

            if self.action == 3 and self.frame_index >= len(self.animation_list[3]) - 1:
                self.is_hit = False
                if self.health > 0:
                    self.update_action(0)  # tagasi Idle pärast Hit
                else:
                    self.update_action(4)   # Käivita surma animatsioon

            elif self.action == 4 and self.frame_index >= len(self.animation_list[4]) - 1:
                self.kill() # Eemalda sprite mängust
            elif self.frame_index >= len(self.animation_list[self.action]):
                self.frame_index = 0 # Taaskäivita animatsioon

    def take_damage(self, damage):
        """Rakendab vaenlasele kahju ja uuendab olekut."""
        if self.alive and not self.is_hit:
            self.health -= damage
            self.is_hit = True
            self.update_action(3)  # "Hit" animatsioon
        if self.health <= 0:
            self.alive = False
            self.update_action(4)  # "Death"


    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
    

    def check_alive(self):
        """Kontrollib, kas vaenlane on elus."""
        if self.health <= 0 and self.alive:
            self.alive = False
            self.update_action(4)  # "Death" 

    def draw(self):
        """Joonistab vaenlase ekraanile."""
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        #pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)  # vaenlase rectangle
        #pygame.draw.rect(screen, RED, self.vision, 1)  # Nägemisala




class World():
    """Mängumaailma klass, mis haldab taseme andmeid ja elemente."""
    def __init__(self):
        """Initsialiseerib maailma takistuste loendi."""
        self.obstavle_list = []

    def process_data(self, data):
        """
        Töötleb taseme andmeid ja loob vastavad elemendid.
        :param data: Kahemõõtmeline massiiv taseme andmetega.
        :return: Vaenlane, mängija ja terviseindikaator.
        """
        self.level_length = len(data[0])

        # Läbib läbi kõik andmed ja määrab objektid
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0: # Kontrollime, kas plaat on kehtiv
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                     # Lisame takistuse
                    if tile >= 0 and tile <=5 or tile == 18:
                        self.obstavle_list.append(tile_data)
                    elif tile >=6 and tile <=9:
                        cristall = Cristall(img, x * TILE_SIZE, y * TILE_SIZE)
                        cristall_group.add(cristall) #kristallid
                    elif tile == 10:# Dekoratsioonid
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 14:  # Loome mängija
                        player = Main_character('Gino Character', x * TILE_SIZE, y * TILE_SIZE, 1.6, 7, 10)
                        health_bar = HeathBar(10, 10, player.health, player.health)
                    elif tile == 15: # Loome vaenlase
                        enemy = Enemy02('Enemy02', x * TILE_SIZE, y * TILE_SIZE, 1.6, 3)
                        enemy_group.add(enemy)
                    elif tile == 12: # Lisame laskemoonakasti
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 13: #tervisekasti
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 11: # teemantikasti
                        item_box = ItemBox('Diamond', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile >=16 and tile <=17:
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit) # Väljapääsu
                

        return enemy, player, health_bar
    

        
    def draw(self):
        """Joonistab kõik takistused ekraanile."""
        for tile in self.obstavle_list:
            tile[1][0]  += screen_scroll
            screen.blit(tile[0], tile[1])



    
class Decoration(pygame.sprite.Sprite):
    """Klass dekoratsiooni loomiseks."""
    def __init__(self, img,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x +TILE_SIZE //2, y+ (TILE_SIZE - self.image.get_height()))


    def update(self):
        """Uuendab dekoratsiooni positsiooni ekraanil."""
        self.rect.x += screen_scroll

class Cristall(pygame.sprite.Sprite):
    """Klass kristalli loomiseks."""
    def __init__(self, img,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x +TILE_SIZE //2, y+ (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Exit(pygame.sprite.Sprite):
    """Klass väljapääsu loomiseks."""
    def __init__(self, img,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x +TILE_SIZE //2, y+ (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
    """Klass erinevate esemekastide loomiseks."""
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        """Uuendab esemekasti positsiooni ja kontrollib, kas mängija on selle kasti võtnud."""
        #scroll
        self.rect.x += screen_scroll
        # Kontrollime, kas mängija korjas kasti üles
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == 'Health':
                player.health += 25
            if player.health > player.max_health:
                player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 5
            elif self.item_type == 'Diamond':
                player.diamondes += 1
            # Eemaldame kasti mängust
            self.kill()

class HeathBar():
    """Terviseindikaatori klass, mis näitab mängija praegust ja maksimaalset tervist."""

    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y+80
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        """
        Joonistab terviseindikaatori ekraanile.
        :param health: Mängija praegune tervis.
        """
        self.health = health
        # Arvutab tervise suhte
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24)) # Raam
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20)) # Taust
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20)) # Täidetud osa

         
class Dagger(pygame.sprite.Sprite):
    """Nuga, mida mängija saab visata."""
    def __init__(self, x, y, direction):
        """
        Initsialiseerib noole omadused.
        :param x: Algne X-koordinaat.
        :param y: Algne Y-koordinaat.
        :param direction: Suund, kuhu nool liigub (1 - paremale, -1 - vasakule).
        """
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10 # Liikumise kiirus
        self.image = dagger_img2
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        """Uuendab noole positsiooni ja eemaldab selle, kui see läheb ekraanilt välja."""
        self.rect.x += (self.direction * self.speed) + screen_scroll # Liigutab noolt
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH - 100: # Kontrollib, kas nool on ekraanilt väljas
            self.kill()


# Nuppude loomine
start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT// 2 -130, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT// 2 +50, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT// 2 -50, restart_img, 2)


# Sprite-gruppide loomine
dagger_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
cristall_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()




# Taseme andmete ettevalmistamine
world_data = []
for row in range(ROWS):
    r= [-1] * COLS
    world_data.append(r)
    
# Taseme andmete laadimine
with open(f'levelid/level{level}_data.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for x, row in enumerate(reader):
            for y, tile in enumerate(row):
                world_data[x][y] = int(tile)


# Mängumaailma ja objektide loomine
world = World()
enemy, player, health_bar = world.process_data(world_data)




# Mängu põhitsükkel
run = True
while run:

    clock.tick(FPS) # Juhib kaadrite kiirust

    if srtart_game == False:
        # Menüükraan
        #screen.fill(BG)
        screen.blit(scaled_background, (0, 0))
        # Nuppud
        if start_button.draw(screen):
            srtart_game = True
        if exit_button.draw(screen):
            run = False
    else:
        # Taust ja maailm
        draw_bg()
        world.draw()



        # Näitab mis level
        draw_text(f'LEVEL: {level} ',font, WHITE, 10, 10)

        # Näitab teemantide arvu
        draw_text('DIAMONDES: ',font, WHITE, 10, 35)
        for x in range(player.diamondes):
            screen.blit(diamond_box_img, (160 + (x * 25), 37 ))
       
        # Näitab tervist
        health_bar.draw(player.health)
        #draw_text('HEALTH: ',font, WHITE, 10, 60)
        #for x in range(player.health):
            #screen.blit(heart_box_img, (115 + (x * 15), 62))
        
        # Näitab laskemoona
        draw_text('AMMO: ',font, WHITE, 10, 65)
        for x in range(player.ammo):
            screen.blit(dag1_box_img, (100 + (x * 7), 67))

        # Uuendused ja joonistused
        player.update()
        player.draw()


        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

            
        for dagger in dagger_group:
            for enemy in enemy_group:
                if pygame.sprite.collide_rect(dagger, enemy) and enemy.alive:
                    enemy.take_damage(25)
                    dagger.kill()

        
        
         # Sprite-gruppide uuendamine ja joonistamine
        item_box_group.update()
        dagger_group.update()
        decoration_group.update()
        cristall_group.update()
        exit_group.update()

    
        item_box_group.draw(screen)
        dagger_group.draw(screen)
        decoration_group.draw(screen)
        cristall_group.draw(screen)
        exit_group.draw(screen)



        ## Mängija tegevuste uuendamine
        if player.alive:
            if player.is_throwing:
                player.update_action(3)  # 3 - "Throw attack"
            elif shoot:
                player.is_throwing = True
            elif player.is_hit:
                player.update_action(5)
            elif player.in_air:
                player.update_action(2)# 2 - hüppemine
            elif moving_left or moving_right:
                player.update_action(1) # 1 on jooksemine
            else:
                player.update_action(0) #0 - idle

            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            # Kontrollib, kas tase on lõpetatud
            if level_complete:
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    with open(f'levelid/level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)


                    world = World()
                    enemy, player, health_bar = world.process_data(world_data)



        else: #Taaskäivitamise jaoks
            screen_scroll = 0
            if restart_button.draw(screen):
                bg_scroll = 0
                world_data = reset_level()
                with open(f'levelid/level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)


                world = World()
                enemy, player, health_bar = world.process_data(world_data)



    for event in pygame.event.get():
        # Väljumine mängust
        if event.type == pygame.QUIT:
            run = False
        # Klahvivajutused
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
            if event.key == pygame.K_ESCAPE:
                run = False

        # Klahvide vabastamine
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False

    pygame.display.update()


pygame.quit()