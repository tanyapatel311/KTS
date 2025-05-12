import pygame
import numpy as np
import random

#BODY CLASS----------------------------------------------------------------
class Body:
    def __init__(self, mass, pos, vel=None, radius=2):
        self.mass = mass
        self.pos = np.array(pos)
        self.vel = np.array(vel) if vel is not None else np.zeros(2)    #if no velocity input, set vel=[0,0]
        self.radius = radius
        self.acc = np.zeros(2)

    def update(self, time_step):        #Eulers method
        self.vel +=self.acc*time_step   #v0 = v1+a*t
        self.pos += self.vel*time_step  #p0 = p1 +v*t
        self.acc=np.zeros(2)            #reset acceleration each frame

    def draw(self, screen, max_color):
        max_speed = max_color                    #at max_speed, color will be maximum vibrancy 
        speed = np.linalg.norm(self.vel)        #Velocity magnitude
        norm_speed = min(speed/(max_speed),1)     #Normalization stuff
        speed_color = (np.abs(1-norm_speed))*255  #change from saturated -> vibrant color
        speed_color = int(speed_color)
        #Update body
        pygame.draw.circle(screen, (255,speed_color,speed_color), self.pos, self.radius)    
#BODY CLASS----------------------------------------------------------------


def forces (bodies, max_force, G=1):
    positions = np.array([body.pos for body in bodies])
    masses = np.array([body.mass for body in bodies])
    
    diff_matrix = positions[None, :, :] - positions[:, None, :]
    dist_sqr = np.sum(diff_matrix**2, axis=2)
    np.fill_diagonal(dist_sqr, np.inf)          #Ignores interactions like body1 to body 1

    force_mag = np.minimum(G*masses[:, None] * masses[None, :]/dist_sqr, max_force)
    force = force_mag[:,:, None] * diff_matrix / np.sqrt(dist_sqr)[:, :, None]

    total_forces = np.sum(force, axis=1)
    for i, body in enumerate(bodies):
        body.acc = total_forces[i]/masses[i]

#Force function------------------------------------------------------------
def force(bodies, max_force, G=1):
    for i in range(len(bodies)):        
        for j in range(i+1,len(bodies)):        #double loops creates O(n^2)

            dist_vector = bodies[j].pos- bodies[i].pos      #All the physics stuff
            dist_sqr = np.dot(dist_vector, dist_vector)     
            dist_mag = np.sqrt(dist_sqr)                    
            dist_norm = dist_vector/dist_mag                
            force_mag = min(G*bodies[i].mass*bodies[j].mass/dist_sqr, max_force)  #sets max force , prevents super fast objects
            force = force_mag*dist_norm
            
            bodies[i].acc += force/bodies[i].mass    #F/m = a
            bodies[j].acc -= force/bodies[i].mass    #Newtons 3rd law
#Force function------------------------------------------------------------


#Generate particle spawns--------------------------------------------------
def generate_spawn(n, velocity_range, mass_range, width=99, height=100):
    y_axis = np.random.uniform(0, height, size=(n, 1))
    x_axis = np.random.uniform(0, width, size=(n, 1))
    position = np.column_stack((x_axis,y_axis))
    velocity = np.random.uniform(velocity_range[0], velocity_range[1], size=(n, 2))            #Modify (#, #...) to change random body velocities
    mass = np.random.uniform(mass_range[0], mass_range[1], size=(n, 1))               #Modify (#, #...) to change random body masses 

    #Adding all bodies to the bodies list
    bodies = []
    for i in range(n):
        body = Body(np.copy(mass[i]), np.copy(position[i]), np.copy(velocity[i]))
        bodies.append(body)
    return bodies
#Generate particle spawns--------------------------------------------------


def generate_ring(n, center=(400, 300), radius=100):
    bodies = []
    for i in range(n):
        theta = 2 * np.pi * i / n
        x = center[0] + radius * np.cos(theta)
        y = center[1] + radius * np.sin(theta)

        # Optional: perpendicular orbital velocity
        vx = -np.sin(theta)
        vy = np.sin(theta)
        vel = np.array([vx, vy]) * 20  # scale velocity

        bodies.append(Body(5, [x, y], vel))
    return bodies

def generate_spiral(n, arm_count=2, center=(400, 300)):
    bodies = []
    for i in range(n):
        theta = i * 0.3
        r = 5 * theta  # increasing radius => spiral
        arm_offset = (i % arm_count) * (2 * np.pi / arm_count)
        angle = theta + arm_offset

        x = center[0] + r * np.cos(angle)
        y = center[1] + r * np.sin(angle)

        vx = np.sin(angle)
        vy = -np.cos(angle)
        vel = np.array([vx, vy]) * np.sqrt(1000 / (r + 1))  # orbital velocity falloff

        bodies.append(Body(5, [x, y], vel))
    return bodies


def generate_two_galaxies(n_per_galaxy=50, center1=(400, 300), center2=(600, 300), 
                          velocity1=(0, 30), velocity2=(0, -30), spiral_arms=3):
    def spiral(center, n, arm_offset=0, velocity_offset=(0, 0)):
        bodies = []
        for i in range(n):
            theta = i * .1
            r = 4 * theta
            arm_angle = (i % spiral_arms) * (2 * np.pi / spiral_arms)
            angle = theta + arm_angle + arm_offset

            x = center[0] + r * np.cos(angle)
            y = center[1] + r * np.sin(angle)

            # Orbital velocity perpendicular to radius
            vx = np.sin(angle)
            vy = -np.cos(angle)
            vel = np.array([vx, vy]) * np.sqrt(2000 / (r + 5)) + velocity_offset

            bodies.append(Body(50, [x, y], vel))
        return bodies

    galaxy1 = spiral(center1, n_per_galaxy, arm_offset=0, velocity_offset=np.array(velocity1))
    galaxy2 = spiral(center2, n_per_galaxy, arm_offset=np.pi, velocity_offset=np.array(velocity2))

    return galaxy1 + galaxy2

def main():
    
    #Parameters to play with
    symmetry = 1
    gravity_strength = 1000
    number_of_bodies = 300
    max_color = 200
    rand_mass_range = [1, 100]
    rand_start_velocity_range = [0,0]


    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 600

    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    #choose the shape of the simulation randomly
    def choose_shape():
        choices = ["generate_spawn", "generate_ring", "generate_spiral"]
        return random.choice(choices)
    
    choice = choose_shape()
    if choice == "generate_spawn":
        bodies = generate_spawn(number_of_bodies, rand_start_velocity_range, rand_mass_range, SCREEN_WIDTH, SCREEN_HEIGHT)
    elif choice == "generate_ring":
        bodies = generate_ring(number_of_bodies)
    elif choice == "generate_spiral":
        bodies = generate_spiral(number_of_bodies, 5)
    else:
        print("Sorry, there was an error with the simulation.")
    #bodies = generate_spawn(number_of_bodies, rand_start_velocity_range, rand_mass_range, SCREEN_WIDTH, SCREEN_HEIGHT) 
    #bodies = generate_spiral(number_of_bodies, 5)
    #bodies = generate_ring(number_of_bodies)



    #Main Loop to run Pygame
    run = True
    while run:
        screen.fill((0,0,0)) #Reset bacground to black each frame 
        dt = clock.tick(60)/1000 #Frame rate

        #Compute the forces between bodies: O(n^2)
        forces(bodies, symmetry, gravity_strength)
        print(dt)
        #Update to next frame
        for body in bodies:
            body.update(dt)
            body.draw(screen, max_color)

        #Exit progarm logic
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        pygame.display.update()
    pygame.quit()


if __name__ == '__main__':
    main()