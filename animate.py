import matplotlib.pyplot as plt

from attitude import quaternion_to_dcm
from geometry import create_cube

""" 
THIS FILE IS COMPLETELY VIBE CODED 
Esentially just a placeholder to model a simple three-dimensional object in spacae.
Will eventually write out logic to define the shape of our spacecraft
    - Modeling spacecraft will loosely match the actual one, with key features to demonstrate pointing and operational modes
    - Momemnts of inertia will be determined from actual craft
TODO
Learn to implement similar logic.
Define a mesh and include it within the orbital simulation.
"""

from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

def animate_cube(t, q):

    vertices_body, edges = create_cube(size=1.0)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.set_xlim([-1.5,1.5])
    ax.set_ylim([-1.5,1.5])
    ax.set_zlim([-1.5,1.5])

    ax.set_box_aspect([1,1,1])

    lines = []

    for edge in edges:
        line, = ax.plot([], [], [], 'k')
        lines.append(line)

    def update(frame):

        C = quaternion_to_dcm(q[:, frame])
        vertices_inertial = (C @ vertices_body.T).T

        for line, edge in zip(lines, edges):
            points = vertices_inertial[list(edge)]
            line.set_data(points[:,0], points[:,1])
            line.set_3d_properties(points[:,2])

        return lines

    ani = FuncAnimation(
        fig,
        update,
        frames=len(t),
        interval=30,
        blit=False
    )

    plt.show()