import pygame
import time
import random
pygame.init()

width, height = 750, 750
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("space shooter")

# Text
main_font = pygame.font.SysFont("comidsans", 50)
lost_font = pygame.font.SysFont("comidsans", 60)

level = 0
lives = 5

##Eneemy
wave_length = 5
enemies = []
enemy_vel = 1


#Color
white = (255, 255, 255)

red_space_ship = pygame.image.load("pixel_ship_red_small.png")
green_space_ship = pygame.image.load("pixel_ship_green_small.png")
blue_space_ship = pygame.image.load("pixel_ship_blue_small.png")

yellow_space_ship = pygame.image.load("pixel_ship_yellow.png")

red_laser = pygame.image.load("pixel_laser_red.png")
green_laser = pygame.image.load("pixel_laser_green.png")
blue_laser = pygame.image.load('pixel_laser_blue.png')
yellow_laser = pygame.image.load("pixel_laser_yellow.png")

#background
bg = pygame.transform.scale(pygame.image.load("background-black.png"), (width, height))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
    def move(self, vel):
        self.y += vel
    def off_screen(self, height):
        return not (self.y <= height and self.y >=0)

    def collision(self, obj):
        return collide(self, obj)

class Ship:

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

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
         if self.cool_down_counter >= 30:
             self.cool_down_counter = 0
         elif self.cool_down_counter > 0:
             self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()
    def get_heigth(self):
        return self.ship_img.get_height()

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = yellow_space_ship
        self.laser_img = yellow_laser
        self.health_max = health
        self.mask = pygame.mask.from_surface(self.ship_img)

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
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height()+10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.health_max), 10))


class Enemy(Ship):
    color_map = {
        "red": (red_space_ship, red_laser),
        "green": (green_space_ship, green_laser),
        "blue": (blue_space_ship, blue_laser)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.color_map[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


player = Player(350, 650)




def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offet_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offet_y)) != None
def main():
    run = True
    fps = 60
    clock = pygame.time.Clock()
    playe_vel = 5
    laser_vel = 8

    level = 0
    lives = 5
    wave_length = 5
    lost = False
    lost_count = 0

    def draw_window():
        win.fill(white)
        win.blit(bg, (0, 0))
        lives_label = main_font.render(f"Level: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        win.blit(lives_label, (10, 10))
        win.blit(level_label, (width - level_label.get_width() - 10, 10))
        for enemy in enemies:
            enemy.draw(win)
        player.draw(win)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255, 255, 255))
            win.blit(lost_label, (width / 2 - lost_label.get_width() / 2, height / 2))

        pygame.display.flip()

    while run:
        clock.tick(fps)
        draw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > fps * 3:
                run = False
            else:
                continue
        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, width-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] and player.x < width - player.get_width() - playe_vel:
            player.x += 5
        if keys[pygame.K_LEFT] and player.x > 5:
            player.x -= 5
        if keys[pygame.K_UP] and player.y - playe_vel >0:
            player.y -= 5
        if keys[pygame.K_DOWN] and player.y < height - player.get_heigth() - playe_vel - 20:
            player.y += 5
        if keys[pygame.K_SPACE]:
             player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 4*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_heigth() > height:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)


def main_menu():
    title_font = pygame.font.SysFont("comicsans", 40)
    run = True
    while run:
        win.blit(bg, (0, 0))
        title_label = title_font.render("appuyer sur la souris pour commencer...", 1, (255, 255, 255))
        win.blit(title_label, (width/2 - title_label.get_width()/2, height/2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


if __name__ == '__main__':
    main_menu()
