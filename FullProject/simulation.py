import pygame
import numpy as np
from numba import njit

#BODY CLASS---------------------------------------------------------------------------------------------------
class Body:
    def __init__(self, mass, pos, vel=None, radius=1):
        self.mass = float(mass)
        self.pos = np.array(pos, dtype=float)    # Force float
        self.vel = np.array(vel, dtype=float) if vel is not None else np.zeros(2, dtype=float) #if no velocity input, set vel=[0,0]
        self.radius = radius
        self.acc = np.zeros(2, dtype=float)      

    def update(self, time_step):        #Eulers method
        self.vel +=self.acc*time_step   #v = v0+a*t
        self.pos += self.vel*time_step  #p = p0+v*t
        self.acc[:]=0                   #Reset acceleration each frame

    def draw(self, screen, max_color):
        speed = np.linalg.norm(self.vel)        #Velocity magnitude
        if np.isnan(speed) or max_color == 0:   #Divide by 0 case
            speed_color = 0     
        else:
            norm_speed = min(speed / max_color, 1)              #Normalization stuff
            speed_color = int((np.abs(1 - norm_speed)) * 255)   #Change from saturated -> vibrant color
        
        scale_radius = min(max(2, int(self.mass ** 0.3)), 10)   #Compute radius based on mass (capped)
        pygame.draw.circle(screen, (255,speed_color,speed_color), self.pos, scale_radius)   #Update body
#BODY CLASS----------------------------------------------------------------

@njit
def compute_forces_numba(positions, mass, max_force, G):
    n = positions.shape[0]
    acc = np.zeros((n, 2))

    for i in range(n):
        m1 = mass[i]
        x,y = positions[i]

        for j in range(i+1,n):
            m2 = mass[j]
            if i == j:
                continue
            dx = positions[j, 0] - x
            dy = positions[j, 1] - y
            dist_sqr = dx * dx + dy * dy #+ 1e-5  # Softening to avoid division by zero
            dist = np.sqrt(dist_sqr)

            f_mag = min(G * m1 * m2 / dist_sqr, max_force)
            fx = f_mag * dx / dist
            fy = f_mag * dy / dist

            acc[i, 0] += fx
            acc[i, 1] += fy

    return acc

def forces(bodies, max_force, G=1):
    if len(bodies) < 2:
        return

    positions = np.array([body.pos for body in bodies])
    masses = np.array([body.mass for body in bodies])

    accelerations = compute_forces_numba(positions, masses, max_force, G)

    for i, body in enumerate(bodies):
        body.acc = accelerations[i]


def generate_spawn(n, velocity_range, mass_range, width=99, height=100):
    '''Randomly generates a spawn position, velocity, and mass'''
    y = np.random.uniform(0, height, size=n)                                   #Random generat x-position
    x = np.random.uniform(0, width, size=n)                                    #Random generat x-position
    #position = np.column_stack((x_axis, y_axis))
    velocity = np.random.uniform(velocity_range[0], velocity_range[1], size=(n, 2)) #Random generate velocity
    mass = np.random.uniform(mass_range[0], mass_range[1], size=n)                  #Random generate mass

    bodies = []
    for i in range(n):
        bodies.append(Body(mass[i], [x[i], y[i]], velocity[i]))
    return bodies


def generate_ring(n, scale_radius=100, center=(600, 350)):
    '''Adds bodies in a circular pattern'''
    bodies = []
    for i in range(n):
        theta = 2 * np.pi * i / n
        x = center[0] + scale_radius * np.cos(theta)    #x-position
        y = center[1] + scale_radius * np.sin(theta)    #y-position

        vx = np.sin(theta)      #x-velocity
        vy = -np.cos(theta)     #y-velocity
        vel = np.array([vx, vy]) * 20  

        bodies.append(Body(5, [x, y], vel))
    return bodies


def generate_spiral(n, spacing=0.3, velocity_offset=(0,0), center=(600, 375)):
    '''This can generate galaxies, (Mass is constant 5)'''
    bodies = []
    for i in range(n):
        angle = i*spacing

        x = center[0] + angle * np.cos(angle)   #x-position
        y = center[1] + angle * np.sin(angle)   #y-position

        vx = np.sin(angle)      #x-velocity
        vy = -np.cos(angle)     #y-velocity
        vel = np.array([vx, vy]) * np.sqrt(2000/(angle+1)) + velocity_offset    #Dampening factor + initial speed

        bodies.append(Body(5, [x, y], vel))
    return bodies


def generate_two_galaxies(n_per_galaxy=50, center1=(400, 400), center2=(800, 200), velocity1=(30, 0), velocity2=(-30, 0)):
    '''Calls generate_spiral to place 2 clusters'''
    galaxy1 = generate_spiral(n_per_galaxy, 0.2, np.array(velocity1), center1)
    galaxy2 = generate_spiral(n_per_galaxy, 0.2, np.array(velocity2), center2)
    return galaxy1 + galaxy2