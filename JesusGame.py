import pygame
import time 
import os
pygame.init()


SCREEN_WIDTH = 1080
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.5)

# initialzing screen and game name
SCREEN = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("Black Jesus ressurect")

BG = pygame.transform.scale(pygame.image.load("summer5.png"),(SCREEN_WIDTH,SCREEN_HEIGHT))
FPS = pygame.time.Clock()

# game variables
GRAVITY = 0.75
TILE_SIZE = 40


# game movements
move_left = False
move_right = False
attack = False
slash_attack = False
throw = False
throwable_in_air = False

# load images
# bullet
slash_image = pygame.image.load("/Users/eric.m.gichohi/Documents/player/Attack/0.png").convert_alpha()
weapon_image = pygame.image.load("/Users/eric.m.gichohi/Documents/player/all_sprites/FB00_nyknck/FB00_nyknck/FB001.png").convert_alpha()
throwable_image = pygame.image.load("/Users/eric.m.gichohi/Documents/player/Explosions/grenade.png").convert_alpha()
health_image = pygame.transform.scale(pygame.image.load("/Users/eric.m.gichohi/Documents/player/world_design/heart.png"),(15,15))

#pick up boxes images
health_box_image =  pygame.transform.scale(pygame.image.load("/Users/eric.m.gichohi/Documents/player/pick_items/Health.png"),(25,25))
Ammo_box_image = pygame.image.load("/Users/eric.m.gichohi/Documents/player/pick_items/Ammo.png").convert_alpha()

# RGB 
RED = (255,0,0)
GREEN = (0, 255, 0)
BLUE = (0,0,255)
WHITE = (255, 255, 255)
BLACK = (0,0,0)



#fonts
FONT = pygame.font.SysFont("press_start_2p.ttf", 30)

#item pick ups
item_boxes = {
    "Health":   health_box_image, 
    "Ammo": Ammo_box_image
}

# drawing background
def draw_BG():
    SCREEN.blit(BG,(0,0))


def draw_font(text, font, text_colour, x , y):
    image = font.render(text, font,text_colour)
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

        #ai 
        self.move_counter = 0
        self.idling = False

        # animation folders
        all_animations = ['Idle', 'Run', 'Death']

        for animation in all_animations:
            # reset temp list of images
            temp_list = []

            # number of pictires in folder
            num_of_frames = len(os.listdir(f"/Users/eric.m.gichohi/Documents/{self.char_type}/{animation}"))

            # load all animations
            for i in range(num_of_frames - 1):
                img = pygame.image.load(f"/Users/eric.m.gichohi/Documents/{self.char_type}/{animation}/{i}.png")
                img = pygame.transform.scale(img, (int(img.get_width() * scale),int(img.get_height() * scale)))
                temp_list.append(img)
            self.animations_list.append(temp_list) 

        #acessing frame image
        self.image = self.animations_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x_position, y_position)

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


        # gravity logic
        self.jump_velocity += GRAVITY
        if self.jump_velocity > 10:
            self.jump_velocity 
        dy += self.jump_velocity

        # the worlds surface ground
        if self.rect.bottom + dy > 400:
            dy = 400 - self.rect.bottom
            self.in_the_air = False

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy

    def ai(self):
        #ai movement logic
        if self.Alive and player.Alive:
            if self.direction == 1:
                ai_moving_right = True
            else:
                ai_moving_right = False
            ai_moving_left = not False
            self.move(ai_moving_left, ai_moving_right)
            self.update_action(1)# running
            self.move_counter += 1
            print("endring 1")
         
        if self.move_counter > TILE_SIZE:
            self.direction *= -1
            self.move_counter *= -1

            print("endring 2")
        

        
      

        


    # attacking starting point and attack replenish
    def attack(self):
        if self.attack_cooldown == 0 and self.ammo > 0:
            self.attack_cooldown = 25
            attack = Weapon(self.rect.centerx + (1.2 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            weapon_group.add(attack)
            # reduce ammo
            self.ammo -= 1
                

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

class PickupBox(pygame.sprite.Sprite):
    def __init__(self,item_type, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


    def update(self):
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

    # moves weapon rate and direction
    def update(self):
        self.rect.x += (self.direction * self.weapon_speed)

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

        # checks for collision on enemy
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, weapon_group, False):
                if enemy.Alive:
                    enemy.health -= 25
                    print(enemy.health)
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
        self.timer = 100
        self.y_velocity = -10
        self.throw_speed = 10
        self.image = throwable_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        # applying gravity
        self.y_velocity += GRAVITY
        dx = self.direction * self.throw_speed 
        dy = self.y_velocity

        # checks when the throwables has hit the ground
        if self.rect.bottom + dy > 400:
            dy = 400 - self.rect.bottom
            self.throw_speed = 0

        if self.rect.right + dx > SCREEN_WIDTH  or self.rect.left + dx < 0:
            self.direction *= -1
            dx = self.direction * self.throw_speed


        # update throwable direction
        self.rect.x += dx
        self.rect.y += dy

        # exlposion animation intialized
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 2, "player")
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


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale,  char_type):
        pygame.sprite.Sprite.__init__(self)

        self.char_type = char_type
        self.frame_index = 0
        self.images = []
        for _ in range(1,21):
            img = pygame.image.load(f"/Users/eric.m.gichohi/Documents/{self.char_type}/Explosions/PixelSimulations/Explosion2/000{_}.png").convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale),int(img.get_height() * scale)))
            self.images.append(img)

        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.counter = 0
    
    def update(self):
        EXPLOSION_SPEED = 3

        # update explosion animation
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            self.image = self.images[self.frame_index]
            
            # if animation has reached end of the list, reset back to start
            if self.frame_index >= len(self.images) - 1:
                self.kill()
            else:
                self.image = self.images[self.frame_index]

# sprite Groups, quicker way to update and draw
weapon_group = pygame.sprite.Group()
item_pickup_group = pygame.sprite.Group()
slashAttack_group = pygame.sprite.Group()
throwable_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

#item pick up
itemBox = PickupBox("Health", 500, 350)
itemBox2 = PickupBox("Ammo", 650, 350)

item_pickup_group.add(itemBox)
item_pickup_group.add(itemBox2)

# initialzing characters
player = Character("player", 200, 400, 2, 8, 10, 5)
# health bar
health_bar = HealthBar(105, 15, player.health, player.health)

enemy1 = Character("enemy", 600, 350, 2, 2, 5, 5)
enemy2 = Character("enemy", 700, 350, 2, 2, 5, 5)
#adding enemy to the group
enemy_group.add(enemy1)
enemy_group.add(enemy2)


#def main():
# main gameloop
run = True
while run:

    FPS.tick(30)
    draw_BG()

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

    # updates players action
    if player.Alive:
        player.move(move_left, move_right)

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

    '''pressed_key = pygame.key.get_pressed()
            
    #all movements
    if pressed_key[pygame.K_d] and player.velocity + player.player_pos.width + player.x_position <= SCREEN_WIDTH:
        player.x_position += player.velocity

    if pressed_key[pygame.K_a] and player.x_position - player.velocity  >= 0:
        player.x_position -= player.velocity

    if pressed_key[pygame.K_w] and player.y_position - player.velocity - player.player_pos.height >= 0:
        player.y_position -= player.velocity

    if pressed_key[pygame.K_s] and player.y_position + player.velocity + player.player_pos.height < SCREEN_HEIGHT: 
        player.y_position += player.velocity

    if pressed_key[pygame.K_ESCAPE]:
        run = False'''
    
    
    '''player.player_pos = player.char_image.get_rect(center=(player.x_position,player.y_position))
    SCREEN.blit(player.char_image,player.player_pos)

    pygame.display.flip()'''

pygame.quit()

'''if __name__ == "__main__":
    main()'''
