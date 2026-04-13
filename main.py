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

if __name__ == '__main__':
    main()

# TODO. Establish more data for telemetry !!!
#   - Return each environmental and internal torque
#   - Include gain and phase margins
#   - Display slew rates, poiniing accuracy, power usgage, and stability.
# TODO. Imrpove geometry for surfaces and model.
# TODO. Implement mission modes, defining pointing requirements and variable conditions for each