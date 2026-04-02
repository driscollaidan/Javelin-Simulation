import numpy as np
import spiceypy as spice

from helpers import assemble_time_string, seed, random_float
from orbitals import get_body_position

# -------------------------------------------------------------------------------------------------------------------------------------- #
#   Acquisition Mode Conditions                                                                                                          #
# -------------------------------------------------------------------------------------------------------------------------------------- #

def get_acquisition_conditions():

    """
    Simulation for spacecraft acquisition mode after separation from launch vehicle.
    - Given random initial angular velocity and orientation.
    - (TODO) Moments of inertia given by Javelin spacecraft definition.
    - Initial position/velocity based on Earth LEO (200km).
    - Bodies being used for physics calculations: Earth, Sun, Moon.
    - Bodies being used for visualization: Earth.
    """
    
    seed()
    w0 = np.array([random_float(0, 1), random_float(0, 1), random_float(0, 1)])
    q0 = np.array([random_float(0, 1), random_float(0, 1), random_float(0, 1), random_float(0, 1)])

    start_time = {
        "year": 2030,
        "month": 1,
        "day": 1,
        "hour": 0,
        "minute": 0,
        "second": 0
    }

    t0 = spice.utc2et(assemble_time_string(start_time))

    earth_state = get_body_position(t0, "earth")
    r0 = earth_state[:3] + np.array([6571, 0, 0]) # km

    v_circ = np.sqrt(398600.4418 / 6571)          # km/s
    v0 = earth_state[3:6] + np.array([0, v_circ, 0])

    return r0, v0, w0, q0, t0