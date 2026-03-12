# External Libraries
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline

# Internal Functions
from dynamics import spacecraft_dynamics
from setup import CUSTOM_SIMULATION, ACQUISITION_SIMULATION, get_conditions
from orbitals import get_body_position, load_kernels, clear_kernels
from visualize import plot_system, animate_spacecraft_attitude
from graphing import plot_orientation, find_intervals

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
    mission_conditions = get_conditions(ACQUISITION_SIMULATION)
    
    I = mission_conditions["I"]

    physics_bodies = mission_conditions["physics_bodies"]
    visualization_bodies = mission_conditions["visualization_bodies"]

    simulation_time = mission_conditions["simulation_time"]
    start_et = mission_conditions["start_et"]

    r0 = mission_conditions["r0"]   
    v0 = mission_conditions["v0"]   
    w0 = mission_conditions["w0"]
    q0 = mission_conditions["q0"]

    # Construct state vector of position, velocity, angular velocity and quaternion orientation
    y0 = np.concatenate((r0, v0, w0, q0))

    # Pre-calulate inverse, save computation time
    I_inverse = np.linalg.inv(I)
    
    # Define time vector for simulation with desired step size.
    time_steps = int (2.5 * simulation_time)
    time_vec = np.linspace(0, simulation_time, time_steps)

    # Get body position data for solar system bodies
    celestial_data = {}
    ets = np.linspace(start_et, start_et + simulation_time, time_steps)
    for body in physics_bodies:
        body_data = []
        for et in ets:
            body_data.append(get_body_position(et, body)[:3])
        celestial_data[body.lower()] = {"r": np.array(body_data)}

    earth_spline = CubicSpline(time_vec, celestial_data["earth"]["r"])
    sun_spline = CubicSpline(time_vec, celestial_data["sun"]["r"])

    # Numerically integrate angular velocity
    sol = solve_ivp(
        fun=spacecraft_dynamics,
        t_span=[time_vec[0], time_vec[-1]],
        y0=y0,
        t_eval=time_vec,
        args=(I, I_inverse, earth_spline, sun_spline),
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

    # Trim dictionary down to just bodies needed for visualization.
    for key in physics_bodies:
        if key not in visualization_bodies:
            del celestial_data[key.lower()]

    """ Pass calculated values to visualization functions """
    start_indexes, end_indexes = find_intervals(q)
    plot_orientation(time_vec, w, q, start_indexes, end_indexes) # Plots quaternions and angular velocities over time.
    animate_spacecraft_attitude(time_vec, q, start_indexes, end_indexes) # Animates cube to represent orientation over time
    plot_system(celestial_data, r, q) # Plots the satellite and solar system in 3D-space wrt time using Plotly

    clear_kernels() # good practice to clear

if __name__ == '__main__':
    main()