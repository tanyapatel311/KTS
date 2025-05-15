import pygame
import pygame_gui
import numpy as np
from simulation import Body, generate_ring, generate_spiral, generate_two_galaxies, generate_spawn

# UI MANAGER CLASS -------------------------------------------------------------
class UIManager:
    def __init__(self, screen, manager, bodies, num_bodies, vel_range, mass_range):
        self.screen = screen
        self.manager = manager
        self.bodies = bodies
        self.num_bodies = num_bodies
        self.vel_range = vel_range
        self.mass_range = mass_range

        self.default_mass = 20
        self.default_radius = 5
        self.creating_body = False
        self.start_pos = None
        self.end_pos = None

        self._setup_gui()

    # Setup GUI components ------------------------------------------------------
    def _setup_gui(self):
        # Control Buttons
        self.pause_button = pygame_gui.elements.UIButton(
            pygame.Rect((10, 10), (80, 30)), 'Pause', self.manager)
        self.reset_button = pygame_gui.elements.UIButton(
            pygame.Rect((100, 10), (80, 30)), 'Reset', self.manager)

        # Body generator buttons
        self.mode_buttons = []
        y = 60  # Vertical offset for stacking buttons

        # Mapping button names to body generators
        generator_defs = {
            'Ring': lambda: generate_ring(self.num_bodies),
            'Spiral': lambda: generate_spiral(self.num_bodies, 3),
            'Two Galaxies': lambda: generate_two_galaxies(150),
            'Random': lambda: generate_spawn(
                self.num_bodies, self.vel_range, self.mass_range,
                self.screen.get_width(), self.screen.get_height()
            )
        }

        # Create buttons and attach their generator callbacks
        for name, func in generator_defs.items():
            button = pygame_gui.elements.UIButton(
                pygame.Rect((10, y), (160, 30)), name, self.manager)
            button.callback_func = func
            self.mode_buttons.append(button)
            y += 40

        # Mass slider and label
        x = self.screen.get_width() - 220
        self.mass_label = pygame_gui.elements.UILabel(
            pygame.Rect((x, 30), (200, 25)),
            f"Mass: {int(self.default_mass)}", self.manager)
        self.mass_slider = pygame_gui.elements.UIHorizontalSlider(
            pygame.Rect((x, 60), (200, 25)),
            self.default_mass, (1, 200), self.manager)
        
        # Number of bodies label and slider
        self.body_count = 10
        self.body_count_label = pygame_gui.elements.UILabel(
            pygame.Rect((x, 100), (200, 25)),
            f"Cluster Size: {int(self.body_count)}", self.manager)

        self.body_count_slider = pygame_gui.elements.UIHorizontalSlider(
            pygame.Rect((x, 130), (200, 25)),
            self.body_count, (1, 100), self.manager)
        
        # FPS and Body Count Info Display (bottom-right)
        screen_width, screen_height = self.screen.get_size()
        self.fps_label = pygame_gui.elements.UILabel(
            pygame.Rect((screen_width - 125, screen_height - 60), (150, 25)),
            "", self.manager)
        self.body_count_label_display = pygame_gui.elements.UILabel(
            pygame.Rect((screen_width - 125, screen_height - 30), (150, 25)),
            "", self.manager)


    def update_info(self, fps):
        self.fps_label.set_text(f"FPS: {int(fps)}")
        self.body_count_label_display.set_text(f"Bodies: {len(self.bodies)}")



    # Handle mouse-based body creation ------------------------------------------
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.manager.get_hovering_any_element():
            self.creating_body = True
            self.start_pos = self.end_pos = np.array(event.pos)

        elif event.type == pygame.MOUSEMOTION and self.creating_body:
            self.end_pos = np.array(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.creating_body:
            self.creating_body = False
            velocity = (self.end_pos - self.start_pos) * 0.4

            # Spawn a cluster of bodies at the start_pos
            for _ in range(self.body_count):
                spread = 30  # how far to scatter the bodies
                scatter = np.random.uniform(-spread, spread, size=2)
                spawn_pos = self.start_pos + scatter
                self.bodies.append(Body(self.default_mass, spawn_pos, velocity, self.default_radius))

            self.start_pos = self.end_pos = None

    # Handle GUI actions --------------------------------------------------------
    def process_gui_events(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.pause_button:
                return 'toggle_pause'
            elif event.ui_element == self.reset_button:
                return 'reset'
            for button in self.mode_buttons:
                if event.ui_element == button:
                    self.bodies.clear()
                    self.bodies.extend(button.callback_func())

        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.mass_slider:
                self.default_mass = self.mass_slider.get_current_value()
                self.mass_label.set_text(f"Mass: {int(self.default_mass)}")

            elif event.ui_element == self.body_count_slider:
                self.body_count = int(self.body_count_slider.get_current_value())
                self.body_count_label.set_text(f"Cluster Size: {self.body_count}")

        return None

    # Draw overlays for visual feedback -----------------------------------------
    def draw_overlay(self):
        if self.creating_body and self.start_pos is not None and self.end_pos is not None:
            # Visual feedback: drag line and preview circle
            pygame.draw.line(self.screen, (0, 255, 0), self.start_pos, self.end_pos, 2)
            pygame.draw.circle(self.screen, (0, 255, 0), self.start_pos.astype(int), self.default_radius, 1)
