# (rest of your imports)
import pygame
import pygame_gui
import numpy as np
from simulation import Body, generate_ring, generate_spiral, generate_two_galaxies, generate_spawn

class UIManager:
    def __init__(self, screen, manager, bodies, num_bodies, vel_range, mass_range):
        self.screen, self.manager, self.bodies = screen, manager, bodies
        self.num_bodies, self.vel_range, self.mass_range = num_bodies, vel_range, mass_range

        self.default_mass, self.default_radius = 20, 5
        self.creating_body = False
        self.start_pos = None
        self.end_pos = None
        self.body_count = 10

        self.spawn_mode = True  # True = cluster spawn, False = particle inspect
        self.selected_body = None

        self._setup_gui()

    def _setup_gui(self):
        '''Setup the GUI buttons and sliders.'''
        w, h = self.screen.get_width(), self.screen.get_height()
        x = w - 220
        
        #Add Pause and Reset buttons
        self.pause_button = pygame_gui.elements.UIButton(pygame.Rect(10, 10, 80, 30), 'Pause', self.manager)
        self.reset_button = pygame_gui.elements.UIButton(pygame.Rect(100, 10, 80, 30), 'Reset', self.manager)

        # Add toggle mode button
        self.mode_toggle_button = pygame_gui.elements.UIButton(pygame.Rect(x, 160, 200, 25), 'Mode: Spawn', self.manager)

        #Create dictionary of generator functions
        generator_map = {
            'Ring': lambda: generate_ring(self.num_bodies),
            'Spiral': lambda: generate_spiral(self.num_bodies, 3),
            'Two Galaxies': lambda: generate_two_galaxies(150),
            'Random': lambda: generate_spawn(self.num_bodies, self.vel_range, self.mass_range, *self.screen.get_size())
        }

        self.generate_buttons = []
        for i, (label, func) in enumerate(generator_map.items()):
            buttons = pygame_gui.elements.UIButton(pygame.Rect(10, 60 + i * 40, 160, 30), label, self.manager)
            buttons.generator_func = func
            self.generate_buttons.append(buttons)

        # Mass and Cluster Size sliders
        self.mass_slider = pygame_gui.elements.UIHorizontalSlider(pygame.Rect(x, 40, 200, 25), self.default_mass, (1, 200), self.manager)
        self.mass_label = pygame_gui.elements.UILabel(pygame.Rect(x, 10, 200, 25), f"Mass: {int(self.default_mass)}")

        self.numBodies_slider = pygame_gui.elements.UIHorizontalSlider(pygame.Rect(x, 110, 200, 25), self.body_count, (1, 100), self.manager)
        self.numBodies_label = pygame_gui.elements.UILabel(pygame.Rect(x, 80, 200, 25), f"Cluster Size: {self.body_count}")

        # FPS and Bodies labels
        self.fps_label = pygame_gui.elements.UILabel(pygame.Rect(w - 125, h - 60, 150, 25), "", self.manager)
        self.bodies_label = pygame_gui.elements.UILabel(pygame.Rect(w - 125, h - 30, 150, 25), "", self.manager)

    def handle_event(self, event):
        '''Handles mouse events'''
        if self.spawn_mode:
            # Cluster spawn mode
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.manager.get_hovering_any_element():
                self.creating_body = True
                self.start_pos = self.end_pos = np.array(event.pos)
            elif event.type == pygame.MOUSEMOTION and self.creating_body:
                self.end_pos = np.array(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.creating_body:
                velocity = (self.end_pos - self.start_pos) * 0.4
                if self.body_count == 1:
                    self.bodies.append(Body(self.default_mass, self.start_pos, velocity, self.default_radius))
                else:
                    for _ in range(self.body_count):
                        scatter = np.random.uniform(-30, 30, size=2)
                        self.bodies.append(Body(self.default_mass, self.start_pos + scatter, velocity, self.default_radius))
                self.creating_body = self.start_pos = self.end_pos = None
        else:
            # Particle inspection mode
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.manager.get_hovering_any_element():
                mouse_pos = np.array(event.pos)
                # Check if mouse is over any body
                for body in self.bodies:
                    if np.linalg.norm(mouse_pos - body.pos) < max(5, body.radius + 2):
                        self.selected_body = body
                        break
                else:
                    self.selected_body = None

    def process_gui_events(self, event):
        '''Handles buttons and sliders'''
        #Handle Button events
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.pause_button:
                return 'toggle_pause'
            elif event.ui_element == self.reset_button:
                return 'reset'
            elif event.ui_element == self.mode_toggle_button:
                self.spawn_mode = not self.spawn_mode
                self.mode_toggle_button.set_text("Mode: Spawn" if self.spawn_mode else "Mode: Inspect")
            for buttons in self.generate_buttons:
                if event.ui_element == buttons:
                    self.bodies.clear()
                    self.bodies.extend(buttons.generator_func())
        #Handle Slider events
        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.mass_slider:
                self.default_mass = self.mass_slider.get_current_value()
                self.mass_label.set_text(f"Mass: {int(self.default_mass)}")
            elif event.ui_element == self.numBodies_slider:
                self.body_count = int(self.numBodies_slider.get_current_value())
                self.numBodies_label.set_text(f"Cluster Size: {self.body_count}")
        return None

    def draw_line(self):
        '''Create drag line'''
        if self.creating_body:
            pygame.draw.line(self.screen, (0, 255, 0), self.start_pos, self.end_pos, 2)
            pygame.draw.circle(self.screen, (0, 255, 0), self.start_pos.astype(int), self.default_radius, 1)

    def update_info(self, fps):
        '''Update FPS and number of bodies trackers and display the inspection info'''
        self.fps_label.set_text(f"FPS: {int(fps)}")
        self.bodies_label.set_text(f"Bodies: {len(self.bodies)}")
        
        # Draw info of selected particle
        if self.selected_body:
            font = pygame.font.SysFont(None, 24)
            mass_text = font.render(f"Mass: {self.selected_body.mass:.2f}", True, (255, 255, 255))
            vel_mag = np.linalg.norm(self.selected_body.vel)
            vel_text = font.render(f"Velocity: {vel_mag:.2f}", True, (255, 255, 255))
            self.screen.blit(mass_text, (10, self.screen.get_height() - 60))
            self.screen.blit(vel_text, (10, self.screen.get_height() - 30))
