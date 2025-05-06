import pygame
import numpy as np

#BODY CLASS----------------------------------------------------------------
class Body:
    def __init__(self, mass, pos, vel=None, radius=2, color=(255,255,255)):
        self.mass = np.random.uniform(1, 100,)
        self.pos = np.array(pos)
        self.vel = np.array(vel) if vel is not None else np.zeros(2)
        self.radius = radius
        self.color = color
        self.acc = np.zeros(2)

    def update(self, time_step):        #Eulers method
        print(self.vel)
        self.vel +=self.acc*time_step   #v0 = v1+a*t
        self.pos += self.vel*time_step  #p0 = p1 +v*t
        self.acc=np.zeros(2)           #reset accel each frame

    def draw(self, screen):
        speed = np.linalg.norm(self.vel)

        max_speed = 50
        norm_speed = min(speed/max_speed,1)
        speed_color = int((1-norm_speed)*255)
        pygame.draw.circle(screen, (255,speed_color,speed_color), self.pos, self.radius)

    

#BODY CLASS----------------------------------------------------------------
    
def force(bodies, softening=1, G=5):
    for i in range(len(bodies)):
        for j in range(i+1,len(bodies)):

            dist_vector = bodies[j].pos- bodies[i].pos
            dist_sqr = np.dot(dist_vector, dist_vector)+softening
            dist_mag = np.sqrt(dist_sqr)
            dist_norm = dist_vector/dist_mag

            force_mag = min(G*bodies[i].mass*bodies[j].mass/dist_sqr, 200)
            force = force_mag*dist_norm
            bodies[i].acc += force/bodies[i].mass     #F/m = a
            bodies[j].acc -= force/bodies[i].mass    #Newtons 3rd law

#Generate particle spawns--------------------------------------------------
def generate_spawn(n, width=150, height=350):
    locations = np.random.uniform(width, height, size=(n, 2))
    velocity = np.random.uniform(-1, 1, size=(n, 2))


    bodies = []
    for i in range(n):
        body = Body(5, np.copy(locations[i]), np.copy(velocity[i]))
        bodies.append(body)
    return bodies
#Generate particle spawns--------------------------------------------------




#class BHtree: 
    







def main():

    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 600
    clock = pygame.time.Clock()

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


    bodies = generate_spawn(100)

    run = True
    while run:
        dt = clock.tick(60)/1000
        screen.fill((0,0,0))        

        '''for i, body in enumerate(bodies):
            for j, other in enumerate(bodies):
                if i != j:
                    body.force(other)
'''
        force(bodies)
        for body in bodies:
            body.update(dt)
            body.draw(screen)

        #Event handeler
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #press exit to quit
                run = False
        pygame.display.update()

    pygame.quit()

if __name__ == '__main__':
    main()