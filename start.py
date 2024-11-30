################################################
# Programmeerimine I
# 2024/2025 sügissemester
#
# Projekt
# Teema: 2d mäng
#
#
# Autorid: Evelina Kortel, Marta Laine
#
# mõningane eeskuju: Super Mario
#
# Lisakommentaar (nt käivitusjuhend): kui see on algversioon mõned vead koodis on, käivitada on vaja debugiga
# See on projekti algversioon, mistõttu võib koodis esineda mõningaid vigu. 
# Mängu käivitamiseks soovitame kasutada debugi režiimi, et tuvastada ja parandada võimalikud probleemid.
#
#
##################################################

import pygame
import os
import random
import csv


pygame.init()


SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

SCROLL_THRESH = 200


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Rocky')

#seadistab kaadrisagedus
clock = pygame.time.Clock()
FPS = 60

#määrab mängu muutujad
GRAVITY = 0.75
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 16
level = 0


#defineerib mängija tegevusmuutujad
moving_left = False
moving_right = False
shoot = False

screen_scroll = 0
bg_scroll = 0

#pildid 

#store tiles in a list
img_list = []
for x in range(1,TILE_TYPES+1):
    img = pygame.image.load(f'rocky/01. Rocky Level/tiles/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)


dagger_img = pygame.image.load('rocky/Sprites/Gino Character/PNG/dagger/1.png').convert_alpha()
dagger_img2 = pygame.transform.scale(dagger_img, (int(dagger_img.get_width() * 2), int(dagger_img.get_height() * 2)))

#pick up boxes
diamond_box_img = pygame.image.load('rocky/Collectible/Diamond/1.png').convert_alpha()
dag1_box_img = pygame.image.load('rocky/Collectible/Dag/1.png').convert_alpha()
dag_box_img = pygame.transform.scale(dag1_box_img, (int(dag1_box_img.get_width() * 2), int(dag1_box_img.get_height() * 2)))
heart_box_img = pygame.image.load('rocky/Collectible/Heart/1.png').convert_alpha()

#cristall_img = pygame.image.load('frocky/01. Rocky Level/tiles/6.png').convert_alpha()
back_list = []
for x in range(1,9):
	img = pygame.image.load(f'rocky/01. Rocky Level/{x}.png').convert_alpha()
	back_list.append(img)



item_boxes ={
    "Health"    : heart_box_img,
    "Ammo"      : dag_box_img,
    "Diamond"   : diamond_box_img
}





#värvid
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

#tekst ащте
font = pygame.font.SysFont('Futura', 30)

def draw_text(text, foont, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
    screen.fill(GREEN)
    width = back_list[1].get_width()
    for x in range(4):
        screen.blit(back_list[0], ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(back_list[1], ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - back_list[1].get_height()+100))
        screen.blit(back_list[2], ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - back_list[2].get_height()+100))
        screen.blit(back_list[3], ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - back_list[3].get_height()+100))
        screen.blit(back_list[4], ((x * width) - bg_scroll * 0.9, SCREEN_HEIGHT - back_list[4].get_height()+100))
        screen.blit(back_list[5], ((x * width) - bg_scroll * 1, SCREEN_HEIGHT - back_list[5].get_height()+100))
        screen.blit(back_list[6], ((x * width) - bg_scroll * 1.1, SCREEN_HEIGHT - back_list[6].get_height()+100))
        screen.blit(back_list[7], ((x * width) - bg_scroll * 1.2, SCREEN_HEIGHT - back_list[7].get_height()+100))



#level disain




class Main_character(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.diamondes = 0
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.health = 100
        self.max_health =self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.is_throwing = False
        self.in_air = True
        self.flip = False
        self.is_hit = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.damage_cooldown = 1000  # 1 sekund (1000 ms) vahe kokkupõrke kahju vahel
        self.last_damage_time = pygame.time.get_ticks()  # algne viide ajale

        #load all images for the player
        animation_types = ['Idle','Run','Jump', 'Throw attack', 'Death', 'Hit']
        for animation in animation_types:
            #reset temporary list of img
            temp_list = []
            #count numbers of files in the folder
            num_of_frames =  len(os.listdir(f'rocky/Sprites/{self.char_type}/PNG/{animation}/small'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'rocky/Sprites/{self.char_type}/PNG/{animation}/small/{i+1}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                #img_mask = pygame.mask.from_surface(img)
                #mask_image = img_mask.to_surface()
                temp_list.append(img)
            self.animation_list.append(temp_list)
        
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)


        #self.collision_rect = pygame.Rect(
                #self.rect.x +10 , self.rect.y +30,  # Adjust the position (inset)
                #self.rect.width - 60, self.rect.height -35 # Adjust the size
            
        
        self.width = self.image.get_width()
        self.height = self.image.get_height()


    def update(self):
        self.update_animation()
        self.check_alive()

        #self.rect.topleft = (self.rect.x , self.rect.y)

        # update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

         # Выполняем бросок в середине анимации "Throw attack"
        if self.action == 3:
            if self.frame_index == len(self.animation_list[3]) // 2 and self.shoot_cooldown == 0 and self.ammo > 0:
                self.shoot()
            elif self.frame_index == len(self.animation_list[3]) - 1:
                self.is_throwing = False
                self.update_action(0)  # Возвращаемся к idle

        #check collision with characters потом закинь на enemies
        
        if self.alive and enemy.alive and self.rect.colliderect(enemy.rect):
            self.take_damage(10)

        if self.direction == 1:  # Facing right
            self.rect.topleft = (self.rect.x, self.rect.y)
        else:  # Facing left
            self.rect.topleft = (self.rect.x , self.rect.y)  # Adjust the x-value for left-facing






    def move(self, moving_left, moving_right):
        #reset movement variables
        screen_scroll = 0
        dx = 0
        dy = 0

        #assign movement variable if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1

        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        #jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -15
            self.jump = False
            self.in_air = True

        #apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y #for jump

        # check collision 
        for tile in world.obstavle_list:
            #check collision in the x direction
            if tile [1].colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                dx = 0
            #check collision in the y direction
            if tile [1].colliderect(self.rect.x + dy, self.rect.y, self.rect.width, self.rect.height):
                #check if below the ground, i.e jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy =  tile[1].bottom - self.rect.top
                    #check if above the ground, ie falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy =  tile[1].top - self.rect.bottom


        if self.rect.left +dx <0 or self.rect.right +dx > SCREEN_WIDTH:
                dx = 0

        #update rectangle position
        self.rect.x += dx
        self.rect.y += dy


        #update scroll
        if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
            or self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx):
            self.rect.x -= dx
            screen_scroll =  -dx

        return screen_scroll


        


    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20

            dagger = Dagger(self.rect.centerx + (0.1 * self.rect.size[0] * self.direction), self.rect.centery +20, self.direction)
            dagger_group.add(dagger)
            self.ammo -= 1

    def get_diamondes(self):
        pass

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



        

    def update_animation(self):
        ANIMATION_COOLDOWN = 100  # animatsiooni kiirus

        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = len(self.animation_list[self.action]) - 1

        self.image = self.animation_list[self.action][self.frame_index]

        # Kontrollime, kas piisavalt aega on möödunud
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

            # Kui "Hit" animatsioon on lõppenud, läheme tagasi "Idle" animatsioonile
            if self.action == 5 and self.frame_index >= len(self.animation_list[5]):
                self.update_action(0)  # 0 - "Idle" animatsioon
                self.is_hit = False  # Lõpetame kahju võtmise oleku

            # Kui tegevus on "Death" ja oleme jõudnud viimase kaadrini, peatame animatsiooni
            elif self.action == 4 and self.frame_index >= len(self.animation_list[4]) - 1:
                self.frame_index = len(self.animation_list[4]) - 1  # Peatume viimase kaadri juures

            # Ülejäänud tegevused, nagu Run või Idle, jätkuvad loopitult
            elif self.frame_index >= len(self.animation_list[self.action]):
                self.frame_index = 0  # Taaskäivita animatsioon

                

    def update_action(self, new_action):
        #check if the new aktion is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(4)



    def draw(self):
         screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        # Draw the collision rectangle for debugging
         pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)  # Red outline for collision rect


                  



class Enemy02(pygame.sprite.Sprite):
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
        self.is_hit = False  # Флаг удара
        self.action = 0  # 0 - Idle, 1 - Run, 2 - Attack, 3 - Hit, 4 - Death
        self.frame_index = 0
        self.flip = False
        self.animation_list = []
        self.update_time = pygame.time.get_ticks()
        self.move_counter = 0
        self.idling = False
        self.idle_counter = 0
        self.vision = pygame.Rect(0, 0, 70, 20)        
        # Загружаем анимации
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

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        #self.collision_rect = pygame.Rect(
                #self.rect.x +10 , self.rect.y +10,  # Adjust the position (inset)
                #self.rect.width - 10, self.rect.height -10 # Adjust the size
            #)

        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()

        #self.rect.topleft = (self.rect.x, self.rect.y)





    def move(self, moving_left, moving_right):
        #reset movement variables
        dx = 0
        dy = 0

        #assign movement variable if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1

        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

         # apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y  # Apply gravity to dy

        # check collision 
        for tile in world.obstavle_list:
            #check collision in the x direction
            if tile [1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            #check collision in the y direction
            if tile [1].colliderect(self.rect.x + dy, self.rect.y, self.rect.width, self.height):
                #check if below the ground, i.e jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy =  tile[1].bottom - self.rect.top
                    #check if above the ground, ie falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy =  tile[1].top - self.rect.bottom

        #update rectangle position
        self.rect.x += dx
        self.rect.y += dy


    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0) #idle
                self.idling = True
                self.idle_counter = 50

            #chek if near
            if self.vision.colliderect(player.rect):
                #attack
                self.update_action(2)
                self.attack_speed = self.speed * 1.2



                if player.rect.centerx - self.rect.centerx > 10 or player.rect.centerx - self.rect.centerx < 10:
                    if player.rect.centerx < self.rect.centerx:
                        self.move(True, False)
                    elif player.rect.centerx > self.rect.centerx:
                        self.move(False, True)

                 # Reset speed after the attack
                self.attack_speed = self.speed


            if self.idling == False:
                if self.direction == 1:
                    ai_moving_right = True
                else:
                    ai_moving_right = False
                ai_moving_left = not ai_moving_right
                self.move(ai_moving_left, ai_moving_right)
                #self.update_action(1)
                self.move_counter += 1

                #update vision
                self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
                #pygame.draw.rect(screen, RED, self.vision)

                if self.move_counter > TILE_SIZE*3:
                    self.direction *= -1
                    self.move_counter *= -1

            else:
                self.idle_counter -= 1
                if self.idle_counter <= 0:
                    self.idling = False
            
            if self.direction == 1:  # Moving right
                front_x = self.rect.right + self.speed
            else:  # Moving left
                front_x = self.rect.left - self.speed

            front_tile_x = front_x // TILE_SIZE
            front_tile_y = (self.rect.bottom + 1) // TILE_SIZE  # 1 pixel below the enemy
            if 0 <= front_tile_x < COLS and 0 <= front_tile_y < ROWS:
                ground_beneath = world_data[front_tile_y][front_tile_x] >= 0
            else:
                ground_beneath = False

            if not ground_beneath:
                self.direction *= -1
                self.move_counter = 0  # Reset move counter
                    

            


        self.rect.x += screen_scroll





    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        # Проверяем, что текущая анимация не пустая
        if len(self.animation_list[self.action]) > 0:
            # Проверяем, что текущий индекс в допустимом диапазоне
            if self.frame_index < len(self.animation_list[self.action]):
                self.image = self.animation_list[self.action][self.frame_index]

        # Обновляем кадры с задержкой
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

            # Если враг умирает и анимация достигла последнего кадра
            if self.action == 4 and self.frame_index >= len(self.animation_list[4]):
                self.kill()  # Удаляем врага из всех групп спрайтов
            elif self.action == 3 and self.frame_index >= len(self.animation_list[3]):
                # После завершения анимации "Hit" возвращаемся к "Idle"
                self.update_action(0)  # Возвращаемся к Idle
                self.is_hit = False
            elif self.frame_index >= len(self.animation_list[self.action]):
                self.frame_index = 0



    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def take_damage(self, damage):
        if self.alive and not self.is_hit:
            self.health -= damage
            self.is_hit = True
            self.update_action(3)  # Устанавливаем состояние "Hit"
        if self.health <= 0:
            self.alive = False
            self.update_action(4)  # Устанавливаем состояние "Death"

        if self.health <= 0:
            self.alive = False
            self.update_action(4)  # Устанавливаем состояние "Death"


    def check_alive(self):
        if self.health <= 0 and self.alive:
            self.alive = False
            self.update_action(4)  # Устанавливаем "Death" только один раз

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)  # Red outline for collision rect
        pygame.draw.rect(screen, RED, self.vision, 1)  # Red outline for collision rect




class World():
    def __init__(self):
        self.obstavle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        # iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <=4:
                        self.obstavle_list.append(tile_data)
                    elif tile >=5 and tile <=8:
                        cristall = Cristall(img, x * TILE_SIZE, y * TILE_SIZE)
                        cristall_group.add(cristall) #cristall
                    elif tile >= 9 and tile <= 9:#decor
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 13:  # Создание игрока
                        player = Main_character('Gino Character', x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20)
                        health_bar = HeathBar(10, 10, player.health, player.health)
                    elif tile == 14: #create enemies
                        enemy = Enemy02('Enemy02', x * TILE_SIZE, y * TILE_SIZE, 1.65, 3)
                        enemy_group.add(enemy)
                    elif tile == 12: #create ammo box
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 11: #create healt box
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 10: #create diamond box
                        item_box = ItemBox('Diamond', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 15:
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit) #exit
                        exit = Cristall(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)

        return enemy, player, health_bar
    

        
    def draw(self):
        for tile in self.obstavle_list:
            tile[1][0]  += screen_scroll
            screen.blit(tile[0], tile[1])


class Cristall(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img  # Устанавливаем изображение
        self.rect = self.image.get_rect()  # Получаем прямоугольник для изображения
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))



class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img 
        self.rect = self.image.get_rect()  
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img  
        self.rect = self.image.get_rect()  
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    
class Decorations(pygame.sprite.Sprite):
    def __init__(self, img,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x +TILE_SIZE //2, y+ (TILE_SIZE - self.image.get_height()))


    def update(self):
        self.rect.x += screen_scroll

class Cristall(pygame.sprite.Sprite):
    def __init__(self, img,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x +TILE_SIZE //2, y+ (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Exit(pygame.sprite.Sprite):
    def __init__(self, img,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x +TILE_SIZE //2, y+ (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        #scroll
        self.rect.x += screen_scroll
        #check if the player has picked up the box
        if pygame.sprite.collide_rect(self, player):
            # check what kind of box it was
            if self.item_type == 'Health':
                player.health += 25
            if player.health > player.max_health:
                player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Diamond':
                player.diamondes += 3
            #delete the item box
            self.kill()

class HeathBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = self.health = health
        self.max_health = max_health

    def draw(self, health):
        #update wirh new health
        self.health = health
        #calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

         
class Dagger(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = dagger_img2
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        #move dagger
        self.rect.x += (self.direction * self.speed) + screen_scroll
        #check if dagger has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH - 100:
            self.kill()





#create sprite groups
dagger_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
cristall_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()



#player = Main_character('Gino Character', 1 * TILE_SIZE, 1 * TILE_SIZE, 1.65, 5, 20)
#health_bar = HeathBar(10, 10, player.health, player.health)
#enemy = Enemy02('Enemy02', 5 * TILE_SIZE, 5 * TILE_SIZE, 1.65, 2)
#enemy_group.add(enemy)





#create empty tile list
world_data = []
for row in range(ROWS):
    r= [-1] * COLS
    world_data.append(r)
    
#load in level data and create word
with open('level0_data.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for x, row in enumerate(reader):
            for y, tile in enumerate(row):
                world_data[x][y] = int(tile)


world = World()
enemy, player, health_bar = world.process_data(world_data)






run = True
while run:

    clock.tick(FPS)

    #update bacground
    draw_bg()
    #draw world map
    world.draw()



    #show diamondes
    draw_text('DIAMONDES: ',font, WHITE, 10, 35)
    for x in range(player.diamondes):
        screen.blit(diamond_box_img, (160 + (x * 25), 37 ))
    #show health
    health_bar.draw(player.health)
    #draw_text('HEALTH: ',font, WHITE, 10, 60)
    #for x in range(player.health):
        #screen.blit(heart_box_img, (115 + (x * 15), 62))
    #show ammo
    draw_text('AMMO: ',font, WHITE, 10, 65)
    for x in range(player.ammo):
        screen.blit(dag1_box_img, (100 + (x * 7), 67))

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

    
    




    item_box_group.update()
    dagger_group.update()
    decoration_group.update()
    cristall_group.update()
    exit_group.update()

    # 3. Draw objects
    item_box_group.draw(screen)
    dagger_group.draw(screen)
    decoration_group.draw(screen)
    cristall_group.draw(screen)
    exit_group.draw(screen)



    #update player action
    if player.alive:
        # shoot dagger
        if player.is_throwing:
            player.update_action(3)  # 3 - это "Throw attack"
        elif shoot:
            player.is_throwing = True
        elif player.is_hit:
            player.update_action(5)
        elif player.in_air:
            player.update_action(2)#2 is jump
        elif moving_left or moving_right:
            player.update_action(1) # 1 on jooksemine
        else:
            player.update_action(0) #0 is idle

        screen_scroll = player.move(moving_left, moving_right)
        bg_scroll -= screen_scroll



    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT:
            run = False
        # keybord presses
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

        # keyboawrd button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False

    pygame.display.update()


pygame.quit()