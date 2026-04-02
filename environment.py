import numpy as np

# This file will establish external torques on the spacecraft
""" 
TODO Verify gravitational acceleration calculations
TODO Replace with one generalized gravity function.
"""

def calculate_gravitational_acceleration(r_sc, r_body, body):
    """
    Computes the gravitational acceleration on the spacecraft from a reference body.
    """
    gravitational_params = {
        "earth": 3.986004418e5,
        "sun": 1.32712440018e11
    }

    mu = gravitational_params[body]

    raise NotImplementedError

def gravitational_acceleration(r, r_earth, r_sun):

    """
    Computes the gravitational accceleration acting on the spacecraft.
    - Currently only takes the following bodies into account:
        - Sun
        - Earth
    """

    # Pointing vectors between spacecraft and celestial bodies
    r_sc_earth = r - r_earth
    r_sc_sun = r - r_sun
    r_earth_sun = r_earth - r_sun

    # Gravitational parameters in km^3/s^2
    mu_earth = 3.986004418e5
    mu_sun   = 1.32712440018e11

    # Gravitational acceleration contributions from each body
    a_sun   = -mu_sun * r_sc_sun / np.linalg.norm(r_sc_sun)**3
    
    a_earth = -mu_earth * (
        r_sc_earth / np.linalg.norm(r_sc_earth)**3
        - r_earth_sun  / np.linalg.norm(r_earth_sun )**3
    )

    return a_earth + a_sun