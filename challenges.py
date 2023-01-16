import pygame


def challenges(screen):
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill('white')
        pygame.display.flip()


def draw_board():
    pass