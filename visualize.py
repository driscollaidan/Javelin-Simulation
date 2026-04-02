import plotly.graph_objects as go
import numpy as np

from geometry import create_sphere
from attitude import get_spacecraft_inertial

# Constants for altering scale of planets, space, and spacecraft for visualiation purposes
POSITION_SCALE = 4              # Global compression of positions, shrinks entire coordinate space. Large value, everything closer. Small value, more spread out.
SPACECRAFT_SCALE = 0.5          # Increasees the size of spacecraft geometry by a factor. Also alters unit vector pointing scale.
VISUAL_SCALE = .5               # Controls rendered size of spheres, affects only how big objects look.
PLANET_SCALE = 1                # Increases the size of small planets by a factor.

BODY_PROPERTIES = {
    "sun": {"radius":696340, "color":"yellow", "marker":20},
    "earth": {"radius":6371*PLANET_SCALE, "color":"blue", "marker":5},
    "venus": {"radius":6052*PLANET_SCALE, "color":"orange", "marker":4},
    "jupiter": {"radius":69911,  "color":"brown", "marker":10},
    "europa": {"radius":1560*PLANET_SCALE, "color":"white", "marker":3},
    "moon": {"radius":1737*PLANET_SCALE, "color":"gray", "marker":3},
    "mercury": {"radius":2440*PLANET_SCALE, "color":"tan", "marker":3},
}

# -------------------------------------------------------------------------------------------------------------------------------------- #
#   6DoF Frame Construction funtions.                                                                                                    #
# -------------------------------------------------------------------------------------------------------------------------------------- #

def build_6dof_frame(r_sc, q_sc, vertices_body, faces, r_planets, bodies):
    """
    Calls visualization functions to construct animation frames for 6DoF mode.
    - Renders detailed spheres for celestial bodies.
    - Renders three-dimensional spacecraft structure.
    - TODO: Look into excluding bodies that will make dimensions too large.
    """

    r_sc_scaled = (r_sc / POSITION_SCALE)

    r_planets_scaled = {
        body: (r_planets[body] / POSITION_SCALE)
        for body in r_planets
    }

    traces = []

    traces.extend(
        get_spacecraft_6dof_frame(
            r_sc_scaled ,
            q_sc,
            vertices_body,
            faces
        )
    )
    
    for body in bodies:
        traces.extend(
            get_celestial_6dof_frame(
                body, 
                r_planets_scaled[body]
            )
        )

    return traces

def get_celestial_6dof_frame(body, r):
    """
    Renders an accurately-sized sphere to plot planetary bodies in 3D space.
    """
    x, y, z = create_sphere(r, (BODY_PROPERTIES[body]["radius"] / POSITION_SCALE) * VISUAL_SCALE)

    surface = go.Surface(
        x=x,
        y=y,
        z=z,
        showscale=False,
        surfacecolor=np.zeros_like(x),
        colorscale=[
            [0, BODY_PROPERTIES[body]["color"]],
            [1, BODY_PROPERTIES[body]["color"]]
        ],
        name=body.capitalize(),
        opacity=1,
        showlegend=True,
        legendgroup=body         
    )

    marker = go.Scatter3d(
        x=[r[0]],
        y=[r[1]],
        z=[r[2]],
        mode="markers",
        marker=dict(
            size=BODY_PROPERTIES[body]["marker"] * 2,  # boost visibility
            color=BODY_PROPERTIES[body]["color"]
        ),
        name=body.capitalize(),
        legendgroup=body,
        showlegend=False  # IMPORTANT: avoids duplicate legend entries
    )

    return [surface, marker]

def get_spacecraft_6dof_frame(r, q, vertices_body, faces):
    """
    Renders position and orientation of spacecraft 3D model for visualization.
    """
    spacecraft = get_spacecraft_inertial(
        vertices_body * SPACECRAFT_SCALE,
        r,
        q
    )

    mesh = go.Mesh3d(
        x=spacecraft[:,0],
        y=spacecraft[:,1],
        z=spacecraft[:,2],

        i=faces[:,0],
        j=faces[:,1],
        k=faces[:,2],

        color="silver",
        opacity=1,
        flatshading=True,
        showscale=False,
        name="Spacecraft",
        showlegend=True
    )

    marker = go.Scatter3d(
        x=[r[0]],
        y=[r[1]],
        z=[r[2]],
        mode="markers",
        marker=dict(size=6, color="silver"),
        name="Spacecraft",
        legendgroup="spacecraft",
        showlegend=False
    )

    return [mesh, marker]

def get_pointing_traces(r_sc, r_planets, bodies):

    pointing_traces = []
    for body in bodies:
        vec = r_planets[body] - r_sc
        unit_vec = vec / np.linalg.norm(vec)
        vec_sized = unit_vec * 1500 * SPACECRAFT_SCALE

        pointing_traces.append(go.Scatter3d(
            x=[vec_sized[0]],
            y=[vec_sized[1]],
            z=[vec_sized[2]],
            mode="markers",
            marker=dict(size=10, color=BODY_PROPERTIES[body]["color"]),
            name=f"{body.capitalize()}"
        ))

    return pointing_traces

def get_full_system_bounds_trace(scale=6e7):

    corners = np.array([
        [ scale,  scale,  scale],
        [-scale,  scale,  scale],
        [ scale, -scale,  scale],
        [ scale,  scale, -scale],
        [-scale, -scale,  scale],
        [-scale,  scale, -scale],
        [ scale, -scale, -scale],
        [-scale, -scale, -scale],
    ])

    return go.Scatter3d(
        x=corners[:,0],
        y=corners[:,1],
        z=corners[:,2],
        mode="markers",
        marker=dict(
            size=1,
            color="white",
            opacity=0.01
        ),
        name="Show Space",
        legendgroup="full_system",
        showlegend=True
    )
    
# -------------------------------------------------------------------------------------------------------------------------------------- #
#   3DoF Frame Construction funtions.                                                                                                    #
# -------------------------------------------------------------------------------------------------------------------------------------- #

def build_3dof_frame(r_planets, spacecraft_position, traj):
    """
    Calls visualization functions to construct animation frames for 3DoF mode.
    - Makes markers for spacecraft and celestial bodies.
    - TODO: Investigate scaling down the graph, and/or forcing 2D-adjacent (easier to visualize).
    - TODO: Implement trails for the markers.
    - TODO: Un-Comment spacecraft position part.
    """
    traces = []

    for body, r in r_planets.items():
        traces.extend(get_celestial_3dof_frame(body, r))

    traces.extend(
        get_spacecraft_3dof_frame(spacecraft_position, traj)
    )

    return traces

def get_celestial_3dof_frame(body, r):
    """
    Constructs marker used for plotting celestial body position in 3DoF mode.
    - TODO: Implement trails.
    """
    body_frame = go.Scatter3d(
        x=[r[0]],
        y=[r[1]],
        z=[r[2]],
        mode="markers",
        marker=dict(size=BODY_PROPERTIES[body]["marker"], color=BODY_PROPERTIES[body]["color"]),
        name=body,
        showlegend=True
    )

    return [body_frame]

def get_spacecraft_3dof_frame(r, traj):
    """
    Constructs marker used for plotting spacecraft position in 3DoF mode.
    - TODO: Implement trails.
    """
    marker = go.Scatter3d(
            x=[r[0]],
            y=[r[1]],
            z=[r[2]],
            mode="markers",
            marker=dict(size=2, color="red", symbol="circle"),
            name="Spacecraft",
            showlegend=True
        )

    trajectory = go.Scatter3d(
        x=traj[:, 0],
        y=traj[:, 1],
        z=traj[:, 2],
        mode="lines",
        line=dict(width=2),
        name="Spacecraft Trajectory",
        showlegend=True
    )

    return [marker, trajectory]