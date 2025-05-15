import pygame, pygame_gui
from simulation import forces

from ui import UIManager, generate_two_galaxies

def main():
    # Simulation settings
    WIDTH, HEIGHT = 1000, 600
    GRAVITY = 1000
    MAX_FORCE = 100
    NUM_BODIES = 300
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
        clock.tick(60)
        current_time = pygame.time.get_ticks() / 1000.0
        dt = current_time - last_time
        last_time = current_time
        dt = min(dt, 0.045)

        screen.fill((0, 0, 0))

        if not paused:
            forces(bodies, MAX_FORCE, GRAVITY)
            for body in bodies:
                body.update(dt)

        for body in bodies:
            body.draw(screen, 200)

        ui.draw_overlay()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.ACTIVEEVENT:
                if event.state == 2 and event.gain == 0:  # window iconified/moved/unfocused
                    paused = True
                elif event.state == 2 and event.gain == 1:
                    paused = False

            # Handle mouse and UI events
            ui.handle_event(event)
            manager.process_events(event)

            # Process UI actions
            action = ui.process_gui_events(event)
            if action == 'toggle_pause':
                paused = not paused
                ui.pause_button.set_text("Play" if paused else "Pause")
            elif action == 'reset':
                bodies.clear()
        
        manager.update(dt)
        ui.update_info(clock.get_fps())
        manager.draw_ui(screen)
        pygame.display.update()
        

    pygame.quit()

if __name__ == '__main__':
    main()
