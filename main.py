import math
import random
from collections.abc import Sequence

import pygame

from player import Player

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 600
RENDER_SCALE = 1
TEXTURE_SIZE = 64
TEXTURE_SMOOTHING = 4
PLAYER_RADIUS = 0.2
FLASHLIGHT_RANGE = 8.0
MAZE_WIDTH = 21
MAZE_HEIGHT = 21
EXIT_TILE = "E"

SKY_COLOR = (38, 43, 66)
FLOOR_COLOR = (48, 43, 39)


def generate_maze(
    width: int = MAZE_WIDTH,
    height: int = MAZE_HEIGHT,
) -> tuple[tuple[str, ...], tuple[int, int]]:
    if width < 5 or height < 5 or width % 2 == 0 or height % 2 == 0:
        raise ValueError("Maze dimensions must be odd integers of at least 5.")

    maze = [["1"] * width for _ in range(height)]
    start = (1, 1)
    maze[start[1]][start[0]] = "0"
    stack = [start]

    while stack:
        x, y = stack[-1]
        neighbors = [
            (x + dx, y + dy)
            for dx, dy in ((0, -2), (2, 0), (0, 2), (-2, 0))
            if 1 <= x + dx < width - 1
            and 1 <= y + dy < height - 1
            and maze[y + dy][x + dx] == "1"
        ]
        if not neighbors:
            stack.pop()
            continue

        next_x, next_y = random.choice(neighbors)
        maze[(y + next_y) // 2][(x + next_x) // 2] = "0"
        maze[next_y][next_x] = "0"
        stack.append((next_x, next_y))

    exit_position = (width - 2, height - 2)
    maze[exit_position[1]][exit_position[0]] = EXIT_TILE
    return tuple("".join(row) for row in maze), exit_position


def cast_ray(
    world_map: Sequence[str],
    position: tuple[float, float],
    ray_direction: tuple[float, float],
) -> tuple[float, int, int, int]:
    """Return perpendicular distance, wall side, material, and texture column."""
    map_x, map_y = int(position[0]), int(position[1])
    ray_x, ray_y = ray_direction

    delta_x = abs(1.0 / ray_x) if ray_x != 0 else math.inf
    delta_y = abs(1.0 / ray_y) if ray_y != 0 else math.inf

    if ray_x < 0:
        step_x = -1
        side_x = (position[0] - map_x) * delta_x
    else:
        step_x = 1
        side_x = (map_x + 1.0 - position[0]) * delta_x

    if ray_y < 0:
        step_y = -1
        side_y = (position[1] - map_y) * delta_y
    else:
        step_y = 1
        side_y = (map_y + 1.0 - position[1]) * delta_y

    side = 0
    while 0 <= map_y < len(world_map) and 0 <= map_x < len(world_map[map_y]):
        tile = world_map[map_y][map_x]
        if tile in ("1", EXIT_TILE):
            if side == 0:
                distance = side_x - delta_x
                wall_position = position[1] + distance * ray_y
            else:
                distance = side_y - delta_y
                wall_position = position[0] + distance * ray_x
            texture_x = int(
                (wall_position - math.floor(wall_position))
                * TEXTURE_SIZE
                * TEXTURE_SMOOTHING
            )
            if (side == 0 and ray_x > 0) or (side == 1 and ray_y < 0):
                texture_x = TEXTURE_SIZE * TEXTURE_SMOOTHING - texture_x - 1
            material = 4 if tile == EXIT_TILE else (map_x + 2 * map_y) % 4
            return max(distance, 1e-6), side, material, texture_x

        if side_x < side_y:
            side_x += delta_x
            map_x += step_x
            side = 0
        else:
            side_y += delta_y
            map_y += step_y
            side = 1

    raise ValueError("Ray left the map without hitting a wall; enclose the map in walls.")


def create_wall_textures() -> tuple[pygame.Surface, ...]:
    textures = []

    brick = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    brick.fill((91, 43, 37))
    for row in range(4):
        offset = 16 if row % 2 else 0
        for column in range(-1, 4):
            x = column * 32 + offset
            y = row * 16
            shade = 12 * ((row + column) % 3)
            color = (142 + shade, 66 + shade // 2, 48 + shade // 3)
            pygame.draw.rect(brick, color, (x + 1, y + 1, 30, 14))
            pygame.draw.line(brick, (177 + shade, 91 + shade // 2, 66), (x + 2, y + 2), (x + 29, y + 2))
    textures.append(brick)

    metal = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    metal.fill((35, 52, 60))
    for row in range(2):
        for column in range(2):
            x, y = column * 32 + 2, row * 32 + 2
            panel = (58 + row * 10, 83 + column * 8, 91 + row * 6)
            pygame.draw.rect(metal, (25, 39, 45), (x, y, 29, 29))
            pygame.draw.rect(metal, panel, (x + 2, y + 2, 25, 25))
            pygame.draw.line(metal, (112, 141, 145), (x + 3, y + 3), (x + 24, y + 3))
            pygame.draw.line(metal, (30, 45, 51), (x + 3, y + 25), (x + 24, y + 25))
            for rivet_x, rivet_y in ((x + 5, y + 5), (x + 24, y + 5), (x + 5, y + 24), (x + 24, y + 24)):
                pygame.draw.circle(metal, (157, 173, 162), (rivet_x, rivet_y), 1)
    pygame.draw.line(metal, (39, 176, 173), (31, 0), (31, 63), 2)
    textures.append(metal)

    stone = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    stone.fill((57, 53, 48))
    for row in range(4):
        offset = 16 if row % 2 else 0
        for column in range(-1, 4):
            x, y = column * 32 + offset, row * 16
            shade = (row * 13 + column * 9) % 27
            color = (105 + shade, 98 + shade, 83 + shade)
            points = (
                (x + 1, y + 1),
                (x + 29, y + 1),
                (x + 31, y + 5),
                (x + 28, y + 14),
                (x + 2, y + 14),
            )
            pygame.draw.polygon(stone, color, points)
            pygame.draw.line(stone, (139 + shade, 131 + shade, 112 + shade), points[0], points[1])
    textures.append(stone)

    hazard = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    hazard.fill((39, 43, 44))
    for offset in range(-TEXTURE_SIZE, TEXTURE_SIZE * 2, 16):
        pygame.draw.polygon(
            hazard,
            (192, 135, 42),
            ((offset, 0), (offset + 8, 0), (offset - 24, TEXTURE_SIZE), (offset - 32, TEXTURE_SIZE)),
        )
    pygame.draw.rect(hazard, (33, 42, 45), (8, 16, 48, 32))
    pygame.draw.rect(hazard, (111, 123, 117), (11, 19, 42, 26), 2)
    pygame.draw.line(hazard, (193, 157, 79), (14, 24), (50, 24), 2)
    pygame.draw.line(hazard, (193, 157, 79), (14, 40), (50, 40), 2)
    textures.append(hazard)

    exit_portal = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    exit_portal.fill((18, 24, 24))
    pygame.draw.rect(exit_portal, (49, 65, 54), (8, 4, 48, 60))
    pygame.draw.rect(exit_portal, (125, 139, 100), (12, 8, 40, 56), 3)
    pygame.draw.rect(exit_portal, (26, 35, 31), (17, 14, 30, 50))
    pygame.draw.line(exit_portal, (93, 156, 102), (21, 17), (21, 60), 2)
    pygame.draw.line(exit_portal, (93, 156, 102), (42, 17), (42, 60), 2)
    pygame.draw.line(exit_portal, (179, 198, 130), (23, 18), (40, 18), 2)
    exit_label = pygame.font.Font(None, 14).render("EXIT", True, (213, 221, 157))
    exit_portal.blit(exit_label, exit_label.get_rect(center=(32, 6)))
    textures.append(exit_portal)

    return tuple(
        pygame.transform.smoothscale(
            texture,
            (TEXTURE_SIZE * TEXTURE_SMOOTHING, TEXTURE_SIZE),
        )
        for texture in textures
    )


def create_flashlight_mask(size: tuple[int, int]) -> pygame.Surface:
    width, height = size
    mask = pygame.Surface(size)
    center_x = width / 2
    center_y = height * 0.62
    radius_x = width * 0.46
    radius_y = height * 0.7

    for y in range(height):
        for x in range(width):
            dx = (x - center_x) / radius_x
            dy = (y - center_y) / radius_y
            radius = math.hypot(dx, dy)
            fade = max(0.0, min(1.0, (1.0 - radius) / 0.4))
            intensity = fade * fade * (3.0 - 2.0 * fade)
            value = round(intensity * 255)
            mask.set_at((x, y), (value, value, value))

    return mask


def draw_flashlight(screen: pygame.Surface) -> None:
    width, height = screen.get_size()
    scale = min(width / SCREEN_WIDTH, height / SCREEN_HEIGHT)
    x, y = width * 0.78, height * 0.9
    flashlight = [
        (x, y + 10 * scale),
        (x + 62 * scale, y - 12 * scale),
        (x + 77 * scale, y + 2 * scale),
        (x + 18 * scale, y + 39 * scale),
    ]
    pygame.draw.polygon(screen, (24, 27, 30), flashlight)
    pygame.draw.polygon(screen, (95, 99, 91), flashlight, max(1, round(2 * scale)))
    pygame.draw.polygon(
        screen,
        (188, 174, 125),
        (
            (x + 66 * scale, y - 13 * scale),
            (x + 81 * scale, y - 7 * scale),
            (x + 84 * scale, y + 1 * scale),
            (x + 74 * scale, y + 6 * scale),
        ),
    )
    pygame.draw.polygon(
        screen,
        (74, 50, 47),
        (
            (x - 15 * scale, y + 31 * scale),
            (x + 18 * scale, y + 21 * scale),
            (x + 39 * scale, y + 55 * scale),
            (x + 16 * scale, height + 5 * scale),
            (x - 20 * scale, height + 5 * scale),
        ),
    )


def flashlight_falloff(distance: float) -> float:
    fade = max(0.0, min(1.0, (FLASHLIGHT_RANGE - distance) / (FLASHLIGHT_RANGE * 0.4)))
    return fade * fade * (3.0 - 2.0 * fade)


def draw_escape_screen(screen: pygame.Surface) -> None:
    screen.fill((5, 7, 8))
    title_font = pygame.font.Font(None, 76)
    prompt_font = pygame.font.Font(None, 32)
    title = title_font.render("YOU ESCAPED", True, (177, 199, 159))
    prompt = prompt_font.render("Press R to enter another maze  |  Esc to quit", True, (120, 133, 122))
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 35)))
    screen.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)))


def flashlight_color(color: tuple[int, int, int], distance: float) -> tuple[int, int, int]:
    brightness = flashlight_falloff(distance)
    return tuple(round(channel * brightness) for channel in color)


def render_scene(
    screen: pygame.Surface,
    player: Player,
    world_map: Sequence[str],
    textures: Sequence[pygame.Surface],
    flashlight_mask: pygame.Surface,
) -> None:
    width, height = screen.get_size()
    horizon = height // 2
    for y in range(height):
        if y < horizon:
            distance = height * 0.75 / (horizon - y)
            color = flashlight_color(SKY_COLOR, distance)
        else:
            distance = height * 0.25 / (y - horizon) if y > horizon else math.inf
            color = flashlight_color(FLOOR_COLOR, distance)
        screen.fill(color, (0, y, width, 1))

    direction_x = math.cos(player.angle)
    direction_y = math.sin(player.angle)
    plane_x, plane_y = player.camera_plane

    for column in range(width):
        camera_x = 2.0 * column / width - 1.0
        ray_x = direction_x + plane_x * camera_x
        ray_y = direction_y + plane_y * camera_x
        distance, side, material, texture_x = cast_ray(
            world_map,
            (player.x, player.y),
            (ray_x, ray_y),
        )

        wall_height = max(1, int(height / distance))
        projected_top = horizon - wall_height // 2
        top = max(0, projected_top)
        bottom = min(height, projected_top + wall_height)
        if top >= bottom:
            continue

        texture_top = max(
            0,
            int((top - projected_top) * TEXTURE_SIZE / wall_height),
        )
        texture_bottom = min(
            TEXTURE_SIZE,
            math.ceil((bottom - projected_top) * TEXTURE_SIZE / wall_height),
        )
        brightness = flashlight_falloff(distance)
        if side == 1:
            brightness *= 0.72
        wall_strip = textures[material].subsurface(
            (
                texture_x,
                texture_top,
                1,
                texture_bottom - texture_top,
            )
        )
        wall_strip = pygame.transform.smoothscale(wall_strip, (1, bottom - top))
        shade = round(brightness * 255)
        wall_strip.fill((shade, shade, shade), special_flags=pygame.BLEND_RGB_MULT)
        screen.blit(wall_strip, (column, top))

    screen.blit(flashlight_mask, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    draw_flashlight(screen)


def can_stand(
    world_map: Sequence[str],
    x: float,
    y: float,
    radius: float = PLAYER_RADIUS,
) -> bool:
    min_x, max_x = math.floor(x - radius), math.floor(x + radius)
    min_y, max_y = math.floor(y - radius), math.floor(y + radius)

    for tile_y in range(min_y, max_y + 1):
        for tile_x in range(min_x, max_x + 1):
            if 0 <= tile_y < len(world_map) and 0 <= tile_x < len(world_map[tile_y]):
                is_wall = world_map[tile_y][tile_x] == "1"
            else:
                is_wall = True
            if not is_wall:
                continue

            nearest_x = max(tile_x, min(x, tile_x + 1))
            nearest_y = max(tile_y, min(y, tile_y + 1))
            if math.hypot(x - nearest_x, y - nearest_y) < radius:
                return False

    return True


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("DDA Raycaster")
    render_target = pygame.Surface(
        (SCREEN_WIDTH // RENDER_SCALE, SCREEN_HEIGHT // RENDER_SCALE)
    )
    textures = create_wall_textures()
    flashlight_mask = create_flashlight_mask(render_target.get_size())
    clock = pygame.time.Clock()
    running = True

    while running:
        world_map, exit_position = generate_maze()
        player = Player(1.5, 1.5, 0.0, 2.5)
        escaped = False
        restart_maze = False

        while running:
            delta_time = min(clock.tick(60) / 1000.0, 0.1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif escaped and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        restart_maze = True
                        break
                    if event.key == pygame.K_ESCAPE:
                        running = False

            if not running or restart_maze:
                break

            if escaped:
                draw_escape_screen(screen)
                pygame.display.flip()
                continue

            if (int(player.x), int(player.y)) == exit_position:
                escaped = True
                continue

            keys = pygame.key.get_pressed()
            turn = float(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - float(
                keys[pygame.K_LEFT] or keys[pygame.K_a]
            )
            if turn:
                player.angle += turn * 1.5 * delta_time

            forward = float(keys[pygame.K_w] or keys[pygame.K_UP]) - float(
                keys[pygame.K_s] or keys[pygame.K_DOWN]
            )
            strafe = float(keys[pygame.K_e]) - float(keys[pygame.K_q])
            if forward or strafe:
                length = math.hypot(forward, strafe)
                forward /= length
                strafe /= length
                direction_x = math.cos(player.angle)
                direction_y = math.sin(player.angle)
                move_x = (
                    direction_x * forward - direction_y * strafe
                ) * player.speed * delta_time
                move_y = (
                    direction_y * forward + direction_x * strafe
                ) * player.speed * delta_time

                if can_stand(world_map, player.x + move_x, player.y):
                    player.x += move_x
                if can_stand(world_map, player.x, player.y + move_y):
                    player.y += move_y

            render_scene(render_target, player, world_map, textures, flashlight_mask)
            pygame.transform.scale(render_target, screen.get_size(), screen)
            pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
