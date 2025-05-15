import pygame
import numpy as np
from numba import njit

#BODY CLASS----------------------------------------------------------------
class Body:
    def __init__(self, mass, pos, vel=None, radius=2):
        self.mass = float(mass)
        self.pos = np.array(pos, dtype=float)    # Force float
        self.vel = np.array(vel, dtype=float) if vel is not None else np.zeros(2, dtype=float) #if no velocity input, set vel=[0,0]
        self.radius = radius
        self.acc = np.zeros(2, dtype=float)      

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

@njit
def compute_forces_numba(positions, masses, max_force, G):
    n = positions.shape[0]
    acc = np.zeros((n, 2))

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            dx = positions[j, 0] - positions[i, 0]
            dy = positions[j, 1] - positions[i, 1]
            dist_sqr = dx * dx + dy * dy + 1e-5  # Softening to avoid division by zero
            dist = np.sqrt(dist_sqr)
            f_mag = min(G * masses[i] * masses[j] / dist_sqr, max_force)
            fx = f_mag * dx / (dist * masses[i])
            fy = f_mag * dy / (dist * masses[i])
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



#Force function------------------------------------------------------------
def forcesa (bodies, max_force, G=1):
    if len(bodies) < 2:
        return
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



#Generate particle spawns--------------------------------------------------
def generate_spawn(n, velocity_range, mass_range, width=99, height=100):
    y_axis = np.random.uniform(0, height, size=n) 
    x_axis = np.random.uniform(0, width, size=n) 
    position = np.column_stack((x_axis, y_axis))
    velocity = np.random.uniform(velocity_range[0], velocity_range[1], size=(n, 2)) #Modify (#, #...) to change random body velocities
    mass = np.random.uniform(mass_range[0], mass_range[1], size=n) #Modify (#, #...) to change random body masses

    #Adding all bodies to the bodies list
    bodies = []
    for i in range(n):
        body = Body(mass[i], np.copy(position[i]), np.copy(velocity[i]))
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
        r = 6 * theta  # increasing radius => spiral
        arm_offset = (i % arm_count) * (2 * np.pi / arm_count)
        angle = theta + arm_offset

        x = center[0] + r * np.cos(angle)
        y = center[1] + r * np.sin(angle)

        vx = np.sin(angle)
        vy = -np.cos(angle)
        vel = np.array([vx, vy]) * np.sqrt(1000 / (r + 1))  # orbital velocity falloff

        bodies.append(Body(5, [x, y], vel))
    return bodies

def generate_two_galaxies(n_per_galaxy=50, center1=(400, 300), center2=(600, 300), velocity1=(0, 30), velocity2=(0, -30), spiral_arms=3):
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