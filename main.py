# External Libraries
import numpy as np
from scipy.integrate import solve_ivp

# Internal Functions
from dynamics import spacecraft_dynamics
from setup import get_initial_conditions
from animate import animate_cube
from orbitals import get_solar_system_data, load_kernels, clear_kernels
from visualize import plot_orientation, plot_system

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

    # Unpack initial conditions
    initial_conditions = get_initial_conditions()
    I = initial_conditions["I"]

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
    
    # Numerically integrate angular velocity
    sol = solve_ivp(
        fun=spacecraft_dynamics,
        t_span=[time_vec[0], time_vec[-1]],
        y0=y0,
        t_eval=time_vec,
        args=(I, I_inverse, start_et),
        method="DOP853",
        rtol=1e-10,
        atol=1e-12
    )

    # Extract vectors from ODE solution
    r = sol.y[0:3]
    v = sol.y[3:6]
    w = sol.y[6:9]
    q = sol.y[9:13]

    # Normalize quaternions for drift correction
    q = q / np.linalg.norm(q, axis=0)

    """ Pass calculated values to visualization functions """
    plot_orientation(time_vec, w, q) # Plots quaternions and angular velocities over time.
    animate_cube(time_vec, q) # Animates cube to represent orientation over time

    solar_system_data = get_solar_system_data(start_et, start_et + seconds_elapsed, time_steps) # Obtains position/velocity data for solar system with inputted time steps

    plot_system(solar_system_data, r) # Plots the satellite and solar system in 3D-space wrt time using Plotly

    clear_kernels() # good practice to clear

if __name__ == '__main__':
    main()