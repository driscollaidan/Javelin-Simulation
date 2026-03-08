import spiceypy as spice
import numpy as np

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
    
    return state # first three elements are position, last three are velocity, in km and km/s respectively