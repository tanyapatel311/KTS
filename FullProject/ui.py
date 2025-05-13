import pygame
import numpy as np
from simulation import Body, generate_ring, generate_spiral, generate_two_galaxies, generate_spawn

#BUTTON CLASS-------------------------------------------------------------
class Button:
    def __init__(self, rect, text, callback):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.font = pygame.font.SysFont(None, 24)

    def draw(self, screen):
        # Draw the button with text
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        color = (150, 150, 150) if is_hovered else (200, 200, 200)
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        text_surf = self.font.render(self.text, True, (0, 0, 0))
        screen.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def handle_event(self, event):
        # Call the button's action if clicked
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if self.callback:
                self.callback()
#BUTTON CLASS-------------------------------------------------------------

class UIManager:
    def __init__(self, screen_width, screen_height):
        self.buttons = []
        self.pause_button = Button((10, 10, 80, 30), 'Pause', None)
        self.creating_body = False
        self.start_pos = None
        self.end_pos = None
        self.default_mass = 20
        self.default_radius = 5
        self.screen_width = screen_width
        self.screen_height = screen_height

    def setup_buttons(self, bodies, num_bodies, vel_range, mass_range):
        y = 60
        # Predefined body setup modes
        modes = [
            ('Ring', lambda: generate_ring(num_bodies)),
            ('Spiral', lambda: generate_spiral(num_bodies, 5)),
            ('Two Galaxies', lambda: generate_two_galaxies(150)),
            ('Random', lambda: generate_spawn(num_bodies, vel_range, mass_range, self.screen_width, self.screen_height))
        ]
        for label, gen_func in modes:
            def make_callback(func=gen_func):
                return lambda: bodies.clear() or bodies.extend(func())
            self.buttons.append(Button((20, y, 160, 30), label, make_callback()))
            y += 40

    def draw(self, screen):
        self.pause_button.draw(screen)
        for btn in self.buttons:
            btn.draw(screen)
        # Show velocity line when creating a new body
        if self.creating_body and self.start_pos is not None and self.end_pos is not None:
            pygame.draw.line(screen, (0, 255, 0), self.start_pos, self.end_pos, 2)
            pygame.draw.circle(screen, (0, 255, 0), self.start_pos.astype(int), self.default_radius, 1)

    def handle_event(self, event, bodies):
        self.pause_button.handle_event(event)
        for btn in self.buttons:
            btn.handle_event(event)

        # Create new body using click and drag
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not any(btn.rect.collidepoint(event.pos) for btn in self.buttons + [self.pause_button]):
                self.creating_body = True
                self.start_pos = np.array(event.pos)
                self.end_pos = np.array(event.pos)

        elif event.type == pygame.MOUSEMOTION and self.creating_body:
            self.end_pos = np.array(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.creating_body:
            self.creating_body = False
            velocity = (self.end_pos - self.start_pos) * 0.1
            new_body = Body(self.default_mass, self.start_pos, velocity, self.default_radius)
            bodies.append(new_body)
            self.start_pos = None
            self.end_pos = None
