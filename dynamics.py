import numpy as np

from control import pd_control
from environment import gravitational_acceleration

def spacecraft_dynamics(t, y, I, I_inverse, start_et):

    """
    Decouples angular velocity and quaternions from state vector
    - Performs angular accelerations calculation
    - Performs quaternion derivative
    - Returns combined derivatives
    """

    # Extract state
    r = y[0:3]
    v = y[3:6]
    w = y[6:9]
    q = y[9:13]

    """ TRANSLATIONAL DYNAMICS """
    # Ephemeris time
    et = start_et + t
    a = gravitational_acceleration(r, et)
    r_dot = v
    v_dot = a

    """ ATTITUDE DYNAMICS """
    # Placeholder, controller logic
    q_desired = np.array([1,0,0,0]) # Desired orientation after maneuver

    # Tunable controller logic
    Kp = 2.0 # Increase if sluggish
    Kd = 2.0 # Increase if oscillating

    L_control = pd_control(w, q, q_desired, Kp, Kd) # Calculate controller torques

    w_dot = rigid_body_dynamics(w, I, L_control, I_inverse)
    q_dot = quaternion_derivative(w, q)

    """ RETURN UPDATED STATE VECTOR """
    return np.concatenate((r_dot, v_dot, w_dot, q_dot))

def rigid_body_dynamics(w, I, L, I_inverse):

    """
    Integrates angular velocity for rigid body.
    - Uses pre-calculated inverse
    """

    Iw = I @ w 
    w_cross_Iw = np.cross(w, Iw)
    w_dot = I_inverse @ (L - w_cross_Iw)
    return w_dot

def quaternion_derivative(w, q):
    
    """
    Calculates time derivative of quaternions.
    - Relative to angular velocity in body frame.
    """
      
    Omega = np.array([
        [0,      -w[0], -w[1], -w[2]],
        [w[0],    0,     w[2], -w[1]],
        [w[1],   -w[2],  0,     w[0]],
        [w[2],    w[1], -w[0],  0]
    ])

    q_dot = 0.5 * Omega @ q

    # Correct quaternion drift during ODE calculation
    q_dot -= q * (np.dot(q, q) - 1) * 10

    return q_dot