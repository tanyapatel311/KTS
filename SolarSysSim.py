#install pygame
import pygame
pygame.init()
import math

#set up pygame window
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
#set title of window
pygame.display.set_caption("Planet Simulation")
#set up colors
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
RED = (188, 39, 50)
DARK_GREY = (80, 78, 81)

FONT = pygame.font.SysFont("comicsans", 16)

#planet class
class Planet:
    AU = 149.6e6 * 1000  # average distance from sun to earth in meters
    G = 6.67428e-11
    SCALE = 250 / AU #1 au = 100 pixels
    TIMESTEP = 3600 * 24 #1 day
    
    def __init__(self,x, y, radius, color, mass):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass
        
        #velocity in mult directions; moving them simultaenously makes them move in circle
        self.x_vel = 0
        self.y_vel = 0
        
        #keep track of all the poitns planet has traveled along 
        self.orbit = []
        #check if planet is Sun (to know whether to draw orbit or not)
        self.sun = False
        self.distance_to_sun = 0
    #draw method    
    def draw(self,win):
        x= self.x * self.SCALE + WIDTH / 2
        y = self.y * self.SCALE + HEIGHT / 2
        
       
        if len(self.orbit) > 2: 
             #updated points to scale
            updated_points = []
            for point in self.orbit:
                x, y = point
                x = x * self.SCALE + WIDTH / 2
                y = y * self.SCALE + HEIGHT / 2
                updated_points.append((x,y))
                
            pygame.draw.lines(win, self.color, False, updated_points, 2)
        pygame.draw.circle(win, self.color, (x,y), self.radius)
        
        
        if not self.sun:
            distance_text = FONT.render(f"{round(self.distance_to_sun/1000, 1)}km", 1, WHITE)
            win.blit(distance_text, (x - distance_text.get_width()/2, y - distance_text.get_height()/2))
            
        

           
        
    #calc force of attarction bwt current object and other object 
    def attraction(self, other):
        other_x, other_y = other.x, other.y
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        distance = math.sqrt(distance_x**2 + distance_y**2)
        
        if other.sun:
            #sun's distance is upated 
            self.distance_to_sun = distance
    
        force = self.G * self.mass * other.mass / distance**2
        #calc the angle using tangent
        theta = math.atan2(distance_y, distance_x)
        #calc force in x and y directions
        force_x =  math.cos(theta) * force
        force_y =  math.sin(theta) * force
        #return the forces 
        return force_x, force_y
    
    #update the position
    def update_position(self, planets):
        #alc force of attraction between current planet and other planets
        total_fx = total_fy = 0
        for planet in planets:
            if self == planet:
                continue
            #gives us fx, fy
            fx, fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy

        #calculate velocity
        self.x_vel += total_fx / self.mass * self.TIMESTEP
        self.y_vel += total_fy / self.mass * self.TIMESTEP
        
        #calc displacement
        self.x += self.x_vel * self.TIMESTEP
        self.y += self.y_vel * self.TIMESTEP
        
        self.orbit.append((self.x, self.y))
              

def main():
    run = True
    #synchronize game
    clock = pygame.time.Clock()
    
    #make the sun
    sun = Planet(0,0,30, YELLOW, 1.98892 * 10**30 )
    sun.sun = True
    
    #make earth
    earth = Planet(-1 *Planet.AU, 0,16, BLUE, 5.9742 * 10**24)
    earth.y_vel = 29.783 * 1000
    
    #make mars 
    mars = Planet(-1.524 * Planet.AU, 0 , 12, RED, 6.39 * 10**23)
    mars.y_vel = 24.077 * 1000
    #make mercury
    mercury = Planet(0.387 * Planet.AU, 0, 8, DARK_GREY, 0.330 * 10**24)
    mercury.y_vel = -47.4 * 1000
    #make venus
    venus = Planet(0.723 * Planet.AU, 0, 14, WHITE, 48.8685 * 10**24)
    venus.y_vel = -35.02 * 1000
    planets = [sun, earth, mars, mercury, venus]
    
    
    while run:
        #60 frames per second update
        clock.tick(60)
        screen.fill((0,0,0))
        #update display
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
        for planet in planets:
            #upate position of the planet
            planet.update_position(planets)
            planet.draw(screen)
            
        pygame.display.update()
    
    #quit the pygame
    pygame.quit()
    
main()
