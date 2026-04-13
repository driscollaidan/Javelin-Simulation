import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline

from control import pd_control
from environment import get_environmental_effects
from attitude import EARTH_POINTING, SUN_POINTING, compute_guidance_quaternion, quaternion_to_dcm
from orbitals import get_body_position
from geometry import create_spacecraft_surfaces

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

    # Spacecraft geometry surfaces
    surfaces = create_spacecraft_surfaces()

    # Numerically integrate angular velocity
    sol = solve_ivp(
        fun=spacecraft_dynamics,
        t_span=[t_vec[0], t_vec[-1]],
        y0=y0,
        t_eval=t_vec,
        args=(I, I_inverse, splines, surfaces),
        method="RK45",
        rtol=1e-12,
        atol=1e-12
    )

    if not sol.success:
        print("Integration failed:", sol.message)

    # Post-processing computation for torques
    telemetry_log = compute_telemetry(sol, I, splines, surfaces, t_vec)

    # Extract vectors from ODE solution
    r = sol.y[0:3]
    v = sol.y[3:6]
    w = sol.y[6:9]
    q = sol.y[9:13]

    # Normalize quaternions for drift correction
    q /= np.linalg.norm(q, axis=0, keepdims=True)

    return r, v, w, q, telemetry_log

def spacecraft_dynamics(t, y, I, I_inverse, splines, surfaces):

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
    L_gg, L_mag, L_srp, a_gg = get_environmental_effects(C, t, r, I, splines, surfaces)

    # Store derivatives.
    r_dot = v
    v_dot = a_gg

    """ ATTITUDE DYNAMICS """
    # Placeholder, controller logic
    q_desired = compute_guidance_quaternion(EARTH_POINTING, r, splines["earth"](t), splines["sun"](t)) # Desired orientation after maneuver

    L_control = pd_control(w, q, q_desired) # Calculate controller torques

    L_total = L_gg + L_mag + L_srp + L_control

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

def compute_telemetry(sol, I, splines, surfaces, t_vec):
    """
    Recompute all torques from ODE.
    - Doing so allows for accurate plotting of torque components, without burdening ODE.
    """
    n = len(t_vec)

    gg = np.zeros((3, n))
    mag = np.zeros((3, n))
    srp = np.zeros((3, n))
    ctrl = np.zeros((3, n))
    total = np.zeros((3, n))

    for i, t in enumerate(t_vec):

        r = sol.y[0:3, i]
        w = sol.y[6:9, i]
        q = sol.y[9:13, i]
        q = q / np.linalg.norm(q)

        C = quaternion_to_dcm(q)
        L_gg, L_mag, L_srp, _ = get_environmental_effects(C, t, r, I, splines, surfaces)

        q_desired = compute_guidance_quaternion(EARTH_POINTING, r, splines["earth"](t), splines["sun"](t))
        L_ctrl = pd_control(w, q, q_desired)

        L_tot = L_gg + L_mag + L_srp + L_ctrl

        gg[:, i] = L_gg
        mag[:, i] = L_mag
        srp[:, i] = L_srp
        ctrl[:, i] = L_ctrl
        total[:, i] = L_tot

    return {
        "t": t_vec,
        "gg": gg,
        "mag": mag,
        "srp": srp,
        "ctrl": ctrl,
        "total": total
    }