import numpy as np

# This file will establish external torques and accleration on the spacecraft

def calculate_gravity_gradient_torque(r_norm, r_hat, mu, I):
    """
    Computes the gravitational gradient torque on the spacecraft from a reference body.
    - Graivity gradient toruqe calculated in the body frame.
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
