import random
import pygame
import math
import os
import sys
from pygame.locals import *


def scale_vector(vector, scale) -> tuple:
    return tuple(i*scale for i in vector)


width = 600
height = 400
fps = 30

white = (255, 255, 255)
black = (0,   0,   0)
green = (0, 255,   0)
bg_color = (73, 183, 200)

player_text = '🤔'
player_size = (545, 545)
player_center = scale_vector(player_size, .5)
player_radious = 120

scale = 0.3
player_size = scale_vector(player_size, scale)
player_center = scale_vector(player_center, scale)
player_radious *= scale

obstacle_text = '💥'
obstacle_cooldown = (15, 30)  # Min, max frames between two obstacles

item_text = '⚡'
item_cooldown = (120, 180)

rock_cooldown = (30, 90)
# Original size: 705x224
rock_size = scale_vector((705, 224), 1/3)


kelp_cooldown = (20, 50)
# Original size: 312x283
kelp_size = scale_vector((312, 283), 1/4)


banana_cooldown = (100, 100)
# Original size and polygon hitbox
banana_size = (1280, 1280)
banana_hitbox = ((410, -1040), (60, -300), (1250, -520))
# Scale down
scale = 0.2
banana_size = scale_vector(banana_size, 0.2)
banana_hitbox = (scale_vector(i, scale_vector) for i in banana_hitbox)


can_cooldown = (100, 100)
# Original size and hitbox
can_size = (636, 1050)
# Scale down
scale = 0.2
can_size = scale_vector(can_size, scale)


def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def load_img(relative_path):
    return pygame.image.load(resource_path(relative_path))


def main():
    global window, clock, emoji_font, text_font, small_emoji_font, imgs
    # Init game
    pygame.init()
    pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])
    window = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    emoji_font = pygame.font.SysFont('Segoe UI Emoji', 50)
    small_emoji_font = pygame.font.SysFont('Segoe UI Emoji', 20)
    text_font = pygame.font.Font(None, 50)

    pygame.display.set_caption('Save the sea!')

    # Load images
    imgs = {}
    imgs['bg'] = load_img('assets/background/ocean.png').convert()
    imgs['bg'] = pygame.transform.scale(imgs['bg'], (width, height))

    imgs['kelp'] = load_img('assets/background/kelp.png').convert_alpha()
    imgs['kelp'] = pygame.transform.scale(imgs['kelp'], kelp_size)

    imgs['rock'] = load_img('assets/background/rock.png').convert_alpha()
    imgs['rock'] = pygame.transform.scale(imgs['rock'], rock_size)

    imgs['banana'] = load_img('assets/obstacle/banana.png').convert_alpha()
    imgs['banana'] = pygame.transform.scale(imgs['banana'], banana_size)

    imgs['can'] = load_img('assets/obstacle/can.png').convert_alpha()
    imgs['can'] = pygame.transform.scale(imgs['can'], can_size)

    imgs['player'] = load_img('assets/player.png').convert_alpha()
    imgs['player'] = pygame.transform.scale(imgs['player'], player_size)

    # Play game
    while True:
        load_screen()
        play()
        retry = game_over()
        if not retry:
            break
    quit()


def check_collision_circle_rect(center, radious, pos, width, height):
    # Check collision between a circle and a rectangle.
    x_diff = abs(center[0] - pos[0])
    y_diff = abs(center[1] - pos[1])

    if x_diff > (radious + width/2) or y_diff > (radious + height/2):
        return False

    if x_diff <= width/2 or y_diff <= height/2:
        return True

    return ((x_diff-width/2)**2 + (y_diff-height/2)**2) <= radious**2


def add_vector(v1, v2):
    return (v1[i] + v2[i] for i in range(len(v1)))


def dist_square(pos1, pos2):
    return (pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2


def check_collision_circle_polygon(center, radious, pos, verticies):
    for i in len(verticies):
        if dist_square(center, add_vector(verticies[i], pos)) < radious**2:
            return True
        x1, y1 = center
        x2, y2 = add_vector(verticies[i-1], pos)
        x3, y3 = add_vector(verticies[i], pos)
        if math.abs(x1*(y2-y3) - y1*(x2-x3) + x2*y3+x3*y2) < radious * (dist_square(verticies[i-1], verticies[i])**.5):
            return True
    return False


def draw_rect_angle(surf, rect, pivot, angle, color):
    pts = [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft]
    pts = [(pygame.math.Vector2(p) - pivot).rotate(-angle) + pivot for p in pts]
    pygame.draw.lines(surf, color, True, pts, 3)


def render_player(pos, angle=0):
    rotated_player = pygame.transform.rotate(imgs['player'], angle)
    player_rect = rotated_player.get_rect()
    player_rect.center = pos

    window.blit(rotated_player, player_rect)
    pygame.draw.circle(window, green, pos, player_radious, 2)


def render_obstacle(pos, color=black):
    obstacle = emoji_font.render(obstacle_text, 1, color)
    obstacle_rect = obstacle.get_rect()
    obstacle_rect.center = pos

    window.blit(obstacle, obstacle_rect)
    draw_rect_angle(window, obstacle_rect, pos, 0, green)


def render_item(pos, color=black):
    item = small_emoji_font.render(item_text, 1, color)
    item_rect = item.get_rect()
    item_rect.center = pos

    window.blit(item, item_rect)
    draw_rect_angle(window, item_rect, pos, 0, green)


def load_screen():
    for i in range(0, 101, 10):
        for event in pygame.event.get():
            if event.type == QUIT:
                quit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    quit()
        window.fill(white)
        window.blit(imgs['bg'], (0, 0))
        render_player((i, height / 2))
        pygame.display.update()
        clock.tick(fps)
    i = 0
    text = text_font.render(f'Press space to start!', 1, black)
    text_rect = text.get_rect()
    text_rect.center = (width/2, 90)
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                quit()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    return
                if event.key == K_ESCAPE:
                    quit()
        window.fill(white)
        window.blit(imgs['bg'], (0, 0))

        i += 1
        if i < 25:
            window.blit(text, text_rect)
        elif i == 50:
            i = 0

        render_player((100, height / 2))
        pygame.display.update()
        clock.tick(fps)


def play():
    imgs['bg_flipped'] = pygame.transform.flip(imgs['bg'], True, False)
    bg_objects = []

    obstacles = []
    items = []

    obstacle_size = emoji_font.render(obstacle_text, 1, black).get_size()
    item_size = small_emoji_font.render(item_text, 1, black).get_size()

    max_y = height - player_radious
    min_y = player_radious

    x = 100
    y = height / 2
    vx = 10
    vy = 0

    moveUp = True
    small = False

    next_obstacle = random.randint(*obstacle_cooldown)
    obstacle_counter = 0

    next_item = random.randint(*item_cooldown)
    item_counter = 0

    next_rock = random.randint(*rock_cooldown)
    rock_counter = 0

    next_kelp = random.randint(*kelp_cooldown)
    kelp_counter = 0

    bg_x = 0
    bg_flipped = False
    while True:
        # Spawn objects
        obstacle_counter += 1
        item_counter += 1
        kelp_counter += 1
        rock_counter += 1
        if obstacle_counter == next_obstacle:
            next_obstacle = random.randint(*obstacle_cooldown)
            obstacle_counter = 0
            obstacles.append(
                [width+obstacle_size[0]/2, random.randint(obstacle_size[1]//2, height-obstacle_size[1]//2)])
        if item_counter == next_item:
            next_item = random.randint(*item_cooldown)
            item_counter = 0
            items.append(
                [width+item_size[0]/2, random.randint(item_size[1]//2, height-item_size[1]//2)])
        if rock_counter == next_rock:
            next_rock = random.randint(*rock_cooldown)
            rock_counter = 0
            bg_objects.append(
                ([width, height - rock_size[1]], imgs['rock']))
        if kelp_counter == next_kelp:
            next_kelp = random.randint(*kelp_cooldown)
            kelp_counter = 0
            bg_objects.append(
                ([width, height - kelp_size[1]], imgs['kelp']))

        # Check events
        for event in pygame.event.get():
            if event.type == QUIT:
                quit()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    moveUp = True
            elif event.type == KEYUP:
                if event.key == K_SPACE:
                    moveUp = False
                elif event.key == K_ESCAPE:
                    quit()

        # Move character
        if moveUp:
            vy += 1
        else:
            vy -= 1

        angle = math.degrees(math.atan(vy/vx))
        y -= vy

        if y > max_y:  # Collides on ceiling
            y = max_y
            if angle < 0:
                angle = 0
                vy = 0
        if y < min_y:  # Collides on floor
            y = min_y
            if angle > 0:
                angle = 0
                vy = 0

        # Update background objects
        for pos, obj in bg_objects:
            pos[0] -= vx
        if bg_objects and bg_objects[0][0][0] < - max(rock_size[0], kelp_size[0]):
            bg_objects.pop(0)

        # Update obstacles and check collision
        collision_possible = True
        for obstacle in obstacles:
            # Update obstacle
            obstacle[0] -= vx

            # Check collision with player
            if collision_possible:
                if (x + player_radious) < (obstacle[0] - obstacle_size[0] / 2):
                    collision_possible = False
                    continue
                if check_collision_circle_rect((x, y), player_radious, obstacle, *obstacle_size):
                    return

        # Obstacle is out of the screen
        if obstacles and obstacles[0][0] < -(obstacle_size[0] / 2):
            obstacles.pop(0)

        # Update items and check collision
        collision_possible = True
        for i, item in enumerate(items):
            # Update item
            item[0] -= vx

            # Check collision with player
            if collision_possible:
                if (x + player_radious) < (item[0] - item_size[0] / 2):
                    collision_possible = False
                    continue
                if check_collision_circle_rect((x, y), player_radious, item, *item_size):
                    # Remove item
                    items.pop(i)

        # Item is out of the screen
        if items and items[0][0] < - (item_size[0] / 2):
            items.pop(0)

        # Render screen
        # Reset window
        window.fill(white)

        # Render background
        bg_x -= vx
        if bg_flipped:
            window.blit(imgs['bg_flipped'], (bg_x, 0))
            window.blit(imgs['bg'], (width+bg_x, 0))
        else:
            window.blit(imgs['bg'], (bg_x, 0))
            window.blit(imgs['bg_flipped'], (width+bg_x, 0))

        if bg_x <= -width:
            bg_x += width
            bg_flipped ^= 1

        # Render background objects
        for pos, obj in bg_objects:
            window.blit(obj, pos)

        # Render obstacles and items
        for pos in obstacles:
            render_obstacle(pos)
        for pos in items:
            render_item(pos)

        # Render player
        render_player((x, y), angle)

        pygame.display.update()
        clock.tick(fps)


def game_over():
    text = text_font.render('Game over', 1, black)
    rect = text.get_rect()
    rect.center = (width/2, height/2)
    window.fill(bg_color)
    window.blit(text, rect)
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                quit()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    # Retry
                    return True
                elif event.key == K_ESCAPE:
                    # Quit
                    return False
        clock.tick(fps)


def quit():
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
