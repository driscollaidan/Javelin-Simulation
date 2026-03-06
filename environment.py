import numpy as np
from orbitals import get_body_position

# This file will establish external torques on the spacecraft

def gravitational_acceleration(r, et):

    """
    Computes the gravitational accceleration acting on the spacecraft.
    - Currently only takes the following bodies into account:
        - Sun
        - Earth
    """
    
    # Current positions of celestial bodies
    r_earth = get_body_position(et, "earth")
    r_sun = get_body_position(et, "sun")

    # Pointing vectors from spacecraft
    r_sc_earth = r - r_earth
    r_sc_sun = r - r_sun

    mu_earth = 3.986004418e14
    mu_sun   = 1.32712440018e20

    a_earth = -mu_earth * r_sc_earth / np.linalg.norm(r_sc_earth)**3
    a_sun   = -mu_sun   * r_sc_sun   / np.linalg.norm(r_sc_sun)**3

    a_total = a_earth + a_sun

    return a_total