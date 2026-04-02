import numpy as np

""" 
Generic spacecraft geometry.
Can be updated to better match specific craft.
"""

def create_spacecraft():

    # Bus size
    bx, by, bz = 120, 100, 140

    # Solar panels
    px = 500
    py = 150

    # Antenna
    antenna_length = 600

    # ---- BUS VERTICES ----
    bus = np.array([
        [-bx,-by,-bz],
        [ bx,-by,-bz],
        [ bx, by,-bz],
        [-bx, by,-bz],

        [-bx,-by, bz],
        [ bx,-by, bz],
        [ bx, by, bz],
        [-bx, by, bz]
    ])

    # ---- PANELS ----
    left_panel = np.array([
        [-bx-px,-py,0],
        [-bx,-py,0],
        [-bx,py,0],
        [-bx-px,py,0]
    ])

    right_panel = np.array([
        [bx,-py,0],
        [bx+px,-py,0],
        [bx+px,py,0],
        [bx,py,0]
    ])

    # ---- ANTENNA DISH ----
    theta = np.linspace(0,2*np.pi,16)

    dish = np.column_stack([
        40*np.cos(theta),
        40*np.sin(theta),
        np.full_like(theta, bz+antenna_length)
    ])

    antenna_base = np.array([[0,0,bz]])

    vertices = np.vstack([
        bus,
        left_panel,
        right_panel,
        antenna_base,
        dish
    ])

    # ---- TRIANGLES ----
    faces = [

        # Bus
        [0,1,2],[0,2,3],
        [4,5,6],[4,6,7],

        [0,1,5],[0,5,4],
        [1,2,6],[1,6,5],
        [2,3,7],[2,7,6],
        [3,0,4],[3,4,7],

        # Panels
        [8,9,10],[8,10,11],
        [12,13,14],[12,14,15],
    ]

    # Dish triangles
    base = 16
    center = base

    for i in range(1,16):
        faces.append([center, base+i, base+i+1])

    faces.append([center, base+16, base+1])

    faces = np.array(faces)

    return vertices, faces

def create_sphere(center, radius, resolution=25):

    u = np.linspace(0, 2*np.pi, resolution)
    v = np.linspace(0, np.pi, resolution)

    x = radius * np.outer(np.cos(u), np.sin(v)) + center[0]
    y = radius * np.outer(np.sin(u), np.sin(v)) + center[1]
    z = radius * np.outer(np.ones(np.size(u)), np.cos(v)) + center[2]

    return x, y, z