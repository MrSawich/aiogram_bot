import pygame
import random

# Инициализация Pygame
pygame.init()

# Настройки экрана
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Simple Arcade Game")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Настройки игрока
player_size = 50
player_pos = [screen_width // 2, screen_height - 2 * player_size]

# Настройки врага
enemy_size = 50
enemy_pos = [random.randint(0, screen_width - enemy_size), 0]
enemy_list = [enemy_pos]

# Скорость игры
speed = 10

# Частота появления врагов
enemy_spawn_rate = 25

# Счет игры
score = 0
clock = pygame.time.Clock()

# Шрифты
font = pygame.font.SysFont("monospace", 35)

# Функция для отображения счета
def display_score(score):
    text = f"Score: {score}"
    label = font.render(text, 1, BLACK)
    screen.blit(label, (screen_width - 200, screen_height - 40))

# Функция для проверки столкновений
def detect_collision(player_pos, enemy_pos):
    p_x, p_y = player_pos
    e_x, e_y = enemy_pos
    if (e_x >= p_x and e_x < (p_x + player_size)) or (p_x >= e_x and p_x < (e_x + enemy_size)):
        if (e_y >= p_y and e_y < (p_y + player_size)) or (p_y >= e_y and p_y < (e_y + enemy_size)):
            return True
    return False

# Основной игровой цикл
game_over = False
while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_pos[0] > 0:
        player_pos[0] -= speed
    if keys[pygame.K_RIGHT] and player_pos[0] < screen_width - player_size:
        player_pos[0] += speed

    screen.fill(WHITE)

    # Спавн врагов
    if random.randint(0, 100) < enemy_spawn_rate:
        enemy_pos = [random.randint(0, screen_width - enemy_size), 0]
        enemy_list.append(enemy_pos)

    # Обновление позиций врагов
    for enemy_pos in enemy_list:
        if enemy_pos[1] >= 0 and enemy_pos[1] < screen_height:
            enemy_pos[1] += speed
        else:
            enemy_list.remove(enemy_pos)
            score += 1

    # Проверка столкновений
    for enemy_pos in enemy_list:
        if detect_collision(player_pos, enemy_pos):
            game_over = True
            break

    # Рисование врагов
    for enemy_pos in enemy_list:
        pygame.draw.rect(screen, RED, (enemy_pos[0], enemy_pos[1], enemy_size, enemy_size))

    # Рисование игрока
    pygame.draw.rect(screen, BLACK, (player_pos[0], player_pos[1], player_size, player_size))

    # Отображение счета
    display_score(score)

    pygame.display.update()

    clock.tick(30)

pygame.quit()
