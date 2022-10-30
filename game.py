import random
import pygame
import math
import os
import sys
from pygame.locals import *

debug = True

width = 600
height = 400
fps = 30


def scale_vector(vector, scale) -> tuple:
    return tuple(i*scale for i in vector)


white = (255, 255, 255)
black = (0,   0,   0)
green = (0, 255,   0)
bg_color = (73, 183, 200)


player_size = (545, 545)
player_center = scale_vector(player_size, .5)
player_radious = 120

scale = 0.3
player_size = scale_vector(player_size, scale)
player_center = scale_vector(player_center, scale)
player_radious *= scale


rock_cooldown = (30, 90)
# Original size: 705x224
rock_size = scale_vector((705, 224), 1/3)


kelp_cooldown = (20, 50)
# Original size: 312x283
kelp_size = scale_vector((312, 283), 1/4)


obstacle_cooldown = (100, 100)

# banana_cooldown = (100, 100)
# Original size and polygon hitbox
banana_size = (1280, 1280)
banana_hitbox = ((410, -1040), (60, -300), (1250, -520))
# Scale down
scale = 0.05
banana_size = scale_vector(banana_size, scale)
banana_hitbox = tuple(scale_vector(i, scale) for i in banana_hitbox)
# Match center
banana_hitbox = tuple(
    (x - banana_size[0]/2, y + banana_size[1]/2) for x, y in banana_hitbox)


# can_cooldown = (100, 100)
# Original size and hitbox
can_size = (636, 1050)
# Scale down
scale = 0.05
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
    return tuple(v1[i] + v2[i] for i in range(len(v1)))


def dist_square(pos1, pos2):
    return (pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2


def check_collision_circle_polygon(center, radious, pos, verticies):
    for i in range(len(verticies)):
        if dist_square(center, add_vector(verticies[i], pos)) < radious**2:
            return True
        x1, y1 = center
        x2, y2 = add_vector(verticies[i-1], pos)
        x3, y3 = add_vector(verticies[i], pos)
        if abs(x1*(y2-y3) - y1*(x2-x3) + x2*y3+x3*y2) < radious * (dist_square(verticies[i-1], verticies[i])**.5):
            return True
    return False


def draw_rect_angle(surf, rect, pivot, angle, color):
    pts = [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft]
    pts = [(pygame.math.Vector2(p) - pivot).rotate(-angle) + pivot for p in pts]
    pygame.draw.lines(surf, color, True, pts, 3)


def render_obstacle(x: float, y: float, type: str):
    rect = imgs[type].get_rect(center=(x, y))
    window.blit(imgs[type], rect)

    if debug:
        if type == 'banana':
            pygame.draw.lines(window, green, True, tuple(
                (x+i[0], y+i[1]) for i in banana_hitbox), 2)
        elif type == 'can':
            pygame.draw.rect(window, green, rect, 2)


def render_player(pos, angle=0):
    rotated_player = pygame.transform.rotate(imgs['player'], angle)
    player_rect = rotated_player.get_rect()
    player_rect.center = pos

    window.blit(rotated_player, player_rect)
    if debug:
        pygame.draw.circle(window, green, pos, player_radious, 2)


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

    # List of list containing 3 items: x, y coordinates and type of the obstacle
    obstacles = []

    max_y = height - player_radious
    min_y = player_radious

    x = 100
    y = height / 2
    vx = 10
    vy = 0

    moveUp = True

    score = 0

    next_obstacle = random.randint(*obstacle_cooldown)
    obstacle_counter = 0

    next_rock = random.randint(*rock_cooldown)
    rock_counter = 0

    next_kelp = random.randint(*kelp_cooldown)
    kelp_counter = 0

    bg_x = 0
    bg_flipped = False
    while True:
        # Spawn objects
        obstacle_counter += 1
        kelp_counter += 1
        rock_counter += 1
        if obstacle_counter == next_obstacle:
            next_obstacle = random.randint(*obstacle_cooldown)
            obstacle_counter = 0
            if random.randint(0, 1):
                obstacles.append([width+banana_size[0]/2, random.randint(
                    banana_size[1]//2, height-banana_size[1]//2), 'banana'])
            else:
                obstacles.append(
                    [width+can_size[0]/2, random.randint(can_size[1]//2, height-can_size[1]//2), 'can'])
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
        for i, obstacle in enumerate(obstacles):
            # Update obstacle
            obstacle[0] -= vx

            # Check collision with player
            if collision_possible:
                if (x + player_radious) < (obstacle[0] - max(banana_size[0], can_size[0]) / 2):
                    collision_possible = False
                    continue
                if obstacle[2] == 'banana':
                    if check_collision_circle_polygon((x, y), player_radious, obstacle[:2], banana_hitbox):
                        score += 1
                        obstacles.pop(i)
                        collision_possible = False
                        continue
                elif obstacle[2] == 'can':
                    if check_collision_circle_rect((x, y), player_radious, obstacle[:2], *can_size):
                        score += 1
                        obstacles.pop(i)
                        collision_possible = False
                        continue

        # Obstacle is out of the screen
        if obstacles and obstacles[0][0] < -(max(can_size[0], banana_size[0]) / 2):
            obstacles.pop(0)

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

        # Render obstacles
        for obstacle in obstacles:
            render_obstacle(*obstacle)

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


def thumbnail():
    window.fill(white)
    window.blit(imgs['bg'], (0, 0))
    window.blit(imgs['rock'], (width / 2, height - rock_size[1]))
    window.blit(imgs['kelp'], (width / 3 - 20, height - kelp_size[1]))
    window.blit(imgs['kelp'], (width / 2 + 40, height - kelp_size[1]))
    window.blit(imgs['can'], (width / 2, height / 3))
    render_player((100, height/2), 10)
    pygame.display.update()
    for i in range(fps * 3):
        clock.tick(fps)


if __name__ == '__main__':
    main()
