from orbitals import load_kernels, clear_kernels
from gui_6dof import run_gui_6dof
from gui_3dof import run_gui_3dof

def main():
    """
    Make sure to run on Python 3.11.14
    """

    load_kernels() # Loads kernels to find celestial body positions
    # run_gui_3dof()
    run_gui_6dof()
    clear_kernels() # Good practice to clear kernels when done.

    """
    Should incorporate these graphs in 6dof GUI view.

    start_indexes, end_indexes = find_intervals(q)
    plot_orientation(time_vec, w, q, start_indexes, end_indexes)
    animate_spacecraft_attitude(time_vec, q, start_indexes, end_indexes) 
    """

if __name__ == '__main__':
    main()