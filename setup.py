import numpy as np
import spiceypy as spice

from helpers import assemble_time_string
from orbitals import get_body_position

# Current values picked on whim, can be later determined based on mission details.
# Function purpose is to cleanly separate numerical values from main script, for ease of alteration.
"""
TODO
Implement conditional setting of initial conditions dependant on either preset mission modes, or user inputs.
- Currently, all initial conditions are somewhat arbitrarily selected, but based on realistic values.
"""
def get_conditions():
    
    """
    Initialize all data needed for simulation start.
    - [I]  : Diagonal intertia matrix
    - [w0] : Initial angular velocities
    - [t]  : Simulation timespan
    - [L]  : Initial torques
    - [q0] : Initial quaternion orientation
    """

    # Inertia Matrix
    I = np.diag([1, 2, 0.5])

    # Angular Velocity
    w0 = np.array([0.1, 0.2, 0.15])

    # Initial Quaternions
    q0 = np.array([1, 0, 0, 0])

    # Time Vector, seconds beyond the start_time
    seconds_elapsed = 2500
    time_steps = 2500
    time_vec = np.linspace(0, seconds_elapsed, time_steps)

    # Initial time definition
    start_time = {
        "year": 2030,
        "month": 1,
        "day": 1,
        "hour": 0,
        "minute": 0,
        "second": 0
    }

    start_et = spice.utc2et(assemble_time_string(start_time)) # convert string to ephemeris time

    # Approximate start position/velocity for spacecraft based on Earth
    earth_state = get_body_position(start_et, "earth")
    r0 = earth_state[:3] + np.array([7000, 0, 0]) # 7000 km from Earth center
    v0 = earth_state[3:6] + np.array([0, 7.5, 0]) # approximate LEO velocity, km/s

    bodies = ["EARTH", "SUN"] # bodies to be queried for position/velocity data, can be altered based on mission details, e.g., "JUPITER", "EUROPA", "VENUS"

    # Wrap in dictionary
    initial_conditions = {
        "I": I,
        "time_vec" : time_vec,
        "time_steps": time_steps,
        "seconds_elapsed": seconds_elapsed,
        "start_et": start_et,
        "r0": r0,
        "v0": v0,
        "w0": w0,
        "q0": q0,
        "bodies": bodies
    }

    return initial_conditions