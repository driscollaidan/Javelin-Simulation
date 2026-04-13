import numpy as np
from orbitals import get_body_grav_parameter

R_EARTH_SOI = 1.5e6
R_JUPITER_SOI = 48.2e6

# TODO: Lots of simplifications/assumptions in the torque calculations. Can expand upon them.

def get_environmental_effects(C, t, r, I, splines, surfaces):
    """
    Coordinator function to retrieve all environmental accelerations and torques given state.
    """
    # Gravitational acceleration and torque.
    a_gg = np.zeros(3)
    L_gg = np.zeros(3)

    for body in splines:

        # Body specific position and gravitational parameter.
        r_body = splines[body](t)
        mu = get_body_grav_parameter(body)
        
        # Vector from spacecraft to body, and permutatons of it.
        r_dist = r - r_body
        r_norm = np.linalg.norm(r_dist)
        r_hat_inertial = r_dist / r_norm
        r_hat_body = C @ r_hat_inertial # Convert unit vector from inertial to body frame

        # Calculate and append acceleration and torque.
        a_gg += calculate_gravitational_acceleration(r_dist, r_norm, mu)
        L_gg += calculate_gravity_gradient_torque(r_norm, r_hat_body, mu, I)

    # Magnetic torque.
    m_body = np.array([4.15, 3.1, -5.2]) # Spacecraft magnetic moment in body frame, A*m^2, magnitude ~7.35
    B = get_magnetic_field(t, r, splines) # Get appropriate magnetic field
    B_body = C @ B # Translate to body frame
    L_mag = calculate_magnetic_torque(m_body, B_body)

    # Solar radiation pressure torque.
    L_srp = calculate_solar_radiation_torque(C, r, splines["sun"](t), surfaces)

    return L_gg, L_mag, L_srp, a_gg

def calculate_gravity_gradient_torque(r_norm, r_hat, mu, I):
    """
    Computes the gravitational gradient torque on the spacecraft from a reference body.
    - Graivity gradient toruqe calculated in the body frame.
    - Simplified version of the equation, from NASA.
    """
    L_gg = ((3 * mu) / (r_norm ** 3)) * np.cross(r_hat, I @ r_hat)

    return L_gg

def calculate_gravitational_acceleration(r, r_norm, mu):
    """
    Computes acceleration due to gravity acting on the spacecraft from a reference body.
    - Gravitational acceleration calculated in inertial frame.
    """
    a = -(mu * r) / (r_norm ** 3)

    return a

def calculate_magnetic_torque(m, B):
    """
    Computes the magnetic torque on the spacecraft from its magnetic moment and the local magnetic field.
    - Magnetic torque calculated in body frame.
    """
    L_mag = np.cross(m, B)

    return L_mag

def get_magnetic_field(t, r, splines):
    """
    Determines which magnetic field model to use based on distance from spacecraft.
    - Calculates appropriate magnetic field, and returns it.
    """

    # Decide whether or not to include conditional logic based on radius of influence.\
    if safe_norm(r - splines["earth"](t)) < (2 * R_EARTH_SOI):
        return calculate_magnetic_field(1000 * (r - splines["earth"](t)), 7.96e22, np.deg2rad(11)) # A*m*2
    elif safe_norm(r - splines["jupiter"](t)) < (2 * R_JUPITER_SOI):
        return calculate_magnetic_field(1000 * (r - splines["jupiter"](t)), 1.5e27, np.deg2rad(10))
    else:
        return 5e-9 * np.array([1, 0, 0]) # Typical interplanetary field from document, investigate Parker spiral

def calculate_magnetic_field(r, dipole, tilt):
    """
    Calculates magnetic field for given body.
    """
    # Calculate tilted magnetic field for planet
    m_body = dipole * np.array([
        np.sin(tilt),
        0,
        np.cos(tilt)
    ])

    r_norm = safe_norm(r)
    r_hat = r / r_norm

    B = (1e-7) * (1 / (r_norm ** 3)) * (3 * np.dot(m_body, r_hat) * r_hat - m_body)
    return B

def calculate_solar_radiation_torque(C, r_sc, r_sun, surfaces):
    """
    Calculates torque due to radiation pressure.
    """
    r_dist = 1000 * (r_sc - r_sun) # spacecraft to sun vector
    s_hat = r_dist / safe_norm(r_dist)
    s_hat_body = C @ s_hat

    c = 3e8 # speed of light
    I0 = 1360  # electromagnetic wave intensity [W/m^2]

    r = safe_norm(r_dist) # scaling intensity based on distance to sun
    I = I0 * ((1.496e11 / r) ** 2)

    P = I / c # Pressure calculation
    # coefficients estimation for alluminum spacecraft
    Cs = 0.7
    Cd = 0.2

    L_srp = np.array([0.0, 0.0, 0.0])

    for surface in surfaces:
        # Unpack surface values
        n_hat = surface["normal"] # surface normal unit vector
        A = surface["area"] # surface area
        r_cp = surface["r_cp"] # surface center of pressure

        cos_theta = np.dot(n_hat, -s_hat_body)

        if cos_theta <= 0:
            continue

        F = -P * A * (
            (1 - Cs) * s_hat_body +
            2 * (Cs * cos_theta + (1/3) * Cd) * n_hat
        ) * cos_theta
        L_srp += np.cross(r_cp, F)

    return L_srp

SAFE_VALUE = 1e-6
def safe_norm(v):
    """
    Prevent explosion from norms.
    """
    return max(np.linalg.norm(v), SAFE_VALUE)