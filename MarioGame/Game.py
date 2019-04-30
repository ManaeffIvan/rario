import os
import sys
import pygame

pygame.init()
pygame.key.set_repeat(200, 70)

FPS = 50
WIDTH = 800
HEIGHT = 600
STEP = 10
MAXSPEED = 10
JUMPHEIHT = 20
BONUSES = {'s': 'star'}

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

player = None
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
block_group = pygame.sprite.Group()
boost_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()

tile_width = tile_height = 50
points = 0


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    image = image.convert_alpha()

    if color_key is not None:
        if color_key is -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


tile_images = {'brick': pygame.transform.scale(load_image('brick.png'), (tile_width, tile_height)), 'floor': pygame.transform.scale(load_image('floor.png'), (tile_width, tile_height)), 'empty': load_image('sky.png'), 'question': load_image('question.png'), 'metal_block': pygame.transform.scale(load_image('metal_block.png'), (tile_width, tile_height)), 'star': pygame.transform.scale(load_image('star.png'), (tile_width, tile_height))}
player_image = load_image('mario.png')
evil_mushroom_image = load_image('evilmushroom.png')
life_sign = 0


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return (list(map(lambda x: x.ljust(max_width, '.'), level_map)), max_width)


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            Tile('empty', x, y)
            if level[y][x] == '#':
                Tile('floor', x, y)
            elif level[y][x] == '@':
                new_player = Player(load_image("mario.png"), 14, 1, x, y)
            elif level[y][x] == 'm':
                EvilMushroom(load_image("evilmushroom.png"), 2, 1, x, y, 50)
            elif level[y][x] == 'b':
                Tile('brick', x, y)
            elif level[y][x] in BONUSES:
                Question(load_image("question.png"), 3, 1, x, y, BONUSES[level[y][x]])
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():

    while True:
        screen.fill((0, 0, 0))
        fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT - 50))
        screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 30)
        button = load_image('button.png')
        screen.blit(button, (10, 500))
        string_rendered = font.render('START GAME', 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect().move(40, 515)
        screen.blit(string_rendered, intro_rect)
        screen.blit(button, (220, 500))
        string_rendered = font.render('EXIT', 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect().move(295, 515)
        screen.blit(string_rendered, intro_rect)
        screen.blit(button, (430, 500))
        string_rendered = font.render('RECORDS', 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect().move(480, 515)
        screen.blit(string_rendered, intro_rect)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if 10 <= event.pos[0] <= 210 and 500 <= event.pos[1] <= 545:
                    return
                if 220 <= event.pos[0] <= 420 and 500 <= event.pos[1] <= 545:
                    terminate()
                if 430 <= event.pos[0] <= 630 and 500 <= event.pos[1] <= 545:
                    show_records()
        pygame.display.flip()
        clock.tick(FPS)


def win_screen():
    running = True
    name = '|'
    recorded = False
    while running:
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 50)
        screen.fill(pygame.Color("black"))
        points1 = font.render('YOU WIN!!!', 1, pygame.Color('white'))
        screen.blit(points1, (WIDTH // 2 - 90, 20))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if 97 <= event.key <= 122:
                    name = name[:-1] + chr(event.key).upper() + '|'
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if 300 <= event.pos[0] <= 500 and 200 <= event.pos[1] <= 245:
                    fo = open('data\\records.txt', 'r')
                    s = fo.readline()
                    mas = []
                    while s != '':
                        s = s.split()
                        if len(s) != 2:
                            break
                        mas += [[-int(s[0]), s[1]]]
                        s = fo.readline()
                    mas += [[-points, name[:-1]]]
                    mas = sorted(mas)
                    fo.close()
                    fo = open('data\\records.txt', 'w')
                    for i in mas:
                        print(-i[0], i[1], file=fo)
                    fo.close()
                    name = 'RECORDED!'
                    recorded = True
        button = load_image('button.png')
        screen.blit(button, (300, 200))
        string_rendered = font.render('Enter your name:', 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect().move(280, 100)
        screen.blit(string_rendered, intro_rect)
        string_rendered = font.render('OK', 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect().move(370, 210)
        screen.blit(string_rendered, intro_rect)
        string_rendered = font.render(name, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect().move(320, 150)
        screen.blit(string_rendered, intro_rect)
        pygame.display.flip()
        clock.tick(FPS)
        if recorded:
            pygame.time.delay(2000)
            return
        pygame.display.flip()


def show_num(n, x, y):
    for i in str(n):
        fon1 = pygame.transform.scale(load_image(i + '.png'), (tile_width, tile_height))
        screen.blit(fon1, (x, y))
        x += tile_width + 5


def show_records():
    running = True
    while running:
        fi = open('data\\records.txt', 'r')
        font = pygame.font.Font(None, 50)
        screen.fill(pygame.Color("black"))
        for i in range(10):
            s = fi.readline()
            s = s.split()
            try:
                points1 = s[0]
                while len(points1) < 6:
                    points1 = '0' + points1
                name = s[1]
            except Exception:
                points1 = '000000'
                name = ''
            points1 = font.render(points1, 1, pygame.Color('white'))
            screen.blit(points1, (WIDTH // 2 - 300, 20 + i * 60))
            name = font.render(name, 1, pygame.Color('white'))
            screen.blit(name, (WIDTH // 2 - 150, 20 + i * 60))
        fi.close()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return
        pygame.display.flip()


class Player(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.acceleration_x = 1
        self.acceleration_y = 1
        self.speed_x = 0
        self.speed_y = JUMPHEIHT + 1
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_anim = 'stright'
        self.mode = 'normal'
        self.timer = 0
        self.cur_frame = 7
        self.size_x = tile_width
        self.size_y = tile_height
        self.image = self.frames[7]
        self.animations = {'stright': [6, 7], 'left': [5, 4, 3, 2], 'right': [8, 9, 10, 11], 'jump': [12, 1], 'die': [13, 0]}
        self.pr = 0
        self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.tick = 0
        self.ghost = False

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(pygame.transform.scale(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)), (tile_width, tile_height)))

    def update(self):
        if self.timer > 0:
            self.timer -= FPS
        else:
            self.mode = 'normal'
        if not self.ghost:
            if self.cur_anim == 'stright':
                if self.acceleration_x > 0 and self.speed_x >= 0:
                    self.cur_frame = 1
                else:
                    self.cur_frame = 0
                self.tick = 0
            if self.cur_anim == 'left':
                if self.speed_x > 0:
                    self.cur_frame = 3
                elif self.tick % 3 == 0:
                    self.cur_frame += 1
                    self.cur_frame %= 3
            if self.cur_anim == 'right':
                if self.speed_x < 0:
                    self.cur_frame = 3
                elif self.tick % 3 == 0:
                    self.cur_frame += 1
                    self.cur_frame %= 3
            if self.cur_anim == 'jump':
                if self.acceleration_x < 0:
                    self.cur_frame = 1
                else:
                    self.cur_frame = 0
            self.image = self.frames[self.animations[self.cur_anim][self.cur_frame]]
            self.tick = self.tick + 1
            if self.rect.y > HEIGHT - tile_height:
                self.cur_anim = 'die'
                self.ghost = True
                self.speed_x = 1 * abs(self.speed_x) / max(self.speed_x, 1)
                self.speed_y = -JUMPHEIHT * 0.5
                if self.acceleration_x < 0:
                    self.cur_frame = 1
                else:
                    self.cur_frame = 0
                self.image = self.frames[self.animations[self.cur_anim][self.cur_frame]]
                return
            if self.mode == 'normal':
                if pygame.sprite.spritecollideany(self, enemies_group):
                    if abs(self.rect.x - pygame.sprite.spritecollideany(self, enemies_group).rect.x) > (abs(self.rect.y - pygame.sprite.spritecollideany(self, enemies_group).rect.y) + tile_width) % tile_width + 1:
                        if pygame.sprite.spritecollideany(self, enemies_group):
                            if self.rect.y > pygame.sprite.spritecollideany(self, enemies_group).rect.y - 5 and self.rect.y - pygame.sprite.spritecollideany(self, enemies_group).rect.y < tile_height - 7:
                                self.cur_anim = 'die'
                                self.ghost = True
                                self.speed_x = 0
                                self.speed_y = -JUMPHEIHT * 0.5
                                if self.acceleration_x < 0:
                                    self.cur_frame = 1
                                else:
                                    self.cur_frame = 0
                                self.image = self.frames[self.animations[self.cur_anim][self.cur_frame]]
                                return
                            if pygame.sprite.spritecollideany(self, enemies_group) and self.rect.y < pygame.sprite.spritecollideany(self, enemies_group).rect.y - 5 and self.speed_y >= 0:
                                player.points += pygame.sprite.spritecollideany(self, enemies_group).xp
                                enemies_group.remove_internal(pygame.sprite.spritecollideany(self, enemies_group))
                                self.speed_y = -JUMPHEIHT * 0.5
                        elif pygame.sprite.spritecollideany(self, enemies_group):
                            if self.rect.x > pygame.sprite.spritecollideany(self, enemies_group).rect.x:
                                self.cur_anim = 'die'
                                self.ghost = True
                                self.speed_x = 0
                                self.speed_y = -JUMPHEIHT * 0.5
                                if self.acceleration_x < 0:
                                    self.cur_frame = 1
                                else:
                                    self.cur_frame = 0
                                self.image = self.frames[self.animations[self.cur_anim][self.cur_frame]]
                                return
                            elif self.rect.x < pygame.sprite.spritecollideany(self, enemies_group).rect.x:
                                player.points += pygame.sprite.spritecollideany(self, enemies_group).xp
                                enemies_group.remove_internal(pygame.sprite.spritecollideany(self, enemies_group))
                                self.speed_y = -JUMPHEIHT * 0.5
                    else:
                        if pygame.sprite.spritecollideany(self, enemies_group):
                            if self.rect.y > pygame.sprite.spritecollideany(self, enemies_group).rect.y - 5 and self.rect.y - pygame.sprite.spritecollideany(self, enemies_group).rect.y < tile_height - 7:
                                self.cur_anim = 'die'
                                self.ghost = True
                                self.speed_x = 0
                                self.speed_y = -JUMPHEIHT * 0.5
                                if self.acceleration_x < 0:
                                    self.cur_frame = 1
                                else:
                                    self.cur_frame = 0
                                self.image = self.frames[self.animations[self.cur_anim][self.cur_frame]]
                                return
                            if pygame.sprite.spritecollideany(self, enemies_group) and self.rect.y < pygame.sprite.spritecollideany(
                                self, enemies_group).rect.y - 5 and self.speed_y >= 0:
                                player.points += pygame.sprite.spritecollideany(self, enemies_group).xp
                                enemies_group.remove_internal(pygame.sprite.spritecollideany(self, enemies_group))
                                self.speed_y = -JUMPHEIHT * 0.5
            elif self.mode == 'god':
                if pygame.sprite.spritecollideany(self, enemies_group):
                    if abs(self.rect.x - pygame.sprite.spritecollideany(self, enemies_group).rect.x) > (abs(self.rect.y - pygame.sprite.spritecollideany(self, enemies_group).rect.y) + tile_width) % tile_width + 1:
                        if pygame.sprite.spritecollideany(self, enemies_group):
                            if pygame.sprite.spritecollideany(self, enemies_group) and self.rect.y < pygame.sprite.spritecollideany(self, enemies_group).rect.y - 5 and self.speed_y >= 0:
                                self.speed_y = -JUMPHEIHT * 0.5
                        elif pygame.sprite.spritecollideany(self, enemies_group):
                            if self.rect.x < pygame.sprite.spritecollideany(self, enemies_group).rect.x:
                                self.speed_y = -JUMPHEIHT * 0.5
                    else:
                        if pygame.sprite.spritecollideany(self, enemies_group):
                            if pygame.sprite.spritecollideany(self, enemies_group) and self.rect.y < pygame.sprite.spritecollideany(self, enemies_group).rect.y - 5 and self.speed_y >= 0:
                                self.speed_y = -JUMPHEIHT * 0.5
                    player.points += pygame.sprite.spritecollideany(self, enemies_group).xp
                    enemies_group.remove_internal(pygame.sprite.spritecollideany(self, enemies_group))

            if pygame.sprite.spritecollideany(self, block_group):
                if abs(self.rect.x - pygame.sprite.spritecollideany(self, block_group).rect.x) > (abs(self.rect.y - pygame.sprite.spritecollideany(self, block_group).rect.y) + tile_width) % tile_width + 1:
                    if pygame.sprite.spritecollideany(self, block_group):
                        if self.rect.x > pygame.sprite.spritecollideany(self, block_group).rect.x:
                            self.rect.x = max(self.rect.x, pygame.sprite.spritecollideany(self, block_group).rect.x + tile_width)
                            self.speed_x = 0
                        elif self.rect.x < pygame.sprite.spritecollideany(self, block_group).rect.x:
                            self.rect.x = min(self.rect.x, pygame.sprite.spritecollideany(self, block_group).rect.x - tile_width)
                            self.speed_x = 0
                    if pygame.sprite.spritecollideany(self, block_group):
                        if self.rect.y > pygame.sprite.spritecollideany(self, block_group).rect.y:
                            self.rect.y = max(self.rect.y, pygame.sprite.spritecollideany(self, block_group).rect.y + tile_height + 2)
                            self.speed_y = 0
                        if pygame.sprite.spritecollideany(self, block_group) and self.rect.y < pygame.sprite.spritecollideany(
                            self, block_group).rect.y:
                            self.rect.y = min(self.rect.y, pygame.sprite.spritecollideany(self, block_group).rect.y - tile_height + 2)
                            self.speed_y = 0
                else:
                    if pygame.sprite.spritecollideany(self, block_group):
                        if self.rect.y > pygame.sprite.spritecollideany(self, block_group).rect.y:
                            self.rect.y = max(self.rect.y, pygame.sprite.spritecollideany(self, block_group).rect.y + tile_height + 2)
                            self.speed_y = 0
                        if pygame.sprite.spritecollideany(self, block_group) and self.rect.y < pygame.sprite.spritecollideany(self, block_group).rect.y:
                            self.rect.y = min(self.rect.y, pygame.sprite.spritecollideany(self, block_group).rect.y - tile_height + 2)
                            self.speed_y = 0
            if pygame.sprite.spritecollideany(self, boost_group):
                boost_group.remove_internal(pygame.sprite.spritecollideany(self, boost_group))
                self.mode = 'god'
                self.points += 200
                self.timer = 30000


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        if tile_type == 'brick' or tile_type == 'floor' or tile_type == 'question':
            block_group.add(self)
        self.tile_type = tile_type
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.t = 0

    def update(self):
        if self.t == 1:
            self.rect.y += 5
            self.t = 0
        self.rect.y += 20
        self.rect.x += 10
        if pygame.sprite.spritecollideany(self, player_group):
            obj = pygame.sprite.spritecollideany(self, player_group)
            if self.tile_type != 'empty' and self.rect.y <= obj.rect.y and (obj.speed_y == 1 or obj.speed_y == 0) and obj.cur_anim == 'jump':
                self.rect.y -= 5
                self.t = 1
        self.rect.y -= 20
        self.rect.x -= 10


class Question(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, pos_x, pos_y, surprise):
        super().__init__(tiles_group, all_sprites, block_group)
        self.surprise = surprise
        self.frames = []
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.t = 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(pygame.transform.scale(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)), (tile_width, tile_height)))

    def update(self):
        self.cur_frame += 1
        self.cur_frame %= 30
        self.image = self.frames[self.cur_frame // 10]
        if self.t == 1:
            self.rect.y += 5
            self.t = 0
            block_group.remove_internal(self)
            tiles_group.remove_internal(self)
            all_sprites.remove_internal(self)
            MetalBlock(self.pos_x, self.pos_y)
            if self.surprise == 'star':
                Star(self.pos_x, self.pos_y)
        self.rect.y += 20
        self.rect.x += 10
        if pygame.sprite.spritecollideany(self, player_group):
            obj = pygame.sprite.spritecollideany(self, player_group)
            if self.rect.y <= obj.rect.y and (obj.speed_y == 1 or obj.speed_y == 0) and obj.cur_anim == 'jump':
                self.rect.y -= 5
                self.t = 1
        self.rect.y -= 20
        self.rect.x -= 10


class MetalBlock(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites, tiles_group, block_group)
        self.image = tile_images['metal_block']
        self.rect = self.image.get_rect().move(tile_width * pos_x - camera.x, tile_height * pos_y)


class Camera:
    # зададим начальный сдвиг камеры и размер поля для возможности реализации циклического сдвига
    def __init__(self, field_size):
        self.dx = 0
        self.dy = 0
        self.x = 0
        self.field_size = field_size

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx

    # позиционировать камеру на объекте target
    def update(self, target):
        if self.x < max_width - WIDTH - tile_width:
            self.dx = min(0, -(target.rect.x + target.rect.w // 2 - WIDTH // 2))
            self.x -= self.dx
        else:
            self.dx = 0


class Star(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(boost_group, all_sprites)
        self.image = tile_images['star']
        self.rect = self.image.get_rect().move(tile_width * pos_x - camera.x, tile_height * pos_y)
        self.counter = 10

    def update(self):
        if self.counter > 0:
            self.counter -= 1
            self.rect.y -= 5


class EvilMushroom(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, pos_x, pos_y, xp):
        super().__init__(enemies_group, all_sprites)
        self.acceleration_x = 0
        self.acceleration_y = 1
        self.xp = xp
        self.speed_x = 5
        self.speed_y = JUMPHEIHT + 1
        self.n = 0
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.image = self.frames[0]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.tick = 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(pygame.transform.scale(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)), (tile_width, tile_height)))

    def update(self):
        self.tick += 1
        self.image = self.frames[self.tick // 9]
        self.tick %= 17
        if self.rect.y > HEIGHT - tile_height:
            player.points += self.xp
            enemies_group.remove_internal(self)
        if pygame.sprite.spritecollideany(self, block_group):
            if abs(self.rect.x - pygame.sprite.spritecollideany(self, block_group).rect.x) > (abs(self.rect.y - pygame.sprite.spritecollideany(self, block_group).rect.y) + tile_width) % tile_width:
                if pygame.sprite.spritecollideany(self, block_group):
                    if self.rect.x > pygame.sprite.spritecollideany(self, block_group).rect.x:
                        self.rect.x = max(self.rect.x, pygame.sprite.spritecollideany(self, block_group).rect.x + tile_width + 2)
                        self.speed_x *= -1
                        enemies_group1 = pygame.sprite.Group()
                        for enemy in enemies_group:
                            if not enemy is self:
                                enemies_group1.add(enemy)
                        if pygame.sprite.spritecollideany(self, enemies_group1) and not pygame.sprite.spritecollideany(self, enemies_group1) == self:
                            if abs(self.rect.x - pygame.sprite.spritecollideany(self, enemies_group1).rect.x) > (abs(self.rect.y - pygame.sprite.spritecollideany(self, enemies_group1).rect.y) + tile_width) % tile_width + 1:
                                if pygame.sprite.spritecollideany(self, enemies_group1):
                                    pygame.sprite.spritecollideany(self, enemies_group1).speed_x *= -1
                                    if self.rect.x > pygame.sprite.spritecollideany(self, enemies_group1).rect.x:
                                        self.rect.x = max(self.rect.x, pygame.sprite.spritecollideany(self, enemies_group1).rect.x + tile_width + 2)
                                        self.rect.x = max(self.rect.x, pygame.sprite.spritecollideany(self, enemies_group1).rect.x + tile_width + 2)
                                    elif self.rect.x < pygame.sprite.spritecollideany(self, enemies_group1).rect.x:
                                        self.rect.x = min(self.rect.x, pygame.sprite.spritecollideany(self, enemies_group1).rect.x - tile_width - 2)
                    elif self.rect.x < pygame.sprite.spritecollideany(self, block_group).rect.x:
                        self.rect.x = min(self.rect.x, pygame.sprite.spritecollideany(self, block_group).rect.x - tile_width)
                        self.speed_x *= -1
                        enemies_group1 = pygame.sprite.Group()
                        for enemy in enemies_group:
                            if not enemy is self:
                                enemies_group1.add(enemy)
                        if pygame.sprite.spritecollideany(self, enemies_group1) and not pygame.sprite.spritecollideany(self, enemies_group1) == self:
                            if abs(self.rect.x - pygame.sprite.spritecollideany(self, enemies_group1).rect.x) > (abs(
                                    self.rect.y - pygame.sprite.spritecollideany(self, enemies_group1).rect.y) + tile_width) % tile_width + 1:
                                if pygame.sprite.spritecollideany(self, enemies_group1):
                                    if self.rect.x > pygame.sprite.spritecollideany(self, enemies_group1).rect.x:
                                        pygame.sprite.spritecollideany(self, enemies_group1).speed_x *= -1
                                        self.rect.x = max(self.rect.x, pygame.sprite.spritecollideany(self, enemies_group1).rect.x + tile_width + 2)
                                    elif self.rect.x < pygame.sprite.spritecollideany(self, enemies_group1).rect.x:
                                        self.rect.x = min(self.rect.x, pygame.sprite.spritecollideany(self, enemies_group1).rect.x - tile_width - 2)
                if pygame.sprite.spritecollideany(self, block_group):
                    if self.rect.y > pygame.sprite.spritecollideany(self, block_group).rect.y:
                        self.rect.y = max(self.rect.y, pygame.sprite.spritecollideany(self, block_group).rect.y + tile_height + 2)
                        self.speed_y = 0
                    if pygame.sprite.spritecollideany(self, block_group) and self.rect.y < pygame.sprite.spritecollideany(self, block_group).rect.y:
                        self.rect.y = min(self.rect.y, pygame.sprite.spritecollideany(self, block_group).rect.y - tile_height + 2)
                        self.speed_y = 0
            else:
                if pygame.sprite.spritecollideany(self, block_group):
                    if self.rect.y > pygame.sprite.spritecollideany(self, block_group).rect.y:
                        self.rect.y = max(self.rect.y, pygame.sprite.spritecollideany(self, block_group).rect.y + tile_height + 2)
                        self.speed_y = 0

                    if pygame.sprite.spritecollideany(self, block_group) and self.rect.y < pygame.sprite.spritecollideany(
                        self, block_group).rect.y:
                        self.rect.y = min(self.rect.y, pygame.sprite.spritecollideany(self, block_group).rect.y - tile_height + 2)
                        self.speed_y = 0
        enemies_group1 = pygame.sprite.Group()
        for enemy in enemies_group:
            if not enemy is self:
                enemies_group1.add(enemy)
        if pygame.sprite.spritecollideany(self, enemies_group1) and not pygame.sprite.spritecollideany(self, enemies_group1) == self:
            if abs(self.rect.x - pygame.sprite.spritecollideany(self, enemies_group1).rect.x) > (abs(self.rect.y - pygame.sprite.spritecollideany(self, enemies_group1).rect.y) + tile_width) % tile_width + 1:
                if pygame.sprite.spritecollideany(self, enemies_group1):
                    if self.rect.x > pygame.sprite.spritecollideany(self, enemies_group1).rect.x:
                        pygame.sprite.spritecollideany(self, enemies_group1).speed_x *= -1
                        self.speed_x *= -1
                        self.rect.x = max(self.rect.x, pygame.sprite.spritecollideany(self, enemies_group1).rect.x + tile_width + 2)
                    elif self.rect.x < pygame.sprite.spritecollideany(self, enemies_group1).rect.x:
                        pygame.sprite.spritecollideany(self, enemies_group1).speed_x *= -1
                        self.speed_x *= -1
                        self.rect.x = min(self.rect.x, pygame.sprite.spritecollideany(self, enemies_group1).rect.x - tile_width - 2)

running1 = True

while running1:
    start_screen()
    lives = 3
    points = 0
    n = 1
    try:
        while lives > 0:
            running = True

            screen = pygame.display.set_mode((WIDTH, HEIGHT))
            clock = pygame.time.Clock()

            all_sprites = pygame.sprite.Group()
            tiles_group = pygame.sprite.Group()
            player_group = pygame.sprite.Group()
            block_group = pygame.sprite.Group()
            boost_group = pygame.sprite.Group()
            enemies_group = pygame.sprite.Group()

            level = load_level("level" + str(n) + ".txt")
            player, level_x, level_y = generate_level(level[0])
            max_width = level[1] * tile_width

            camera = Camera((level_x, level_y))

            time = 0
            game_time = 3600000
            fl = False
            life_sign = player.frames[player.animations['stright'][1]]

            lifes = pygame.transform.scale(load_image('lifes.png'), (WIDTH, HEIGHT))
            screen.blit(lifes, (0, 0))
            life_sign_img = pygame.transform.scale(life_sign, (tile_width, tile_height))
            screen.blit(life_sign_img, (WIDTH // 2 - tile_width * 2, HEIGHT // 2 - tile_height - 7))
            kr = pygame.transform.scale(load_image('kr.png'), (tile_width, tile_height))
            screen.blit(kr, (WIDTH // 2 - tile_width, HEIGHT // 2 - tile_height - 7))
            show_num(lives, WIDTH // 2, HEIGHT // 2 - tile_height - 7)
            g = True
            while g:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        terminate()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        g = False  # начинаем игру
                pygame.display.flip()

            fullname = os.path.join('data', 'musicfon.mp3')
            pygame.mixer.music.load(fullname)
            pygame.mixer.music.play()
            player.points = points
            win = True
            while running:
                if not player.ghost:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                            running1 = False
                            lives = 0

                    if pygame.key.get_pressed()[pygame.K_UP] and pygame.sprite.spritecollideany(player, block_group) and player.rect.y == pygame.sprite.spritecollideany(player, block_group).rect.y - tile_height + 2:
                        player.acceleration_y = 1
                        player.speed_y = -JUMPHEIHT
                        player.cur_anim = 'jump'
                        player.rect.y += player.speed_y
                        player.speed_y += player.acceleration_y

                player.rect.y += player.speed_y
                player.speed_y += player.acceleration_y
                player.speed_y = min(player.speed_y, JUMPHEIHT + 1)

                if not player.ghost:
                    if pygame.key.get_pressed()[pygame.K_LEFT]:
                        player.acceleration_x = -1
                        player.speed_x += player.acceleration_x
                        player.speed_x = max(player.speed_x, -MAXSPEED)
                        if player.cur_anim != 'jump':
                            player.cur_anim = 'left'
                    elif pygame.key.get_pressed()[pygame.K_RIGHT]:
                        player.acceleration_x = 1
                        player.speed_x += player.acceleration_x
                        player.speed_x = min(player.speed_x, MAXSPEED)
                        if player.cur_anim != 'jump':
                            player.cur_anim = 'right'
                    elif abs(player.speed_x) > 0:
                        if player.speed_x != 0:
                            if player.speed_x > 0:
                                player.acceleration_x = 1
                            else:
                                player.acceleration_x = -1
                            player.speed_x -= player.acceleration_x
                        if player.cur_anim != 'jump' and player.speed_x == 0:
                            player.cur_anim = 'stright'
                player.rect.x += player.speed_x
                if player.rect.x < 0:
                    player.rect.x = 0
                    player.speed_x = 0
                elif player.rect.x > WIDTH - tile_width:
                    player.rect.x = WIDTH - tile_width
                    player.speed_x = 0
                if player.speed_x == 0 and not player.cur_anim == 'jump':
                    player.cur_anim = 'stright'

                for enemy in enemies_group:
                    enemy.speed_x += enemy.acceleration_x
                    enemy.speed_y += enemy.acceleration_y
                    enemy.rect.x += enemy.speed_x
                    enemy.rect.y += enemy.speed_y

                camera.update(player)

                for sprite in all_sprites:
                    camera.apply(sprite)

                screen.fill(pygame.Color(0, 0, 0))
                all_sprites.update()
                tiles_group.draw(screen)
                enemies_group.draw(screen)
                player_group.draw(screen)
                boost_group.draw(screen)

                next = pygame.transform.scale(load_image('next.png'), (2 * tile_width, 1 * tile_height))
                screen.blit(next, (WIDTH - 100, HEIGHT // 2))

                font = pygame.font.Font(None, 50)
                name = font.render('RARIO', 1, pygame.Color('white'))
                screen.blit(name, (0, 0))
                points1 = str(player.points)
                while len(points1) < 6:
                    points1 = '0' + points1
                points1 = font.render(points1, 1, pygame.Color('white'))
                screen.blit(points1, (0, 30))

                name = font.render('TIME', 1, pygame.Color('white'))
                screen.blit(name, (400, 0))
                time1 = str(int(game_time // 1000))
                while len(time1) < 6:
                    time1 = '0' + time1
                time1 = font.render(time1, 1, pygame.Color('white'))
                screen.blit(time1, (400, 30))

                pygame.display.flip()

                if pygame.sprite.spritecollideany(player, block_group) and player.rect.y == pygame.sprite.spritecollideany(player, block_group).rect.y - tile_height + 2:
                    player.cur_anim = 'stright'

                clock.tick(FPS)
                game_time -= FPS
                game_time = max(0, game_time)
                time += FPS
                if time >= 185000:
                    pygame.mixer.music.play()
                    time = 0

                if player.ghost and not fl or game_time <= 0:
                    fl = True
                    fullname = os.path.join('data', 'mario-die.mp3')
                    pygame.mixer.music.load(fullname)
                    pygame.mixer.music.play()
                    time = 0
                elif player.ghost:
                    if time >= 8000:
                        running = False
                        win = False
                if player.rect.x == WIDTH - tile_width:
                    n += 1
                    win = True
                    break
            if not win:
                lives -= 1
            else:
                points = player.points
            pygame.mixer.music.stop()
    except Exception:
        win_screen()

terminate()
