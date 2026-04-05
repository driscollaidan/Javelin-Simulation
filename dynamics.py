import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline

from control import pd_control
from environment import calculate_gravitational_acceleration, calculate_gravity_gradient_torque
from attitude import EARTH_POINTING, SUN_POINTING, compute_guidance_quaternion, quaternion_to_dcm
from orbitals import get_body_position, get_body_grav_parameter

def simulate_6DoF(I, r0, v0, w0, q0, t0, bodies):
    """ 
    Simulates spacecraft orientation and position for 200 seconds.
    Required inputs:
    - I: diagonal inertia tensor for spacecraft.
    - r0: initial spacecraft position.
    - v0: initial spacecraft velocity.
    - w0: initial spacecraft angular veleocity.
    - q0: inital spacecraft orientation.
    - t0: simulation start time.
    - bodies: list of celestial bodies involved in calculations.

    TODO: Instead of retrieving celestial body data from kernels, have it retrieved from Orbitals 3DoF for spline calculations.
    TODO: Figure out how we want to determine w0 and q0, for sake of visualization.
    """
    dt = 200 # 6dof simulations always 200 seconds.
    t1 = t0 + dt # End time (Ephemeris)
    t_steps = 5 * dt
    t_vec = np.linspace(0, dt, t_steps)
    ets = np.linspace(t0, t1, t_steps)

    # Construct state vector of position, velocity, angular velocity and quaternion orientation
    y0 = np.concatenate((r0, v0, w0, q0))

    # Pre-calulate inverse, save computation time
    I_inverse = np.linalg.inv(I)

    # Get body position data for solar system bodies
    celestial_data = {}
    for body in bodies:
        body_data = []
        for et in ets:
            body_data.append(get_body_position(et, body)[:3])
        celestial_data[body.lower()] = {"r": np.array(body_data)}

    # Construct planetary splines.
    splines = {}
    for body in bodies:
        splines[body] = CubicSpline(t_vec, celestial_data[body]["r"])

    # Numerically integrate angular velocity
    sol = solve_ivp(
        fun=spacecraft_dynamics,
        t_span=[t_vec[0], t_vec[-1]],
        y0=y0,
        t_eval=t_vec,
        args=(I, I_inverse, splines),
        method="DOP853",
        rtol=1e-6,
        atol=1e-9
    )

    if not sol.success:
        print("Integration failed:", sol.message)

    # Extract vectors from ODE solution
    r = sol.y[0:3]
    v = sol.y[3:6]
    w = sol.y[6:9]
    q = sol.y[9:13]

    # Normalize quaternions for drift correction
    q /= np.linalg.norm(q, axis=0, keepdims=True)

    return r, v, w, q

def spacecraft_dynamics(t, y, I, I_inverse, splines):

    """
    Decouples angular velocity and quaternions from state vector
    - Performs angular accelerations calculation
    - Performs quaternion derivative
    - Returns combined derivatives

    r: Inertial Frame.
    I: Body Frame.
    """

    # Extract state
    r = y[0:3]
    v = y[3:6]
    w = y[6:9]
    q = y[9:13]

    # Normalize quaternion
    q = q / np.linalg.norm(q)

    """ TRANSLATIONAL DYNAMICS """
    C = quaternion_to_dcm(q)

    # Initialize zeros.
    a_total = np.zeros(3)
    L_total = np.zeros(3)

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
        a_total += calculate_gravitational_acceleration(r_dist, r_norm, mu)
        L_total += calculate_gravity_gradient_torque(r_norm, r_hat_body, mu, I)

    # Store derivatives.
    r_dot = v
    v_dot = a_total

    """ ATTITUDE DYNAMICS """
    # Placeholder, controller logic
    q_desired = compute_guidance_quaternion(EARTH_POINTING, r, splines["earth"](t), splines["sun"](t)) # Desired orientation after maneuver

    # Tunable controller logic
    Kp = 2.0 # Increase if sluggish
    Kd = 2.0 # Increase if oscillating

    L_total += pd_control(w, q, q_desired, Kp, Kd) # Calculate controller torques

    w_dot = rigid_body_dynamics(w, I, L_total, I_inverse)
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