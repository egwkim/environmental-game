import random
import pygame
import math
import sys
from pygame.locals import *

width = 600
height = 400
fps = 30

white = (255, 255, 255)
black = (0,   0,   0)
green = (0, 255,   0)
bg_color = (73, 183, 200)

player_text = '🤔'

obstacle_text = '💥'
obstacle_cooldown = (15, 30)  # Min, max frames between two obstacles

item_text = '⚡'
item_cooldown = (120, 180)


def main():
    global window, clock, emoji_font, text_font, small_emoji_font, bg_img
    pygame.init()
    window = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    emoji_font = pygame.font.SysFont('Segoe UI Emoji', 50)
    small_emoji_font = pygame.font.SysFont('Segoe UI Emoji', 20)
    text_font = pygame.font.Font(None, 50)
    pygame.display.set_caption('My First Pygame!')
    bg_img = pygame.image.load('assets/background/ocean.png')
    bg_img = pygame.transform.scale(bg_img, (width, height))
    while True:
        load_screen()
        play()
        retry = game_over()
        if not retry:
            break
    quit()


def check_collision(pos1, radious, pos2, width, height):
    # Check collision between a circle and a rectangle.
    x_diff = abs(pos1[0] - pos2[0])
    y_diff = abs(pos1[1] - pos2[1])

    if x_diff > (radious + width/2) or y_diff > (radious + height/2):
        return False

    if x_diff <= width/2 or y_diff <= height/2:
        return True

    return ((x_diff-width/2)**2 + (y_diff-height/2)**2) <= radious


def draw_rect_angle(surf, rect, pivot, angle, color):
    pts = [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft]
    pts = [(pygame.math.Vector2(p) - pivot).rotate(-angle) + pivot for p in pts]
    pygame.draw.lines(surf, color, True, pts, 3)


def render_player(pos, angle=0, small=False, color=black):
    if small:
        player = small_emoji_font.render(player_text, 1, color)
    else:
        player = emoji_font.render(player_text, 1, color)
    player_rect_original = player.get_rect()
    player_rect_original.center = pos
    player = pygame.transform.rotate(player, angle)
    player_rect = player.get_rect()
    player_rect.center = pos

    window.blit(player, player_rect)
    pygame.draw.circle(window, green, pos, player_rect_original.height/2, 2)


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
        window.blit(bg_img, (0, 0))
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
        window.blit(bg_img, (0, 0))

        i += 1
        if i < 25:
            window.blit(text, text_rect)
        elif i == 50:
            i = 0

        render_player((100, height / 2))
        pygame.display.update()
        clock.tick(fps)


def play():
    bg_img_flipped = pygame.transform.flip(bg_img, True, False)

    obstacles = []
    items = []

    obstacle_size = emoji_font.render(obstacle_text, 1, black).get_size()
    item_size = small_emoji_font.render(item_text, 1, black).get_size()

    big_player_radious = emoji_font.render(
        player_text, 1, black).get_height() / 2
    small_player_radious = small_emoji_font.render(
        player_text, 1, black).get_height() / 2
    player_radious = big_player_radious
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
    bg_x = 0
    bg_flipped = False
    while True:
        obstacle_counter += 1
        item_counter += 1
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

        collision_possible = True
        for obstacle in obstacles:
            # Update obstacle
            obstacle[0] -= vx

            # Check collision with player
            if collision_possible:
                if (x + player_radious) < (obstacle[0] - obstacle_size[0] / 2):
                    collision_possible = False
                if check_collision((x, y), player_radious, obstacle, *obstacle_size):
                    return

        # Obstacle is out of the screen
        if obstacles and obstacles[0][0] < -(obstacle_size[0] / 2):
            obstacles.pop(0)

        collision_possible = True
        for i, item in enumerate(items):
            # Update item
            item[0] -= vx

            # Check collision with player
            if collision_possible:
                if (x + player_radious) < (item[0] - item_size[0] / 2):
                    collision_possible = False
                if check_collision((x, y), player_radious, item, *item_size):
                    # Remove item
                    items.pop(i)

                    # Change player size
                    small = not small
                    if small:
                        player_radious = small_player_radious
                    else:
                        player_radious = big_player_radious
                    max_y = height - player_radious
                    min_y = player_radious

        # Item is out of the screen
        if items and items[0][0] < - (item_size[0] / 2):
            items.pop(0)

        # Render screen
        window.fill(white)

        bg_x -= vx
        if bg_flipped:
            window.blit(bg_img_flipped, (bg_x, 0))
            window.blit(bg_img, (width+bg_x, 0))
        else:
            window.blit(bg_img, (bg_x, 0))
            window.blit(bg_img_flipped, (width+bg_x, 0))

        if bg_x <= -width:
            bg_x += width
            bg_flipped ^= 1

        for pos in obstacles:
            render_obstacle(pos)
        for pos in items:
            render_item(pos)
        render_player((x, y), angle, small)

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
