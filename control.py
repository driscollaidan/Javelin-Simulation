import numpy as np

from attitude import quaternion_conjugate, quaternion_multiply

# ========================================================================================== # 
#
#  Simple PD Controller Implementation:
#        - Recieves current angular velocity, current orientation, and desired orientation.
#               - Desired orientations can be dictated from operational modes and maneuvers
#        - Currently assumes ideal case where torque can be instantly applied.
#               - Will later be constrained basesd on hardware capabilities.
#
# ========================================================================================== #

def pd_control(w, q, q_desired):

    """
    - [e] : vector part of quaternion error:
         - quaternion error encodes the axis of rotation and the angle required to correct it
         - points along the axis where rotation must occur for correction
    - [𝜔] : angular velocity
    - [L] : applied torque
    """

    # Tunable controller logic
    Kp = 2.0 # Increase if sluggish
    Kd = 2.0 # Increase if oscillating

    # Quaternion error
    q_error = quaternion_multiply(quaternion_conjugate(q), q_desired)

    # Vector part of quaternion error
    e = q_error[1:]

    """
    Calculates torque needed to be applied, control law.
    - The torque would come from reaction wheels, thrusters, etc.
    - Curretly modeling ideal case where any torque can be instantly applied

    - [Kp] : Proportional gain.
        - Tells controller to apply torque along axis to reduce error
        - Rotational Hooke's Law
    - [Kd] : Derivative gain,
        - Tells controller to resist the current angular velocity
        - Applies torque oppsoite to spin, rotational damping
        - Prevents oscillation
    """
    L = -Kp * e - Kd * w

    return L