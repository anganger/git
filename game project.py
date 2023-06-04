import pygame
import random
pygame.mixer.pre_init(44100,16,2,4096)
pygame.init()
pygame.font.init()

pygame.display.set_caption("rocket league game") #caption
icon=pygame.image.load("icon.png") #icon
pygame.display.set_icon(icon) #display icon on window
width, height =750, 750
screen= pygame.display.set_mode((width, height))

background=pygame.image.load("bg.png") #background picture

#player picture and lazer picture
player_img=pygame.image.load("player.png")
player_laser_img=pygame.image.load("pixel_laser_yellow.png")

#music
pygame.mixer.music.load("music.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

#alien picture and lazer picture
alien_img_red=pygame.image.load("pixel_ship_red_small.png")
alien_laser_img_red=pygame.image.load("pixel_laser_red.png")
alien_img_green=pygame.image.load("pixel_ship_green_small.png")
alien_laser_img_green=pygame.image.load("pixel_laser_green.png")

class Lazer:
    def __init__(self, x, y, img):
        self.x=x
        self.y=y
        self.img= img
        self.mask= pygame.mask.from_surface(img)

    def draw(self, window):
        window.blit(self.img, (self.x -18, self.y - 15))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class ship:  #abstrat class
    COOLDOWN = 25
    def __init__(self, x, y, health=100):
        self.x=x
        self.y=y
        self.health=health
        self.player_img=None
        self.laser_img=None
        self.lasers=[]
        self.cool_down_counter=0

    def draw(self, window):
        window.blit(self.player_img, (self.x, self.y))
        for lasers in self.lasers:
            lasers.draw(screen)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)


    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:  #cooldown counter-time is over
            laser = Lazer(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter=1

    def get_width(self):
        return self.player_img.get_width()

    def get_height(self):
        return self.player_img.get_height()


class player(ship):
    high_score = 0
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.player_img= player_img
        self.laser_img= player_laser_img
        self.mask=pygame.mask.from_surface(self.player_img)
        self.max_health=health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        player.high_score += 1
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(screen)

    def healthbar(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y + self.player_img.get_height() + 10, self.player_img.get_width(),10))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y + self.player_img.get_height() + 10, self.player_img.get_width() * (self.health/self.max_health),10))

class Enemy(ship):
    COLOUR_MAP= {"red": (alien_img_red, alien_laser_img_red), "green": (alien_img_green, alien_laser_img_green)}
    def __init__(self, x , y, colour, health=100):
        super().__init__(x, y, health)
        self.player_img, self.laser_img = self.COLOUR_MAP[colour]
        self.mask = pygame.mask.from_surface(self.player_img)

    def move(self, vel):
        self.y+= vel



def collide(obj1, obj2): # colling system function
     offset_x = obj2.x - obj1.x
     offset_y = obj2.y - obj1.y
     return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    running= True
    FPS=60
    level =0
    lives =5
    font= pygame.font.SysFont('comicsans', 30)
    lost_font= pygame.font.SysFont('comicsans', 50)

    #enemy object initialisatoion
    enemies=[]
    wave_length=5
    enemy_vel=1

    velocity=5
    laser_velocity=5

    player_obj= player(750/2-64, 630) #player initial possition

    clock=pygame.time.Clock()

    lost = False
    lost_count=0

    def redraw_window():
        screen.blit(background, (0, 0)) #background

        #draw text
        levels_label= font.render(f"levels: {level}", 1, (255, 120, 0))
        lives_label= font.render(f"lives: {lives}", 1, (50, 25, 255))
        score_label = font.render(f"score: {player.high_score}", 1, (50, 25, 255))

        screen.blit(levels_label, (10, 10))
        screen.blit(score_label, (10, 50))
        screen.blit(lives_label, (width- lives_label.get_width()-10, 10))

        for enemy in enemies: # drawing enemies
            enemy.draw(screen)

        player_obj.draw(screen)

        if lost: # lost display
            lost_lable = lost_font.render("You Lost!!", 1, (255, 25, 255))
            screen.blit(lost_lable, (width/2 - lost_lable.get_width()/2, 350))

        # updating screen
        pygame.display.update()

    while running:
        clock.tick(FPS)
        redraw_window()  # calling redraw function

        # stopping the game if lives becomes zero or HEALTH BECOMES ZERO TOO
        if lives <= 0 or player_obj.health <=0:
            lost = True
            lost_count +=1

        # lost display on the screen
        if lost:
            if lost_count > FPS * 3:
                running = False
            else:
                continue

        # incrementing the level and adding more enemies to the enemies list for each sucessive level
        if len(enemies) == 0:
            level+=1
            wave_length +=5
            for i in range(wave_length):
                enemy=Enemy(random.randrange(50,width-100),random.randrange(-1500,-100),random.choice(["red", "green"]))
                enemies.append(enemy)

        # quiting the game
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                quit()

        # moving of the player and shooting
        keys= pygame.key.get_pressed() # movement of the player
        if keys[pygame.K_LEFT] and player_obj.x - velocity > 0: # left
            player_obj.x -= velocity
        if keys[pygame.K_RIGHT] and (player_obj.x + player_obj.get_width() + velocity)< width:  #right
            player_obj.x += velocity
        if keys[pygame.K_UP] and player_obj.y - velocity > 0: # up
            player_obj.y -= velocity
        if keys[pygame.K_DOWN] and player_obj.y + player_obj.get_height() + 20 + velocity < height: #down
            player_obj.y += velocity
        if keys[pygame.K_SPACE]:
            player_obj.shoot()


        # decrements the life if the alien touches ground
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_velocity, player_obj)

            if random.randrange(0, 2*60)==1:
                enemy.shoot()

            if collide(enemy, player_obj):
                player_obj.health -= 10
                enemies.remove(enemy)
            elif enemy.y +enemy.get_height() > height:
                lives -= 1
                enemies.remove(enemy)

        player_obj.move_lasers(-laser_velocity, enemies)
def start_function(): # main screen after lost and start
    title_font = pygame.font.SysFont("comicsans", 50)
    run = True
    while run:
        screen.blit(background, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        screen.blit(title_label, (width/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()
start_function()