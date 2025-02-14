import pygame
import math
from player import Player

map = [[1,2,1,2,1,2,1,2,1,2],
       [2,0,0,0,0,0,0,1,0,1],
       [1,0,1,2,0,2,0,2,0,2],
       [2,0,2,0,0,1,0,1,0,1],
       [1,0,1,2,0,2,0,0,0,2],
       [2,0,0,0,0,1,0,1,2,1],
       [1,2,0,2,0,0,0,0,0,2],
       [2,0,0,1,0,2,2,1,0,1],
       [1,0,0,0,0,0,0,2,0,2],
       [2,1,2,1,2,1,2,1,3,1]]
precision = 30
width = 1280
height = 720

player = Player(1,1,45,0.5)


pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
running = True


def raycast():

    ray_angle = player.angle - player.FOV / 2
    change_angle = player.FOV / width

    for i in range(width):
        rayCos = math.cos(math.radians(ray_angle)) / precision
        raySin = math.sin(math.radians(ray_angle)) / precision

        start = [player.x, player.y]
        end = start.copy()

        color = "red"
        hit_wall = False

        while not hit_wall:
            end[0] += rayCos
            end[1] += raySin

            if map[math.floor(end[1])][math.floor(end[0])] > 0:
                hit_wall = True
                if map[math.floor(end[1])][math.floor(end[0])] == 2:
                    color = "blue"
                elif map[math.floor(end[1])][math.floor(end[0])] == 3:
                    color = "gray"
        a = end[0] - start[0]
        b = end[1] - start[1]
        distance = math.sqrt(a**2 + b**2)
        distance = distance * math.cos(math.radians(ray_angle - player.angle))
        wall_height = height / 2 / distance

        pygame.draw.line(screen, "green", (i, height), (i, (height / 2) - wall_height))
        pygame.draw.line(screen, color, (i, (height / 2) - wall_height), (i, (height / 2) + wall_height))
        pygame.draw.line(screen, "black", (i, (height / 2) - wall_height), (i, 0))
        ray_angle += change_angle

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame

    raycast();


    # RENDER YOUR GAME HERE
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        playerCos = math.cos(math.radians(player.angle)) * player.speed
        playerSin = math.sin(math.radians(player.angle)) * player.speed
        newX = player.x + playerCos
        newY = player.y + playerSin

        if map[math.floor(newY)][math.floor(newX)] == 0:
            player.x = newX
            player.y = newY
    if keys[pygame.K_s]:
        playerCos = math.cos(math.radians(player.angle)) * player.speed
        playerSin = math.sin(math.radians(player.angle)) * player.speed
        newX = player.x - playerCos
        newY = player.y - playerSin

        if map[math.floor(newY)][math.floor(newX)] == 0:
            player.x = newX
            player.y = newY
    if keys[pygame.K_a]:
        player.angle -= 3
    if keys[pygame.K_d]:
        player.angle += 3

    # flip() the display to put your work on screen

    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

    if math.floor(player.x) == 8 and math.floor(player.y) == 8:
        break

pygame.quit()