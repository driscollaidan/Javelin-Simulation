import matplotlib.pyplot as plt

def plot_orientation(t, w, q):

    """
    Outputs hard-coded plots for the following:
    - Angular Momentum Magnitude
    - Angular Velocities
    - Quaternions
    """

    # Graph angular velocities over time.
    plt.figure()
    plt.plot(t, w[0], label='$\omega_x$')
    plt.plot(t, w[1], label='$\omega_y$')
    plt.plot(t, w[2], label='$\omega_z$')
    plt.legend()
    plt.xlabel("Time (s)")
    plt.ylabel("Angular Velocity (rad/s)")

    # Graph quaternions over time.
    plt.figure()
    plt.plot(t, q[0], label='$\epsilon_1$')
    plt.plot(t, q[1], label='$\epsilon_2$')
    plt.plot(t, q[2], label='$\epsilon_3$')
    plt.plot(t, q[3], label='$\epsilon_4$')
    plt.legend()
    plt.xlabel("Time (s)")
    plt.ylabel("Quaternions")

    # Display plots
    plt.show()