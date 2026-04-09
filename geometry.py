import numpy as np

"""
Spacecraft Geometry Definition (Consistent with Structures Team Notes)

All dimensions are in meters unless otherwise specified.

MAIN BODY (Bus):
- Shape: Rectangular prism (approximation of two stacked aluminum cylinders)
- Height (Z): 3.0 m
- Width (Y): 1.5 m
- Depth (X): 1.5 m (assumed symmetric with width)

SOLAR ARRAYS:
- Configuration: 2 wings (port and starboard), mounted along ±Y faces of bus
- Each wing consists of 5 panels (modeled here as a single equivalent surface per wing)
- Individual panel dimensions: 4.13 m (height) × 2.47 m (length)
- Total deployed length per wing: ~14.1 m
- Modeled dimensions per wing: 14.1 m (length, X-direction) × 4.13 m (height, Z-direction)

ANTENNA:
- Type: Circular dish
- Diameter: 3.0 m
- Mounting location: Side-mounted on bus (modeled along +X face)

MODEL NOTES:
- Geometry is simplified for simulation purposes
- Solar panels are aggregated into single surfaces per wing for radiation pressure calculations
- Bus is modeled as a rectangular prism instead of cylindrical stack for consistency between mesh and force models
- Surface definitions are aligned with mesh geometry to ensure consistent force/torque calculations

COORDINATE SYSTEM:
- Origin at center of spacecraft bus
- +X: nominal forward / antenna-facing direction
- +Y: starboard (right wing), -Y: port (left wing)
- +Z: upward along spacecraft body axis
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

def box_surfaces(dims):
    """
    dims: (L, W, H)
    """
    L, W, H = dims
    x, y, z = L/2, W/2, H/2

    faces = [
        # +X
        {"normal": np.array([1,0,0]), "area": W*H, "r_cp": np.array([x,0,0])},
        # -X
        {"normal": np.array([-1,0,0]), "area": W*H, "r_cp": np.array([-x,0,0])},

        # +Y
        {"normal": np.array([0,1,0]), "area": L*H, "r_cp": np.array([0,y,0])},
        # -Y
        {"normal": np.array([0,-1,0]), "area": L*H, "r_cp": np.array([0,-y,0])},

        # +Z
        {"normal": np.array([0,0,1]), "area": L*W, "r_cp": np.array([0,0,z])},
        # -Z
        {"normal": np.array([0,0,-1]), "area": L*W, "r_cp": np.array([0,0,-z])},
    ]

    return faces

def panel_surface(root, span_vec, height_vec):
    """
    root: attachment point in body frame
    span_vec: panel length direction
    height_vec: panel height direction (normal × span)
    """

    span = np.linalg.norm(span_vec)
    height = np.linalg.norm(height_vec)

    n_hat = np.cross(span_vec, height_vec)
    n_hat = n_hat / np.linalg.norm(n_hat)

    r_cp = root + 0.5 * span_vec + 0.5 * height_vec

    return {
        "normal": n_hat,
        "area": span * height,
        "r_cp": r_cp
    }

def create_spacecraft_surfaces():
    L, W, H = 1.5, 1.5, 3.0
    r = np.array([0,0,0])

    surfaces = []

    # bus
    surfaces += box_surfaces((L,W,H))

    # solar panels (+Y wing)
    surfaces.append(
        panel_surface(
            root=np.array([0, W/2, 0]),
            span_vec=np.array([5.0, 0, 0]),
            height_vec=np.array([0, 0, 2.0])
        )
    )

    # solar panels (-Y wing)
    surfaces.append(
        panel_surface(
            root=np.array([0, -W/2, 0]),
            span_vec=np.array([5.0, 0, 0]),
            height_vec=np.array([0, 0, 2.0])
        )
    )

    return surfaces