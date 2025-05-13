import pygame
from simulation import forces
from ui import UIManager

def main():
    #Parameters to play with
    gravity_strength = 1000
    symmetry = 1
    number_of_bodies = 300
    max_color = 200
    mass_range = [1, 100]
    vel_range = [0, 0]
    SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 600

    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Gravity Simulation")
    
    # Create list of bodies (populated in the UI)
    bodies = []
    paused = False
        
    # Create  UI
    ui = UIManager(SCREEN_WIDTH, SCREEN_HEIGHT)
    ui.setup_buttons(bodies, number_of_bodies, vel_range, mass_range)

    def toggle_pause():
        nonlocal paused
        paused = not paused
        ui.pause_button.text = 'Play' if paused else 'Pause'

    ui.pause_button.callback = toggle_pause

    run = True
    while run:
        screen.fill((0, 0, 0)) #Reset bacground to black each frame
        dt = clock.tick(60) / 1000 #Frame rate

        if not paused:
            #Compute the forces between bodies: O(n^2)
            forces(bodies, symmetry, gravity_strength)
            #Update to next frame
            for body in bodies:
                body.update(dt)

        for body in bodies:
            body.draw(screen, max_color)

        ui.draw(screen)
        # Handle events and Exit progarm logic
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            ui.handle_event(event, bodies)
        pygame.display.update()
    pygame.quit()

if __name__ == '__main__':
    main()
