import spiceypy as spice
import numpy as np
from helpers import assemble_time_string, process_time

def load_kernels():
    # Load kernels
    # Kernels are essentially cached binaries
    spice.furnsh("kernels/naif0012.tls")
    spice.furnsh("kernels/de440s.bsp")     # planetary ephemeris
    spice.furnsh("kernels/gm_de440.tpc")    
    spice.furnsh("kernels/jup365.bsp")     # Jupiter + Galilean moons

def clear_kernels():
    # Clean up kernels, good practice
    spice.kclear()

def get_body_position(et, body):

    # expecting time in ephemeris time format: spice.utc2et("2030-01-01T00:00:00")

    state, lt = spice.spkezr( # spice.spkezr returns [state vector, light time]
                body,
                et,
                "ECLIPJ2000",
                "NONE",
                "SUN" # Reference frame
            )

    # Convert from km → m and km/s → m/s
    state = np.array(state)
    state[:3] *= 1000.0   # position
    state[3:] *= 1000.0   # velocity

    return state # first three elements are position, last three are velocity, in km and km/s respectively

def load_spacecraft_3dof(data):
    """
    Retrieves position and velocity data for mission from JSON data, as calculated by Orbitals subteam.
    """

    times = []
    positions = []
    velocities = []

    def process_item(item):

        time = item.get("epoch")
        position = item.get("position_m")
        velocity = item.get("velocity_m_s")

        if time and position and velocity:
            time = process_time(time) # convert to numerical
            times.append(time)
            positions.append(position)
            velocities.append(velocity)

    for sample in data.get("dense_samples", []):
        process_item(sample)

    return times, positions, velocities

def load_planetary_data(bodies):
    """
    Return:
    - time_vec
    - solar_system_data

    Currently, using kernels w/Spiceypy.
    Obtains all planetary position data over time frame.
    - Start/end times matching spacecraft mission definition.
    """

    start_time = {
        "year": 2034,
        "month": 7,
        "day": 5,
        "hour": 17,
        "minute": 48,
        "second": 2
    }

    end_time = {
        "year": 2041,
        "month": 4,
        "day": 20,
        "hour": 20,
        "minute": 43,
        "second": 16
    }

    start_et = spice.utc2et(assemble_time_string(start_time))
    end_et = spice.utc2et(assemble_time_string(end_time))
    t_steps = 10000
    t_vec = np.linspace(start_et, end_et, t_steps)

    celestial_data = {}
    ets = np.linspace(start_et, end_et, t_steps)
    for body in bodies:
        body_data = []
        for et in ets:
            body_data.append(get_body_position(et, body)[:3])
        celestial_data[body.lower()] = {"r": np.array(body_data)}

    return t_vec, celestial_data

def get_body_grav_parameter(body):
    """
    Obtains gravitational parameter 'mu' from kernel data.
    """
    dim, (gm,) = spice.bodvrd(body, 'GM', 1)
    return gm * 1e9