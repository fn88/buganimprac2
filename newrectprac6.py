import pygame as pg
import sys, os, random, math

FPS = 30

class Player:
    def __init__(self, location, facing):
        self.sprite_sheet = pg.image.load("arrowspritesheet8.png").convert()
        self.sprite_sheet.set_colorkey((0, 255, 255))
        self.sprite = self.sprite_sheet.subsurface(0, 0, 40, 40)
        self.rect = self.sprite.get_rect(center=location)
        self.speed = 5
        self.direction = [0, 0]
        self.facing = facing
        self.all_directions = [[0, -1, "N"],
                               [1, -1, "NE"],
                               [1, 0, "E"],
                               [1, 1, "SE"],
                               [0, 1, "S"],
                               [-1, 1, "SW"],
                               [-1, 0, "W"],
                               [-1, -1, "NW"],
                               [0, 0]]
        self.sprite_list = []                      
        for y in range(0, 41, 40):
            for x in range(0, 121, 40):
                unpacked_sprite = self.sprite_sheet.subsurface(pg.Rect(x, y, 40, 40))
                self.sprite_list.append(unpacked_sprite)

        for direction in self.all_directions[:8]:
            if direction[2] == self.facing:
                self.sprite = self.sprite_list[self.all_directions.index(direction)]
        

    def move(self):
        self.rect.x += self.speed * self.direction[0]
        self.rect.y += self.speed * self.direction[1]


    def get_event(self, event, objects):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                objects.add(Arrows(self.rect.center, self.facing))
            if event.key == pg.K_a or event.key == pg.K_LEFT: 
                self.direction[0] -= 1
            if event.key == pg.K_d or event.key == pg.K_RIGHT:
                self.direction[0] += 1
            if event.key == pg.K_w or event.key == pg.K_UP:
                self.direction[1] -= 1
            if event.key == pg.K_s or event.key == pg.K_DOWN:
                self.direction[1] += 1
        if event.type == pg.KEYUP:
            if event.key == pg.K_a or event.key == pg.K_LEFT:
                self.direction[0] += 1
            if event.key == pg.K_d or event.key == pg.K_RIGHT:
                self.direction[0] -= 1
            if event.key == pg.K_w or event.key == pg.K_UP:
                self.direction[1] += 1
            if event.key == pg.K_s or event.key == pg.K_DOWN:
                self.direction[1] -= 1

    def update(self):
        for direction in self.all_directions[:8]:
            if self.direction == direction[:2]:
                self.sprite = self.sprite_list[self.all_directions.index(direction)]
                self.facing = direction[2]
        self.speed = (4 if all(self.direction) else 5)
        self.move()        
                

    def draw(self, surface):
        surface.blit(self.sprite, self.rect)

class Arrows(pg.sprite.Sprite):
    def __init__(self, location, facing):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load("arrow8missile40.png").convert()
        self.image.set_colorkey((0, 255, 255))
        self.rect = self.image.get_rect(center=location)
        self.speed = 10
        self.facing = facing
        self.move_coords = [self.rect.x, self.rect.y]
        self.sprite_list = []
        for i in range(8):
            copy = self.image.copy()
            rot_copy = pg.transform.rotate(copy, -45*i)
            self.sprite_list.append(rot_copy)

        self.facing_dict = {"N":[0, -1, self.sprite_list[0]],
                            "NE":[1, -1, self.sprite_list[1]],
                            "E":[1, 0, self.sprite_list[2]],
                            "SE":[1, 1, self.sprite_list[3]],
                            "S":[0, 1, self.sprite_list[4]],
                            "SW":[-1, 1, self.sprite_list[5]],
                            "W":[-1, 0, self.sprite_list[6]],
                            "NW":[-1, -1, self.sprite_list[7]]}
        self.image = self.facing_dict[self.facing][2]

    def update(self, screen):
        self.move_coords[0] += self.speed * self.facing_dict[self.facing][0]
        self.move_coords[1] += self.speed * self.facing_dict[self.facing][1]
        self.rect.center = self.move_coords
        if not self.rect.colliderect(screen):
            self.kill()



class Foe():
    def __init__(self, location):
        self.sprites = []
        for i in range(1, 11):
            file = pg.image.load("000"+str(i)+"a.png").convert()  # 10 sprite files named "0001a-10a.png" last 1 is idle stance
            file.set_colorkey((0, 255, 255))
            self.sprites.append(file)
        self.move_anim_index = 9
        self.image = self.sprites[self.move_anim_index]
        self.rotated_image = self.image.copy()
        self.rect = self.image.get_rect(center=location)
        self.move_rect_coords = [self.rect.x, self.rect.y]
        self.angle = 90
        self.speed = 2
        self.time = 0
        self.frames_counter = 0
        

    def move_anim(self, rate): # rate is in frames
        if self.frames_counter % rate == 0:
            self.move_anim_index += 1
            if self.move_anim_index >= 9:
                self.move_anim_index = 0
            self.image = self.sprites[self.move_anim_index]
            self.rotated_image = self.image.copy()
            self.rotated_image = pg.transform.rotate(self.image, self.angle - 90)
            self.rect = self.rotated_image.get_rect(center=self.rect.center)


    def move(self, last_tick):
        self.move_anim(1)    # fix later
        self.rect.x += int(self.speed * math.cos(self.angle)) 
        self.rect.y -= int(self.speed * math.sin(self.angle))
        self.move_rect_coords = [self.rect.x, self.rect.y]


    def change_direction(self, change_time): # change_time in frames
        if self.frames_counter % change_time == 0: 
            a = random.choice([-1, 1])
            self.angle += a * 5
            if self.angle < 0: self.angle += 360
            if self.angle > 360: self.angle -=360

        
    def track_time(self, last_tick, amount):
        self.time += last_tick
        self.frames_counter += 1
        if self.time >= last_tick * amount:
            self.time = 0
            self.counter = 0


    def think(self, last_tick):
        self.track_time(last_tick, FPS*2)
        self.change_direction(FPS)


    def update(self, last_tick, screen_rect):
        self.think(last_tick)
        self.move(last_tick)


    def draw(self, screen):
        screen.blit(self.rotated_image, self.move_rect_coords)


class ControlGame:
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.done = False
        self.keys = pg.key.get_pressed()
        self.clock = pg.time.Clock()
        self.last_tick = 0
        self.player = Player((200, 200), "E")
        self.foe = Foe((300, 300))
        self.objects = pg.sprite.Group()
        

    def event_loop(self):
        for event in pg.event.get():
            self.keys = pg.key.get_pressed()
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True
            self.player.get_event(event, self.objects)

    def update(self):
        self.player.update()
        self.foe.update(self.last_tick, self.screen_rect)
        self.objects.update(self.screen_rect)
        

    def draw(self):
        self.screen.fill((50, 50, 50))
        self.player.draw(self.screen)
        self.foe.draw(self.screen)
        self.objects.draw(self.screen)
        

    def main_loop(self):
        while not self.done:
            self.event_loop()
            self.update()
            self.draw()
            pg.display.flip()
            self.last_tick = self.clock.tick(FPS)



if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.display.set_mode((1024, 640))
    run_game = ControlGame()
    run_game.main_loop()
    pg.quit()
sys.exit()