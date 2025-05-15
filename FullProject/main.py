# pip install pygame
# pip install pygame_gui
# pip install numpy
# pip install numba

import pygame, pygame_gui
from simulation import forces
from ui import UIManager
import numpy as np

from ui import UIManager

def main():
    # Simulation settings
    WIDTH, HEIGHT = 1200, 750
    GRAVITY = 100
    MAX_FORCE = 100
    NUM_BODIES = 1500
    MASS_RANGE = [1, 100]
    VEL_RANGE = [0, 0]

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Gravity Simulation")
    clock = pygame.time.Clock()
    last_time = pygame.time.get_ticks() / 1000.0

    manager = pygame_gui.UIManager((WIDTH, HEIGHT), theme_path="theme.json")

    bodies = []
    ui = UIManager(screen, manager, bodies, NUM_BODIES, VEL_RANGE, MASS_RANGE)
    paused = False
    running = True


    while running:
        #Clock Speed
        clock.tick(120)
        current_time = pygame.time.get_ticks() / 1000.0
        dt = current_time - last_time
        last_time = current_time
        dt = min(dt, 0.045)

        screen.fill((0, 0, 0))
        ui.draw_overlay()

        #Body calculations
        if not paused:
            forces(bodies, MAX_FORCE, GRAVITY)
            for body in bodies:
                body.update(dt)
        for body in bodies:
            body.draw(screen, 200)

    
        for event in pygame.event.get():
            # Handle mouse and UI events
            ui.handle_event(event)
            manager.process_events(event)
            if event.type == pygame.QUIT:
                running = False
            
            # Process UI actions
            action = ui.process_gui_events(event)
            if action == 'toggle_pause':
                paused = not paused
                ui.pause_button.set_text("Play" if paused else "Pause")
            elif action == 'reset':
                bodies.clear()
            elif action == 'create_body':
                #center = np.array([WIDTH//2, HEIGHT //2])
                ui.spawn_bodies_button((1,1))
                
        
        manager.update(dt)
        ui.update_info(clock.get_fps())
        #call the update_hover_label each frame
        #ui.update_hover_label()
        
        manager.draw_ui(screen)
        pygame.display.update()
    pygame.quit()

if __name__ == '__main__':
    main()
