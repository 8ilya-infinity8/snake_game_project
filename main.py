import os
import sys
import datetime
import time
import csv
from random import randrange, choice

import pygame

FPS = 60
GRAVITY = 0.25


def terminate():
    # функция закрытия игры
    file.close()
    pygame.quit()
    sys.exit()


def start_screen():
    # создание главного меню
    global file, writer, reader, max_score
    fon = load_image('menu.png')
    screen.blit(fon, (0, 0))
    buttons = pygame.sprite.Group()
    play_b = Button(buttons, 'play_button.png', 149, 203)
    score_b = Button(buttons, 'score_button.png', 149, 305)
    close_b = Button(buttons, 'close_button.png', 149, 407)
    play_b.func = game
    score_b.func = scores_screen
    close_b.func = terminate

    file = open('scores.csv', 'r')
    reader = list(csv.reader(file, delimiter=';', quotechar='"'))[-1:-10:-1]
    try:
        max_score = int(reader[0][1])
    except ValueError:
        max_score = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEMOTION:
                for button in buttons:
                    button.press(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button.is_focused(event.pos):
                        if button.func == game:
                            file.close()
                            file = open('scores.csv', 'a', newline='')
                            writer = csv.writer(file, delimiter=';',
                                                quotechar='"')
                        return button.activate()

        buttons.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def scores_screen():
    # создание и вывод таблицы достижений на экран
    fon = pygame.Surface((width, height))
    fon.fill('#91c634')
    buttons = pygame.sprite.Group()
    back_b = Button(buttons, 'menu_button.png', 60, 500)
    back_b.func = start_screen

    font = pygame.font.SysFont('MV Boli', 25)
    title = 'date' + (' ' * 13) + 'score' + (' ' * 7) + 'time'
    string_rendered = font.render(title, 1, (0, 100, 0))
    intro_rect = string_rendered.get_rect().move(40, 5)
    fon.blit(string_rendered, intro_rect)
    text_coord = 30
    if reader[-1][0] == 'date':
        del reader[-1]
    for line in reader:
        line = (' ' * 7).join(line)
        string_rendered = font.render(line, 1, (0, 100, 0))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 15
        text_coord += intro_rect.height
        fon.blit(string_rendered, intro_rect)
    screen.blit(fon, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEMOTION:
                back_b.press(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_b.is_focused(event.pos):
                    file.close()
                    return back_b.activate()

        buttons.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def game_over_screen():
    # экран проигрыша
    global max_score
    counter_res, timer_res = counter.result(), timer.result()
    color = (0, 100, 0)
    flag = False
    if int(counter_res) > max_score:
        now = datetime.datetime.now()
        writer.writerow([now.strftime("%d-%m-%Y"), counter_res, timer_res])
        max_score = int(counter_res)
        color = (150, 0, 0)
        flag = True

    gameover = Gameover(counter_res, timer_res, color)
    all_sprites.change_layer(gameover, 1)
    all_sprites.change_layer(gameover.restart, 1)
    all_sprites.change_layer(gameover.menu, 1)

    if flag:
        x, y, w, h = gameover.rect
        create_particles((x + w // 2 - 8, y))
    while True:
        screen.fill('#a2ed5d')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if gameover.is_focused(event.pos, 1):
                    gameover.killl()
                    return game()
                elif gameover.is_focused(event.pos, 0):
                    gameover.killl()
                    file.close()
                    return start_screen()
            elif event.type == pygame.MOUSEMOTION:
                gameover.press(event.pos)
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def paused():
    # остановка экарна
    timer.stop()
    while True:
        screen.fill('#a2ed5d')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pause.rect.collidepoint(event.pos):
                    return timer.resume()


def load_image(name, colorkey=None):
    # функция для загрузки изображений
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def create_particles(position):
    # создание частиц
    count = 70
    for _ in range(count):
        Particle(position, randrange(-4, 5), randrange(-7, 3))


class Particle(pygame.sprite.Sprite):
    # частицы, появляющиеся при достижении нового рекорда
    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.image = choice(fire)
        self.rect = self.image.get_rect()

        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos

        # гравитация будет неизменной
        self.gravity = GRAVITY
        all_sprites.change_layer(self, 1)

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect((0, 0, width, height)):
            self.kill()


class Button(pygame.sprite.Sprite):
    # кнопки главного меню
    def __init__(self, group, pic, x, y):
        super().__init__(group)
        pic2 = '_2.'.join(pic.split('.'))
        self.images = (load_image(pic), load_image(pic2))
        self.image = self.images[0]
        self.rect = self.image.get_rect().move(x, y)
        self.func = lambda: None

    def is_focused(self, pos):
        return self.rect.collidepoint(pos)

    def press(self, pos):
        self.image = self.images[self.is_focused(pos)]

    def activate(self):
        return self.func()


class Gameover(pygame.sprite.Sprite):
    # окно проигрыша
    def __init__(self, score, timing, color=(0, 100, 0)):
        super().__init__(all_sprites)
        self.images1 = load_image('restart.png'),\
            load_image('restart_down.png')
        self.images2 = load_image('return.png'),\
            load_image('return_down.png')
        self.image = load_image('gameover.png')
        self.restart = pygame.sprite.Sprite(all_sprites)
        self.menu = pygame.sprite.Sprite(all_sprites)
        self.restart.image = self.images1[0]
        self.menu.image = self.images2[0]
        self.rect = self.image.get_rect().move(70, 100)
        self.restart.rect = self.restart.image.get_rect().move(190, 260)
        self.menu.rect = self.menu.image.get_rect().move(304, 286)
        result = ('Score      Time', f'{score}      {timing}')
        font = pygame.font.SysFont('MV Boli', 35)
        str1_rend = font.render(result[0], True, (0, 100, 0))
        str1_rect = str1_rend.get_rect().move(30, 82)
        self.image.blit(str1_rend, str1_rect)
        str2_rend = font.render(result[1], True, color)
        str2_rect = str1_rend.get_rect().move(34, 122)
        self.image.blit(str2_rend, str2_rect)

    def is_focused(self, pos, x):
        if x:
            return self.restart.rect.collidepoint(pos)
        return self.menu.rect.collidepoint(pos)

    def press(self, pos):
        self.restart.image = self.images1[self.is_focused(pos, 1)]
        self.menu.image = self.images2[self.is_focused(pos, 0)]

    def killl(self):
        self.restart.kill()
        self.kill()


class Pause(pygame.sprite.Sprite):
    # окно паузы
    def __init__(self):
        super().__init__(all_sprites)
        self.images = load_image('stop.png'),\
            load_image('stop_down.png')
        self.image = self.images[0]
        self.rect = self.image.get_rect().move(215, 485)

    def up(self):
        self.image = self.images[0]

    def down(self):
        self.image = self.images[1]


class Timer:
    # объект, подсчитывающий игровое время
    def __init__(self):
        self.total = 0
        self.started = time.time()
        self.font = pygame.font.SysFont('MV Boli', 30)
        string_rend = self.font.render('00:00', True, (0, 100, 0))
        self.string_rect = string_rend.get_rect().move(60, 484)
        screen.blit(string_rend, self.string_rect)

    def result(self):
        total = self.total + (time.time() - self.started)
        return '{:0>2}:{:0>2}'.format(str(int(total // 60)),
                                      str(int(total % 60)))

    def show(self):
        string_rend = self.font.render(self.result(), True, (0, 100, 0))
        screen.blit(string_rend, self.string_rect)

    def start(self):
        self.started = time.time()

    def stop(self):
        self.total += time.time() - self.started

    def resume(self):
        self.started = time.time()


class Counter:
    # объект, подсчитывающий игровой счёт
    def __init__(self):
        self.score = 0
        self.font = pygame.font.SysFont('MV Boli', 30)
        string_rend = self.font.render('000', True, (0, 100, 0))
        self.string_rect = string_rend.get_rect().move(340, 484)
        screen.blit(string_rend, self.string_rect)

    def result(self):
        return '{:0>3}'.format(str(self.score))

    def increase(self, points):
        self.score += points

    def show(self):
        string_rend = self.font.render(self.result(), True, (0, 100, 0))
        screen.blit(string_rend, self.string_rect)

    def reset(self):
        self.score = 0


class Tile(pygame.sprite.Sprite):
    # плитка поля
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites)
        image = pygame.Surface((tile_width, tile_height))
        image.fill((154, 205, 50))
        pygame.draw.rect(image, '#b2ec5d', (2, 2, 36, 36))
        self.image = image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    # сам игрок
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        poses = tile_width * pos_x + 5, tile_height * pos_y + 5
        image = load_image('head.png')
        self.image = image
        self.rect = self.image.get_rect().move(poses[0], poses[1])
        snake_group.add(self)
        self.x, self.y = 0, 1
        self.xx, self.yy = 0, 1
        self.angle = 180
        self.turning = 0
        self.flag = False
        self.full = 0

        self.pieces = [Body(poses[0], i, 0) for i in
                       range(poses[1], poses[1] - 61, -4)]

    def move(self):
        x, y = self.rect.x, self.rect.y
        conds = (self.x == -1 and not (x - 5) % tile_width,
                 self.x == 1 and not (x + 35) % tile_width,
                 self.y == -1 and not (y - 5) % tile_height,
                 self.y == 1 and not (y + 35) % tile_height)
        if any(conds) and self.flag:
            self.image = pygame.transform.rotate(self.image, self.turning)
            self.x = self.xx
            self.y = self.yy
            self.flag = False
        self.rect = self.rect.move(self.x * 4, self.y * 4)
        piece = self.pieces[0].rect
        self.pieces.insert(0, Body(piece[0] + self.x * 4,
                                   piece[1] + self.y * 4, 0))
        self.pieces[15].change()
        if self.full:
            self.full -= 1
        else:
            self.pieces[-1].kill()
            del self.pieces[-1]
        if pygame.sprite.spritecollideany(self, food_group):
            self.full += 10
            food.move()
            counter.increase(1)
        all_sprites.change_layer(self, 1)
        if not 0 < x < 449 or not 0 < y < 449\
                or pygame.sprite.spritecollideany(self, body_group):
            game_over_screen()

    def turn(self, side):
        angles = {(-1, 0): 270, (1, 0): 90, (0, -1): 0, (0, 1): 180}
        save = self.xx, self.yy
        self.xx, self.yy = 0, 0
        if side == pygame.K_LEFT:
            self.xx = -1
        if side == pygame.K_RIGHT:
            self.xx = 1
        if side == pygame.K_UP:
            self.yy = -1
        if side == pygame.K_DOWN:
            self.yy = 1
        if any((self.x == -self.xx, self.y == -self.yy,
                self.x == self.xx, self.y == self.yy)):
            self.xx, self.yy = save
            return
        self.turning = self.angle - angles[(self.xx, self.yy)]
        self.angle = angles[(self.xx, self.yy)]
        self.flag = True


class Body(pygame.sprite.Sprite):
    # часть туловища змеи
    def __init__(self, pos_x, pos_y, flag):
        super().__init__(all_sprites)
        image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(image, (57, 150, 39), (15, 15), 15)
        self.image = image
        self.rect = self.image.get_rect().move(
            pos_x, pos_y)
        snake_group.add(self)
        if flag:
            body_group.add(self)

    def change(self):
        body_group.add(self)

    def __repr__(self):
        return f'Body({self.rect.x, self.rect.y})'


class Food(pygame.sprite.Sprite):
    # объект еды
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites, food_group)
        image = load_image('apple.png', -1)
        self.image = image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 5, tile_height * pos_y + 5)
        self.move()

    def move(self):
        flag = True
        for _ in range(10):
            self.rect.x = randrange(12) * tile_width + 5
            self.rect.y = randrange(12) * tile_height + 5
            if not pygame.sprite.spritecollideany(self, snake_group):
                flag = False
                break
        if flag:
            for x in range(12):
                for y in range(12):
                    self.rect.x = randrange(12) * tile_width + 5
                    self.rect.y = randrange(12) * tile_height + 5
                    if not pygame.sprite.spritecollideany(self, snake_group):
                        break


def generate_level():
    # функция генерации поля
    x, y = None, None
    for y in range(12):
        for x in range(12):
            Tile(x, y)
    new_player = Player(5, 5)
    new_food = Food(1, 1)
    return new_player, new_food, x, y


def game():
    # главная функция самой игры
    global player, food, level_x, level_y, pause, file

    for item in all_sprites:
        item.kill()
    player, food, level_x, level_y = generate_level()
    pause = Pause()
    timer.start()
    counter.reset()
    while True:
        screen.fill('#a2ed5d')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                side = event.key
                player.turn(side)
            elif event.type == pygame.MOUSEMOTION:
                if pause.rect.collidepoint(event.pos):
                    pause.down()
                else:
                    pause.up()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pause.rect.collidepoint(event.pos):
                    paused()

        player.move()
        timer.show()
        counter.show()

        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


pygame.font.init()
size = width, height = 480, 540
screen = pygame.display.set_mode(size)
pygame.display.set_caption('змейка')
tile_width = tile_height = 40
clock = pygame.time.Clock()

all_sprites = pygame.sprite.LayeredUpdates()
body_group = pygame.sprite.Group()
food_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
snake_group = pygame.sprite.Group()

fire = [load_image('star.png'), load_image('medal.png')]
for ind in range(2):
    for scale in range(10, 26, 5):
        fire.append(pygame.transform.scale(fire[ind], (scale, scale)))
player, food, level_x, level_y = None, None, None, None
timer = Timer()
counter = Counter()
pause = None
file, writer, reader = None, None, None
max_score = 0

start_screen()
