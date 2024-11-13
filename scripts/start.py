import pygame, sys
import os
import random
from pytmx.util_pygame import load_pygame

pygame.init()


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 520

TILE_SIZE = 15

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Kill the fucking hero')

#set framerate
clock = pygame.time.Clock()
FPS = 60

#define game variables
GRAVITY = 0.75

#define player action variables
moving_left = False
moving_right = False
shoot = False


#load images
dagger_img = pygame.image.load('rocky/Sprites/Gino Character/PNG/dagger/1.png').convert_alpha()
dagger_img2 = pygame.transform.scale(dagger_img, (int(dagger_img.get_width() * 2), int(dagger_img.get_height() * 2)))

#pick up boxes
diamond_box_img = pygame.image.load('rocky/Collectible/Diamond/1.png').convert_alpha()
dag1_box_img = pygame.image.load('rocky/Collectible/Dag/1.png').convert_alpha()
dag_box_img = pygame.transform.scale(dag1_box_img, (int(dag1_box_img.get_width() * 2), int(dag1_box_img.get_height() * 2)))
heart_box_img = pygame.image.load('rocky/Collectible/Heart/1.png').convert_alpha()

item_boxes ={
    "Health"    : heart_box_img,
    "Ammo"      : dag_box_img,
    "Diamond"   : diamond_box_img
}


#define colours
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

#define font
font = pygame.font.SysFont('Futura', 30)

def draw_text(text, foont, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
    screen.fill(BLACK)


tmx_maps = {0: load_pygame('tiled/test2.tmx')}


#creating camera, peremesti potom v podhodjasee mesto
camera_group = pygame.sprite.Group()




class Level:
    def __init__(self, tmx_map, scale_factor=2, layer_names=None):
        self.tmx_data = tmx_map
        self.scale_factor = scale_factor
        self.layer_names = layer_names  # Store layer names to be drawn

    def draw(self, surface):
        # Draw each specified layer
        for layer_name in self.layer_names:
            layer = self.tmx_data.get_layer_by_name(layer_name)
            if layer and hasattr(layer, 'tiles'):
                for x, y, surf in layer.tiles():
                    # Scale tile image and position
                    scaled_surf = pygame.transform.scale(
                        surf,
                        (int(surf.get_width() * self.scale_factor), int(surf.get_height() * self.scale_factor))
                    )
                    screen_x = x * TILE_SIZE * self.scale_factor
                    screen_y = y * TILE_SIZE * self.scale_factor
                    surface.blit(scaled_surf, (screen_x, screen_y))






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
            num_of_frames =  len(os.listdir(f'rocky/Sprites/{self.char_type}/PNG/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'rocky/Sprites/{self.char_type}/PNG/{animation}/{i+1}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                #img_mask = pygame.mask.from_surface(img)
                #mask_image = img_mask.to_surface()
                temp_list.append(img)
            self.animation_list.append(temp_list)
        
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)


        self.collision_rect = pygame.Rect(
                self.rect.x +10 , self.rect.y +30,  # Adjust the position (inset)
                self.rect.width - 60, self.rect.height -35 # Adjust the size
            )

    def update(self):
        self.update_animation()
        self.check_alive()
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
        
        if self.alive and enemy.alive and self.collision_rect.colliderect(enemy.collision_rect):
            self.take_damage(10)

        if self.direction == 1:  # Facing right
            self.collision_rect.topleft = (self.rect.x + 10, self.rect.y + 35)
        else:  # Facing left
            self.collision_rect.topleft = (self.rect.x + 45, self.rect.y + 35)  # Adjust the x-value for left-facing






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

        #jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        #apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y #for jump

        # check collision with floor
        if self.rect.bottom + dy > 500:
            dy = 500 - self.rect.bottom
            self.in_air = False
        else:
            self.in_air = True

        #update rectangle position
        self.rect.x += dx
        self.rect.y += dy


        


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
         pygame.draw.rect(screen, (255, 0, 0), self.collision_rect, 1)  # Red outline for collision rect


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

        self.collision_rect = pygame.Rect(
                self.rect.x +10 , self.rect.y +10,  # Adjust the position (inset)
                self.rect.width - 10, self.rect.height -10 # Adjust the size
            )

    def update(self):
        self.update_animation()
        self.check_alive()

        self.collision_rect.topleft = (self.rect.x + 10, self.rect.y + 10)


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

        # check collision with floor
        if self.rect.bottom + dy > 500:
            dy = 500 - self.rect.bottom
            self.in_air = False
        else:
            self.in_air = True

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy
            


    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0) #idle
                self.idling = True
                self.idle_counter = 50

            #chek if near
            if self.vision.colliderect(player.collision_rect):
                #attack
                self.update_action(2)
                self.attack_speed = self.speed * 1.2

        

                if player.collision_rect.centerx - self.collision_rect.centerx > 10 or player.collision_rect.centerx - self.collision_rect.centerx < 10:
                    if player.collision_rect.centerx < self.collision_rect.centerx:
                        self.move(True, False)
                    elif player.collision_rect.centerx > self.collision_rect.centerx:
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
                self.is_hit = False
                self.update_action(0)  # Возвращаемся к Idle
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


    def check_alive(self):
        if self.health <= 0 and self.alive:
            self.alive = False
            self.update_action(4)  # Устанавливаем "Death" только один раз

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        pygame.draw.rect(screen, (255, 0, 0), self.collision_rect, 1)  # Red outline for collision rect
        pygame.draw.rect(screen, RED, self.vision, 1)  # Red outline for collision rect



class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
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
        self.rect.x += (self.direction * self.speed)
        #check if dagger has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH - 100:
            self.kill()

class Camera:
    def __init__(self, width, height):
        self.camera_rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        # Directly apply the camera offset for pygame.Rect objects
        if isinstance(entity, pygame.Rect):
            return entity.move(self.camera_rect.topleft)
        # Otherwise, apply the offset based on collision_rect or rect
        if hasattr(entity, 'collision_rect'):
            return entity.collision_rect.move(self.camera_rect.topleft)
        return entity.rect.move(self.camera_rect.topleft)

    def update(self, target):
        target_rect = target.collision_rect if hasattr(target, 'collision_rect') else target.rect
        x = -target_rect.centerx + SCREEN_WIDTH // 2
        y = -target_rect.centery + SCREEN_HEIGHT // 2

        # Limit scrolling to map boundaries
        x = min(0, x)  # Left boundary
        y = min(0, y)  # Top boundary
        x = max(-(self.width - SCREEN_WIDTH), x)  # Right boundary
        y = max(-(self.height - SCREEN_HEIGHT), y)  # Bottom boundary

        self.camera_rect = pygame.Rect(x, y, self.width, self.height)




#create sprite groups
dagger_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
#creating camera, peremesti potom v podhodjasee mesto
camera_group = pygame.sprite.Group()



#temp -create item boxes
item_box = ItemBox('Health', 100, 450)
item_box_group.add(item_box)
item_box = ItemBox('Ammo', 400, 450)
item_box_group.add(item_box)
item_box = ItemBox('Diamond', 600, 450)
item_box_group.add(item_box)

level = Level(tmx_maps[0], scale_factor=1.5, layer_names=["background", "border"])


player = Main_character('Gino Character', 200, 200, 1.65, 5, 20)
camera_group.add(player)
health_bar = HeathBar(10, 10, player.health, player.health)
enemy = Enemy02('Enemy02', 300, 200, 1.65, 2)
enemy_group.add(enemy)

camera = Camera(level.tmx_data.width * TILE_SIZE * level.scale_factor,
        level.tmx_data.height * TILE_SIZE * level.scale_factor)


run = True
while run:

    clock.tick(FPS)

    draw_bg()

    camera.update(player)

    for layer_name in level.layer_names:
        layer = level.tmx_data.get_layer_by_name(layer_name)
        if layer and hasattr(layer, 'tiles'):
            for x, y, surf in layer.tiles():
                scaled_surf = pygame.transform.scale(
                    surf,
                    (int(surf.get_width() * level.scale_factor),
                     int(surf.get_height() * level.scale_factor))
                )
                screen_x = x * TILE_SIZE * level.scale_factor
                screen_y = y * TILE_SIZE * level.scale_factor
                screen.blit(scaled_surf, camera.apply(pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)))


    level.draw(screen)

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
    screen.blit(pygame.transform.flip(player.image, player.flip, False), camera.apply(player))


    
    for enemy in enemy_group:
        enemy.ai()
        enemy.update()
        enemy.draw()
        screen.blit(enemy.image, camera.apply(enemy))

        

    for dagger in dagger_group:
        if pygame.sprite.collide_rect(dagger, enemy) and enemy.alive:
            enemy.take_damage(25)
            dagger.kill()
    
    # Update and draw item boxes and daggers with camera offset
    for item in item_box_group:
        item.update()
        screen.blit(item.image, camera.apply(item))
    for dagger in dagger_group:
        dagger.update()
        screen.blit(dagger.image, camera.apply(dagger))




    #update and draw groups
    dagger_group.update()
    item_box_group.update()
    dagger_group.draw(screen)
    item_box_group.draw(screen)


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
        player.move(moving_left, moving_right)

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