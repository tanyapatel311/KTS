# Gravity Simulator
By: Kevin Kopcinski, Tanya Patel, Sayumi Amarasinghe<br/>
A Python-based real-time gravity simulation that models interactions between bodies (like planets or stars) using object-oriented programming and a Pygame. 


# Features
* Interactive GUI with sliders and buttons for spawning and inspecting particles
* Custom Galaxy Generators: Random, Ring, Spiral, and Two-Galaxy collision scenarios
* Real-Time Physics: Newtonian gravity using Numba-accelerated calculations
* Visualization: Velocity-based coloring and dynamic body radius
* Particle Selection Mode: Inspect mass and velocity of individual bodies

# Libraries
* pygame
* pygame_gui
* numpy
* numba


# Controls & UI Overview
* Pause / Play: Toggle simulation state
* Reset: Clear all particles
* Spawn Mode: Click and drag to set initial velocity and spawn a body or cluster
* Inspect Mode: Click a body to display mass and velocity
* Galaxy Generator Buttons: Instantly create predefined galaxy setups
* Mass Slider: Default mass for new bodies
* Cluster Size Slider: Number of bodies spawned at once

# File Structure
* main.py: Entry point, manages game loop and core logic
* simulation.py: Contains physics backend
* ui.py: Handles all GUI elements and interactions
* theme.json: GUI theme customization

# Contribution
This project was fully designed and implemented by the team members, as a final project for CS 2520 (Spring 2025).
