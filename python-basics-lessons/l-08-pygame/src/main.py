import pygame

from game_scene import GameScene

pygame.init()

scene = GameScene()

# Игровой цикл
run_game_loop = True
while run_game_loop:
    # Обработка события выхода
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            run_game_loop = False

    scene.draw_all()
    scene.handle_game_logic()

# Корректное закрытие всех модулей Pygame
pygame.quit()
