import pygame

from game_constants import (DISPLAY_HEIGHT, DISPLAY_WIDTH,
                            PLAYER_INITIAL_RADIUS, PLAYER_INITIAL_VELOCITY)


class Player:

    def __init__(self):
        self.x = DISPLAY_WIDTH / 2
        self.y = DISPLAY_HEIGHT / 2
        self.v = PLAYER_INITIAL_VELOCITY
        self.radius = PLAYER_INITIAL_RADIUS

    def handle_keys(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.v * dt
        if keys[pygame.K_RIGHT] and self.x < DISPLAY_WIDTH:
            self.x += self.v * dt
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.v * dt
        if keys[pygame.K_DOWN] and self.y < DISPLAY_HEIGHT:
            self.y += self.v * dt

    def draw(self, screen):
        pygame.draw.circle(screen, "red", (self.x, self.y), self.radius)
