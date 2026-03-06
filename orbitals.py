import spiceypy as spice
import numpy as np

def get_solar_system_data(start_et, end_et, time_steps):

    """
    Iterates through time range of 2030-2040, with inputted amount of steps.
    - Stores position and velocity of each body with reference to the sun in a dictionary.
        - Returns dictionary.
    - Bodies currently implemented: Earth, Venus, Jupiter, Europa, Sun
    """

    ets = np.linspace(start_et, end_et, time_steps)

    # Bodies queried
    bodies = ["EARTH", "VENUS", "JUPITER", "EUROPA", "SUN"]

    # Dictionary containing body data
    data = {}

    """
    Allegedly, this structure can work:
    
        for body in bodies:
        states = np.array([
            spice.spkezr(body, et, "J2000", "NONE", "SOLAR SYSTEM BARYCENTER")[0]
            for et in ets
        ])

    And is an improvement in terms of computational runtime.
    TODO: Investigate.
    """

    for body in bodies:
        r_list = []
        v_list = []

        for et in ets:
            # State Vector: [x, y, z, vx, vy, vz], in km & km/s 
            state, lt = spice.spkezr(   # spice.spkezr returns [state vector, light time]
                body,
                et,
                "J2000",
                "NONE",
                "SOLAR SYSTEM BARYCENTER" # Reference frame
            )
            r_list.append(state[:3])   # km
            v_list.append(state[3:])   # km/s

        data[body.lower()] = {
            "r": np.array(r_list),
            "v": np.array(v_list)
        }

    return data

def load_kernels():
    # Load kernels
    # Kernels are essentially cached binaries
    spice.furnsh("kernels/naif0012.tls")
    spice.furnsh("kernels/de440s.bsp")     # planetary ephemeris
    spice.furnsh("kernels/jup365.bsp")     # Jupiter + Galilean moons

def clear_kernels():
    # Clean up kernels, good practice
    spice.kclear()

def get_body_position(et, body):

    # expecting time in ephemeris time format: spice.utc2et("2030-01-01T00:00:00")

    state, lt = spice.spkezr( # spice.spkezr returns [state vector, light time]
                body,
                et,
                "J2000",
                "NONE",
                "SOLAR SYSTEM BARYCENTER" # Reference frame
            )
    
    return state[:3] # km