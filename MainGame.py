import pygame
from pygame import mixer
import time 
import os
import random 
import csv
import Button_main

# initialize pygame module and music module
pygame.init()
mixer.init()


SCREEN_WIDTH = 1080
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.5)

# initialzing screen and game name
SCREEN = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("Black Jesus ressurect")

CLOCK = pygame.time.Clock()
FPS = 60


# game constant variables
GRAVITY = 0.75
MAX_LEVELS = 2

# amount of tiles, rows, colums and tile size
TILE_TYPES = 20
ROWS = 12
MAX_COL = 150
SCROLL_THRESH = 300
TILE_SIZE = SCREEN_HEIGHT // ROWS

# game variables
level = 1
screen_scroll = 0
bg_scroll = 0
start_game = False
intro_fade = False


# game movements actions
move_left = False
move_right = False
attack = False
slash_attack = False
throw = False
throwable_in_air = False

# load music and sound
pygame.mixer.music.load('/Users/eric.m.gichohi/Documents/shooter_assets/audio/music2.mp3')
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1, 0.0, 5000)
jump_fx = pygame.mixer.Sound('/Users/eric.m.gichohi/Documents/shooter_assets/audio/jump.wav')
jump_fx.set_volume(0.05)
grenade_fx = pygame.mixer.Sound('/Users/eric.m.gichohi/Documents/shooter_assets/audio/grenade.wav')
grenade_fx.set_volume(0.05)
shot_fx = pygame.mixer.Sound('/Users/eric.m.gichohi/Documents/shooter_assets/audio/shot.wav')
shot_fx.set_volume(0.05)

# storing tiles in a list
tile_images = []
# load all tiles 
for j in range(TILE_TYPES + 1):
    img = pygame.image.load(f"/Users/eric.m.gichohi/Documents/Tiles/{j}.png").convert_alpha()
    img = pygame.transform.scale(img, (int(TILE_SIZE), int(TILE_SIZE)))
    tile_images.append(img)


# loading background images
pine_1 = pygame.image.load("/Users/eric.m.gichohi/Documents/background/pine1.png").convert_alpha()
pine_2 = pygame.image.load("/Users/eric.m.gichohi/Documents/background/pine2.png").convert_alpha()
mountain = pygame.image.load("/Users/eric.m.gichohi/Documents/background/mountain.png").convert_alpha()
sky = pygame.image.load("/Users/eric.m.gichohi/Documents/background/sky_cloud.png").convert_alpha()

#load and save images
start_image = pygame.image.load("/Users/eric.m.gichohi/Documents/shooter_assets/img/start_btn.png").convert_alpha()
restart_image = pygame.image.load("/Users/eric.m.gichohi/Documents/shooter_assets/img/restart_btn.png").convert_alpha()
exit_image = pygame.image.load("/Users/eric.m.gichohi/Documents/shooter_assets/img/exit_btn.png").convert_alpha()


# load weapon images 
slash_image = pygame.image.load("/Users/eric.m.gichohi/Documents/player/Attack/0.png").convert_alpha()
weapon_image = pygame.image.load("/Users/eric.m.gichohi/Documents/player/all_sprites/FB00_nyknck/FB00_nyknck/FB001.png").convert_alpha()
throwable_image = pygame.image.load("/Users/eric.m.gichohi/Documents/player/Explosions/grenade.png").convert_alpha()
health_image = pygame.transform.scale(pygame.image.load("/Users/eric.m.gichohi/Documents/player/world_design/heart.png"),(15,15))

#pick-up boxes images
health_box_image =  pygame.transform.scale(pygame.image.load("/Users/eric.m.gichohi/Documents/Tiles/19.png"),(25,25))
Ammo_box_image = pygame.image.load("/Users/eric.m.gichohi/Documents/Tiles/17.png").convert_alpha()

# RGB 
RED = (102, 0, 0)
GREEN = (0, 100, 0)
BLUE = (0,0,255)
WHITE = (255, 255, 255)
BLACK = (0,0,0)

#font name and size
FONT = pygame.font.SysFont("press_start_2p.ttf", 30)

#item pick-ups
item_boxes = {
    "Health":   health_box_image, 
    "Ammo": Ammo_box_image
}

# resets the game assets and world
def restart_game():
    weapon_group.empty()
    item_pickup_group.empty()
    slashAttack_group.empty()
    throwable_group.empty()
    explosion_group.empty()
    enemy_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    # resets world data
    # loading in world
    data = []
    for x in range(ROWS + 1):
        row = [-1] * MAX_COL
        data.append(row)

    return data


# drawing background
def draw_BG():
    SCREEN.fill(GREEN)

        # getting background image width
    image_width = sky.get_width()
    
    for x in range(4):
        SCREEN.blit(sky, ((x * image_width) - bg_scroll * 0.4, 0))
        SCREEN.blit(mountain, ((x * image_width) -bg_scroll * 0.6, SCREEN_HEIGHT - mountain.get_height() - 250))
        SCREEN.blit(pine_2, ((x * image_width) -bg_scroll * 0.8, SCREEN_HEIGHT - pine_2.get_height() - 25))
        SCREEN.blit(pine_1, ((x * image_width) -bg_scroll * 1, SCREEN_HEIGHT - pine_1.get_height() + 5))


def draw_font(text, font, text_colour, x , y):
    image = font.render(text, font, text_colour)
    SCREEN.blit(image, (x,y))


class Character(pygame.sprite.Sprite):
    def __init__(self,char_type, x_position, y_position, scale, velocity, ammo, throwables):
        pygame.sprite.Sprite.__init__(self)
        
        self.Alive = True
        self.velocity = velocity
        self.char_type = char_type
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.ammo = ammo
        self.start_ammo = ammo
        self.throwables = throwables
        self.attack_cooldown = 0
        self.flip = False
        self.jump = False
        self.jump_velocity = 0
        self.in_the_air = True
        self.animations_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.action = 0

        #ai variables
        self.move_counter = 0
        self.idling = False
        self.idle_counter = 0
        #ai vision of the player
        self.vision = pygame.Rect(0, 0, 200, 20)

        # animation folders
        all_animations = ['Idle', 'Run', 'Jump', 'Death']
        for animation in all_animations:
            # reset temp list of images
            temp_list = []

            # number of pictires in folder
            num_of_frames = len(os.listdir(f"/Users/eric.m.gichohi/Documents/{self.char_type}/{animation}"))

            # load all animations
            for i in range(num_of_frames - 1):
                img = pygame.image.load(f"/Users/eric.m.gichohi/Documents/{self.char_type}/{animation}/{i}.png")
                #img = pygame.transform.scale(img, (int(img.get_width() * scale),int(img.get_height() * scale)))
                img = pygame.transform.scale(img, (int(TILE_SIZE) * 1.5,int(TILE_SIZE) * 1.5))
                temp_list.append(img)
            self.animations_list.append(temp_list) 

        #acessing frame image
        self.image = self.animations_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x_position, y_position)
        self.width = self.image.get_width()
        self.height = self.image.get_height()


    def all_updates(self):

        # updates players animations
        self.update_animation()
        # update if player is dead
        self.check_alive()
    
        # updates cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    # moving player
    def move(self, left, right):
        # reset movement variables
        dx = 0
        dy = 0
        screen_scroll = 0

        # moving left
        if left:
            dx = -self.velocity 
            self.direction = -1
            self.flip = True

        # moving right
        if right:
            dx = self.velocity 
            self.direction = 1
            self.flip = False
        
        # jumping
        if self.jump == True and self.in_the_air == False:
            self.jump_velocity = -15
            self.jump == False
            self.in_the_air = True


        # check gravity logic
        self.jump_velocity += GRAVITY
        if self.jump_velocity > 10:
            self.jump_velocity 
        dy += self.jump_velocity

        # check collision with obsticles
        for tile in world.obstacle_list:
            # check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                # check collision with wall for ai
                if self.char_type == "enemy":
                    self.direction *= -1
                    self.move_counter = 0
            # check collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # check if collision from bottom up, jumping
                if self.jump_velocity < 0:
                    self.jump_velocity = 0
                    dy = tile[1].bottom - self.rect.top
                # check if collision top down, falling
                elif self.jump_velocity >= 0:
                    self.jump_velocity = 1
                    self.in_the_air = False
                    dy = tile[1].top - self.rect.bottom


        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        # check if player in water
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0
            dx = 0
       

        # check if player falls off the map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0
            dx = 0

        # check if level completed
        level_completed = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_completed = True
            

        # check if player is on the edge of the map
        if self.char_type == "player":
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                self.rect.x = 0
         
        # update scroll based on players position
        if self.char_type == "player":
            if ((self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.world_length * TILE_SIZE) -  SCREEN_WIDTH) or 
                (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx))):
                self.rect.x -= dx
                screen_scroll = -dx
            
        return screen_scroll, level_completed

    def ai(self):
        #ai movement logic
        if self.Alive and player.Alive:
            # checking when to idle
            if self.idling == False and random.randint(1,200) == 10:
                self.idling = True
                self.idle_counter = 50
                self.update_action(0)# idle

            # check if ai is near the player
            if self.vision.colliderect(player.rect):
                self.update_action(0)# idle
                self.attack() # attack player
            
            else:
                # stopping idling and changing direction 
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = True
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)# running
                    self.move_counter += 1

                    #update vision as enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                
                    if self.move_counter > TILE_SIZE:
                        self.move_counter *= -1
                        self.direction *= -1
                else:
                    self.idle_counter -= 1
                    if self.idle_counter <= 0:
                        self.idling = False

        # ai charaters stay on their positions while screen is scrolling
        self.rect.x += screen_scroll
                
    # attacking starting point and attack replenish
    def attack(self):
        if self.attack_cooldown == 0 and self.ammo > 0:
            shot_fx.play()
            self.attack_cooldown = 25
            attack = Weapon(self.rect.centerx + (1.2 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            weapon_group.add(attack)
            # reduce ammo
            self.ammo -= 1
                
    # attack with slash 
    def slash_attacking(self):
        if self.attack_cooldown == 0:
            self.attack_cooldown = 30
            slash_ATTACK = SlashAttack((self.rect.centerx  * self.direction), self.rect.centery, self.direction, 2)
            slashAttack_group.add(slash_ATTACK)


    def update_animation(self):
        # update animation cooldown
        ANIMATION_COOLDOWN = 100

        # update frame by getting the image
        self.image = self.animations_list[self.action][self.frame_index]

        # checking if enough time has passed since the last update
        if  pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.frame_index += 1

        # if death animation has reached end of the list, reset back to start
        if len(self.animations_list[self.action]) <= self.frame_index:
            if self.action == 3:
                self.frame_index = len(self.animations_list[self.action]) - 1
            else:
                self.frame_index = 0

      
    def update_action(self, new_animation):
        # updates current animation to the next
        if self.action != new_animation:
            self.action = new_animation

            # reseting animation update
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    
    # check if player is alive
    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.velocity = 0
            self.Alive = False
            self.update_action(3)

    def draw(self):
        SCREEN.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World():
    def __init__(self):
        #level obstacles 
        self.obstacle_list = []

    def update_world(self, data):
        # length of list to track the end of the map
        self.world_length = len(data[0])

        for x, row in enumerate(data):
            for y, tile in  enumerate(row):
                if tile >= 0:
                    # gets the image from the indeks
                    img = tile_images[tile]
                    img_rect = img.get_rect()
                    img_rect.x = y * TILE_SIZE
                    img_rect.y = x * TILE_SIZE
                    tile_data = (img, img_rect)
                
                    # surface area
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)   
                    # water surface area
                    elif tile >= 9 and tile <= 10:
                        water =  Water(img, y * TILE_SIZE,  x * TILE_SIZE)
                        water_group.add(water)                      
                    # decorations
                    elif tile >= 11 and tile <= 14:
                        decorations =  Decorations(img, y * TILE_SIZE,  x * TILE_SIZE)
                        decoration_group.add(decorations)

                    # player data initialized
                    elif tile == 15:
                        # initialzing player
                        player =  Character("player", y * TILE_SIZE,  x * TILE_SIZE, 2, 5, 10, 5)
                        health_bar = HealthBar(105, 15, player.health, player.health)
                    
                    # enemy data initialized
                    elif tile == 16:
                        # initialzing enemy
                        enemy = Character("enemy", y * TILE_SIZE,  x * TILE_SIZE, 2, 2, 5, 5)
                        enemy_group.add(enemy)
                    # initialize ammo box
                    elif tile == 17:
                        AmmoBox = PickupBox("Ammo", y * TILE_SIZE,  x * TILE_SIZE)
                        item_pickup_group.add(AmmoBox)
                    # initialize health box
                    elif tile == 19:
                        HealthBox = PickupBox("Health", y * TILE_SIZE,  x * TILE_SIZE)
                        item_pickup_group.add(HealthBox)
                    # exit
                    elif tile == 20:
                        exit =  Exit(img, y * TILE_SIZE,  x * TILE_SIZE)
                        exit_group.add(exit)
        
        return player, health_bar

    # draws obstacles tiles in the world
    def draw_world(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            SCREEN.blit(tile[0],tile[1])


class Decorations(pygame.sprite.Sprite):
    def __init__(self,image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    # updates scroll function for objects
    def update(self):
        self.rect.x += screen_scroll

class Water(pygame.sprite.Sprite):
    def __init__(self,image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    # updates scroll function for objects
    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self,image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    # updates scroll function for objects
    def update(self):
        self.rect.x += screen_scroll

class PickupBox(pygame.sprite.Sprite):
    def __init__(self,item_type, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))



    def update(self):
        # updates scroll function for objects
        self.rect.x += screen_scroll

        # check if the player has picked up box
        if pygame.sprite.collide_rect(self, player):

            # check what item is to be taken
            if self.item_type == "Health":
                player.health += 25

                if player.health > player.max_health:
                    player.health = player.max_health

            elif self.item_type == "Ammo":
                player.ammo  += 10
                
            # delete box
            self.kill()

class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    # updates health
    def draw(self, health):

        self.health = health
        ratio = self.health / self.max_health
        pygame.draw.rect(SCREEN,BLACK, (self.x - 2 , self.y - 2, 154, 24))
        pygame.draw.rect(SCREEN,RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(SCREEN,GREEN, (self.x, self.y, 150 * ratio , 20))
     

class Weapon(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)

        self.weapon_speed = 10
        self.image = weapon_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.attacking_active = False
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    # moves weapon rate and direction
    def update(self):
        self.rect.x += (self.direction * self.weapon_speed) + screen_scroll

        # changing the weapons direction
        weapon_flip = pygame.transform.flip(self.image, True, False)
        if attack == True and self.attacking_active == False and self.direction == -1:
            self.image = weapon_flip 
            self.attacking_active = True
        else:
            self.image


        if self.rect.right > SCREEN_WIDTH  or self.rect.left < 0:
            self.kill()

        # checks for collision of player
        if pygame.sprite.spritecollide(player, weapon_group, False):
            if player.Alive:
                # deplating health
                player.health -= 5
                self.kill()

        for tile in world.obstacle_list:
        # check collision in the x direction
            if tile[1].colliderect(self.rect):
                self.kill()

        # checks for collision on enemy
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, weapon_group, False):
                if enemy.Alive:
                    enemy.health -= 25
                    self.kill()


class SlashAttack(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, scale):
        pygame.sprite.Sprite.__init__(self)
        self.weapon_speed = 10
        self.images = []
        for i in range(0,8):
            imge = pygame.image.load(f"/Users/eric.m.gichohi/Documents/player/Attack/{i}.png").convert_alpha()
            imge = pygame.transform.scale(imge, (int (imge.get_width() * scale), int (imge.get_height() * scale)))
            self.images.append(imge)

        self.image_frame_indeks = 0
        self.image = self.images[self.image_frame_indeks]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.counter = 0


    def update(self):
        SLASH_COOLDOWN = 100
        self.counter += 1


        # next frame begins after cooldown
        if  pygame.time.get_ticks() - player.update_time > SLASH_COOLDOWN:
            self.image_frame_indeks += 1


        # changing the weapons direction
        weapon_flip = pygame.transform.flip(self.image, True, False)
        if attack == True and self.attacking_active == False and self.direction == -1:
            self.image = weapon_flip 
            self.attacking_active = True
        else:
            self.image

         # updating animation
        if self.counter < SLASH_COOLDOWN:
            if self.image_frame_indeks <= len(self.images) - 1:
                self.counter = 0
                self.image = self.images[self.image_frame_indeks]
            else:
                self.kill()

        # checks for collision on enemy
        if pygame.sprite.spritecollide(enemy, slashAttack_group, False):
                if enemy.Alive:
                    enemy.health -= 5
                    print(enemy.health)  


class Throwable(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 70
        self.y_velocity = -10
        self.throw_speed = 10
        self.image = throwable_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        # applying gravity
        self.y_velocity += GRAVITY
        dx = self.direction * self.throw_speed 
        dy = self.y_velocity

        # checks when the throwables has hit the ground
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.throw_speed

            # check collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # check if collision from bottom up, jumping
                if self.y_velocity < 0:
                    self.throw_speed = 0
                    dy = tile[1].bottom - self.rect.top
                # check if collision top down, falling on ground
                elif self.y_velocity >= 0:
                    self.throw_speed = 0
                    dy = tile[1].top - self.rect.bottom         
   

        # update throwable direction
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        # exlposion animation intialized
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y)
            explosion_group.add(explosion)

        # explosion radius damage
            if (abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2  and  
            abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2):
                # depleting health
                player.health -= 50
                self.kill()
                print(player.health)

            for enemy in enemy_group:
                    if (abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2  and 
                        abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2):
                        # depleting health
                        enemy.health -= 50
                        self.kill()
                        print(enemy.health)

# explosion animation class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.frame_index = 0
        self.images = []
        for _ in range(1,6):
            print(_)
            #img = pygame.image.load(f"/Users/eric.m.gichohi/Documents/{self.char_type}/Explosions/PixelSimulations/Explosion2/000{_}.png").convert_alpha()
            img = pygame.image.load(f"/Users/eric.m.gichohi/Documents/shooter_assets/img/explosion/exp{_}.png").convert_alpha()
            img = pygame.transform.scale(img, (int(TILE_SIZE),int(TILE_SIZE)))
            self.images.append(img)

        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.counter = 0
    
    def update(self):
        self.rect.x += screen_scroll
        EXPLOSION_SPEED = 6

        # update explosion animation
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            self.image = self.images[self.frame_index]
            
            # if animation has reached end of the list, reset back to start
            if self.frame_index >= len(self.images) - 1:
                grenade_fx.play()
                self.kill()
            else:
                self.image = self.images[self.frame_index]

class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        # check if fade is complete
        fade_complete = False
        # speed of the rectangle filler
        self.fade_counter += self.speed
        if self.direction == 1: #intro screen
            pygame.draw.rect(SCREEN, self.colour, (0 - self.fade_counter, 0 , SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(SCREEN, self.colour, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(SCREEN, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(SCREEN, self.colour, (0, SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))

        if self.direction == 2: #death screen, vertical screen fade
            pygame.draw.rect(SCREEN, self.colour, (0,0, SCREEN_WIDTH, 0 + self.fade_counter) )
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True

        return fade_complete

# initialize screen fade
introFade = ScreenFade(1, BLACK, 5)
deathFade = ScreenFade(2, RED, 6)

# initialze buttons
start_button = Button_main.Button((SCREEN_WIDTH // 2) - 300, 200, start_image , 1)
exit_button = Button_main.Button((SCREEN_WIDTH // 2) + 50, 200, exit_image , 1)
restart_button = Button_main.Button((SCREEN_WIDTH // 2) -105, 230, restart_image , 2)

# sprite Groups, quicker way to update and draw
weapon_group = pygame.sprite.Group()
item_pickup_group = pygame.sprite.Group()
slashAttack_group = pygame.sprite.Group()
throwable_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# loading in world
world_data = []
for x in range(ROWS + 1):
    row = [-1] * MAX_COL
    world_data.append(row)

# load data in from a file
with open(f"Level_{level}_data_csv", "r", newline = '') as csvfile:
    reader = csv.reader(csvfile, delimiter = ',')
    for y, row in enumerate(reader):
        for x, col in enumerate(row):
            world_data[y][x] = int(col)

print(f"level {level} is loaded! ")

# initializing world 
world = World()
player, health_bar = world.update_world(world_data)


# main gameloop
run = True
while run:
    CLOCK.tick(FPS)

    # main menu
    if start_game == False:
        SCREEN.fill(GREEN)

        #main menu buttons
        if start_button.draw_button(SCREEN):
            start_game = True
            start_intro = True
            print("Game started!")
        if exit_button.draw_button(SCREEN):
            run = False
            print("Game exit!")

    else:
        # draw background
        draw_BG()

        # drawing world level
        world.draw_world()

        draw_font(f"HEALTH: ", FONT, GREEN, 10,15)
        health_bar.draw(player.health)

        draw_font(f"AMMO: ", FONT, WHITE, 10,45)
        for x in range(player.ammo):
            SCREEN.blit(weapon_image, (75 + (x * 15), 40))

        draw_font(f"GREANDE: ", FONT, WHITE, 10,80)
        for x in range(player.throwables):
            SCREEN.blit(throwable_image, (125 + (x * 15), 85))
                    

        player.all_updates()
        player.draw()

        for enemy in enemy_group:
            enemy.ai()
            enemy.all_updates()
            enemy.draw()

        # drawing weapon attack
        weapon_group.draw(SCREEN)
        weapon_group.update()

        # drawing weapon attack
        slashAttack_group.draw(SCREEN)
        slashAttack_group.update()
        
        # drawing throwable attack
        throwable_group.draw(SCREEN)
        throwable_group.update()
        

        # drawing explosion
        explosion_group.draw(SCREEN)
        explosion_group.update()
        
        # drawing items boxes
        item_pickup_group.draw(SCREEN)
        item_pickup_group.update()

        # updating level objects and drawing
        decoration_group.draw(SCREEN)
        decoration_group.update()

        
        water_group.draw(SCREEN)
        water_group.update()

        exit_group.draw(SCREEN)
        exit_group.update()

        if start_intro == True:
            if introFade.fade():
                start_intro = False
                introFade.fade_counter = 0
                

        # updates players action
        if player.Alive:
            screen_scroll, level_completed = player.move(move_left, move_right)
            bg_scroll -= screen_scroll
            # check if level is completed, resets and moves to next level
            if level_completed:
                level += 1
                start_intro = True
                bg_scroll = 0
                world_data = restart_game()
                if level <= MAX_LEVELS:
                    # loads world data
                    with open(f"Level_{level}_data_csv", "r", newline = '') as csvfile:
                        reader = csv.reader(csvfile, delimiter = ',')
                        for y, row in enumerate(reader):
                            for x, col in enumerate(row):
                                world_data[y][x] = int(col)
                        # initializing world 
                        world = World()
                        player, health_bar = world.update_world(world_data)
                        print("New level started!")

            # attack action
            if slash_attack:
                player.slash_attacking()
            
            elif attack:
                player.attack()

            # throwing throwables
            elif throw and throwable_in_air == False and player.throwables > 0:
                throw = Throwable(player.rect.centerx + (player.rect.size[0] * 1.2 * player.direction), player.rect.top , player.direction)
                throwable_group.add(throw)
                player.throwables -= 1
                throwable_in_air = True

            elif player.in_the_air:
                player.update_action(2)#2 jumping action

            elif move_left or move_right:# 1 left and right action
                player.update_action(1)

            else:
                player.update_action(0)#0 idle action
        else:
            # activates when player dies
            pygame.mixer.music.set_volume(0.0)
            screen_scroll = 0
            if deathFade.fade():
                if restart_button.draw_button(SCREEN):
                    pygame.mixer.music.set_volume(0.1)
                    pygame.mixer.music.play(-1, 0.0, 5000)
                    deathFade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    
                    #empty world data
                    world_data = restart_game()
                    # loads world data
                    with open(f"Level_{level}_data_csv", "r", newline = '') as csvfile:
                        reader = csv.reader(csvfile, delimiter = ',')
                        for y, row in enumerate(reader):
                            for x, col in enumerate(row):
                                world_data[y][x] = int(col)
                        # initializing world 
                        world = World()
                        player, health_bar = world.update_world(world_data)
                        print("Game restarted!")

    for event in pygame.event.get():
        # quit game
        if event.type == pygame.QUIT:
            run = False

        # controlling player
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                move_left = True
            if event.key == pygame.K_d:
                move_right = True
            if event.key == pygame.K_SPACE:
                attack = True
            if event.key == pygame.K_k:
                slash_attack = True
            if event.key == pygame.K_q:
                throw = True
            if event.key == pygame.K_w and player.Alive:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                run = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                move_left = False
            if event.key == pygame.K_d:
                move_right = False
            if event.key == pygame.K_q:
                throw = False
                throwable_in_air = False
            if event.key == pygame.K_SPACE:
                attack = False
                attacking_active = False
            if event.key == pygame.K_k:
                slash_attack = False
            if event.key == pygame.K_w and player.Alive:
                player.jump = False

    # updating frames
    pygame.display.update()

pygame.quit()


