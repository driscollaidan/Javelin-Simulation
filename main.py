# External Libraries
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline

# Internal Functions
from dynamics import spacecraft_dynamics
from setup import get_conditions
from orbitals import get_body_position, load_kernels, clear_kernels
from visualize import plot_system, animate_spacecraft_attitude
from graphing import plot_orientation

"""
TODO
Looking into next area of development.
The best solution, as identfied in orbitals notes, is to have the code generate orientations for different brief simulation.
- Have the program query the simulation to be calculated (i.e., launch, earth orbit, transfer, approach)
    - Define initial conditions for each case, specifically initial state vector
        - Can add a degree of randomness for this
    - Define controller operations for each simulation case
        - Mission modes, pointinng requirements per mode
        - Define simulated maneuvers for each orientation change, using realistic reaction wheels/gas jets
    - Add reasonable environmental torques/effects dependent on case.
"""

def main():

    load_kernels() # Loads kernels to find celestial body positions

    # Unpack mission conditions
    initial_conditions = get_conditions()
    I = initial_conditions["I"]

    bodies = initial_conditions["bodies"]

    time_vec = initial_conditions["time_vec"]
    time_steps = initial_conditions["time_steps"]
    seconds_elapsed = initial_conditions["seconds_elapsed"]
    start_et = initial_conditions["start_et"]

    r0 = initial_conditions["r0"]   
    v0 = initial_conditions["v0"]   
    w0 = initial_conditions["w0"]
    q0 = initial_conditions["q0"]

    # Construct state vector of position, velocity, angular velocity and quaternion orientation
    y0 = np.concatenate((r0, v0, w0, q0))

    # Pre-calulate inverse, save computation time
    I_inverse = np.linalg.inv(I)
    
    # Get body position data for solar system bodies
    celestial_data = {}
    ets = np.linspace(start_et, start_et + seconds_elapsed, time_steps)
    for body in bodies:
        body_data = []
        for et in ets:
            body_data.append(get_body_position(et, body)[:3])
        celestial_data[body.lower()] = {"r": np.array(body_data)}

    earth_spline = CubicSpline(time_vec, celestial_data["earth"]["r"])
    sun_spline   = CubicSpline(time_vec, celestial_data["sun"]["r"])

    # Numerically integrate angular velocity
    sol = solve_ivp(
        fun=spacecraft_dynamics,
        t_span=[time_vec[0], time_vec[-1]],
        y0=y0,
        t_eval=time_vec,
        args=(I, I_inverse, earth_spline, sun_spline),
        method="DOP853",
        rtol=1e-9,
        atol=1e-9
    )

    # Extract vectors from ODE solution
    r = sol.y[0:3]
    v = sol.y[3:6]
    w = sol.y[6:9]
    q = sol.y[9:13]

    # Normalize quaternions for drift correction
    q /= np.linalg.norm(q, axis=0, keepdims=True)

    """ TEMP: VISUALIZATION WITH JUST EARTH """
    # Get body position data for solar system bodies
    bodies = ["EARTH"]
    celestial_data = {}
    ets = np.linspace(start_et, start_et + seconds_elapsed, time_steps)
    for body in bodies:
        body_data = []
        for et in ets:
            body_data.append(get_body_position(et, body)[:3])
        celestial_data[body.lower()] = {"r": np.array(body_data)} 

    """ Pass calculated values to visualization functions """
    # plot_orientation(time_vec, w, q) # Plots quaternions and angular velocities over time.
    animate_spacecraft_attitude(time_vec, q) # Animates cube to represent orientation over time
    plot_system(celestial_data, r, q) # Plots the satellite and solar system in 3D-space wrt time using Plotly

    clear_kernels() # good practice to clear

if __name__ == '__main__':
    main()