import numpy as np
import spiceypy as spice

from helpers import assemble_time_string, seed, random_integer, random_float
from orbitals import get_body_position

# -------------------------------------------------------------------------------------------------------------------------------------- #
#   Preset mission modes, can be expanded based on needs.                                                                              #
# -------------------------------------------------------------------------------------------------------------------------------------- #

CUSTOM_SIMULATION = 0
ACQUISITION_SIMULATION = 1
EARTH_ORBIT_SIMULATION = 2

# -------------------------------------------------------------------------------------------------------------------------------------- #
#   Main wrapper, coordinates initial conditions for each simulation type.                                                               #
# -------------------------------------------------------------------------------------------------------------------------------------- #

def get_conditions(simulation):
    
    if simulation == ACQUISITION_SIMULATION:
        return get_acquisition_conditions()

# -------------------------------------------------------------------------------------------------------------------------------------- #
#   Acquisition Mode Conditions                                                                                                          #
# -------------------------------------------------------------------------------------------------------------------------------------- #

def get_acquisition_conditions():

    """
    Simulation for spacecraft acquisition mode after separation from launch vehicle.
    - Given random initial angular velocity and orientation.
    - (TODO) Moments of inertia given by Javelin spacecraft definition.
    - Runs for about one/sixth period of Earth orbit, 1000 seconds.
    - (TODO) Start time/date for simulation based on mission definition, proposed date.
    - Initial position/velocity based on Earth LEO (200km).
        - (TODO) Specific orbit defined based on mission definition.
    - Bodies being used for physics calculations: Earth, Sun, Moon.
    - Bodies being used for visualization: Earth.

    """
    
    seed()
    w0 = np.array([random_float(0, 1), random_float(0, 1), random_float(0, 1)])
    q0 = np.array([random_float(0, 1), random_float(0, 1), random_float(0, 1), random_float(0, 1)])

    I = get_inertia_matrix()

    start_time = {
        "year": 2030,
        "month": 1,
        "day": 1,
        "hour": 0,
        "minute": 0,
        "second": 0
    }

    start_et = spice.utc2et(assemble_time_string(start_time))

    earth_state = get_body_position(start_et, "earth")
    r0 = earth_state[:3] + np.array([6571, 0, 0]) # km

    v_circ = np.sqrt(398600.4418 / 6571)          # km/s
    v0 = earth_state[3:6] + np.array([0, v_circ, 0])

    conditions = {
        "I": I,
        "simulation_time": 1000,
        "start_et": start_et,
        "r0": r0,
        "v0": v0,
        "w0": w0,
        "q0": q0,
        "physics_bodies": ["EARTH", "SUN"],
        "visualization_bodies": ["EARTH"]
    }

    return conditions

# -------------------------------------------------------------------------------------------------------------------------------------- #
#   Returns diagonal inertia matrix.                                                                                                     #
# -------------------------------------------------------------------------------------------------------------------------------------- #

def get_inertia_matrix(Ixx = 1, Iyy = 2, Izz = 0.5):
    
    """
    Placeholder function for generating inertia matrix, can be expanded based on needs.
    - Default case based on Javelin spacecraft definition (TBD).
    """

    I = np.diag([Ixx, Iyy, Izz])
    return I