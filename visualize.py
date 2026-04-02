import plotly.graph_objects as go
import numpy as np

from geometry import create_spacecraft, create_sphere
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

    return [surface]

def get_spacecraft_6dof_frame(r, q, vertices_body, faces):
    """
    Renders position and orientation of spacecraft 3D model for visualization.
    """
    spacecraft = get_spacecraft_inertial(
        vertices_body * SPACECRAFT_SCALE,
        r,
        q
    )

    frame = go.Mesh3d(
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

    return [frame]

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

""" ==================================================================================================================================== # 
#                                                                                                                                        #
#   Legacy functions.                                                                                                                    #
#   - plot_system                                                                                                                        #
#   - display_plot                                                                                                                       #
#                                                                                                                                        #       
#   Were previously used for generating and displaying solar system plots. Keeping in file (for now) in case needed.                     #
#   Being replaced with Plotly Dash GUI.                                                                                                 #
#                                                                                                                                        #
# ==================================================================================================================================== """

SPACECRAFT_TRAJECTORY_MODE = 0
SPACECRAFT_ORIENTATION_MODE = 1

# -------------------------------------------------------------------------------------------------------------------------------------- #
#   Legacy coordination wrapper.                                                                                                         #
# -------------------------------------------------------------------------------------------------------------------------------------- #

def plot_system(solar_system_data, spacecraft_position, spacecraft_orientation, mode):
    """
    Legacy coordination function for generating three-dimensional solar system plots.
    - Being replaced with GUI logic, built with Plotly Dash.
    """
    bodies = list(solar_system_data.keys()) # earth, venus, jupiter, europa, sun
    length = len(solar_system_data[bodies[0]]["r"]) # should be equal to time_steps

    # Create figure
    fig = go.Figure()

    """ Placeholder geometry, will replace later """
    # Generate spacecraft geometry
    vertices_body, faces = create_spacecraft()

    """ Create inital traces for first frame """
    # Get initial cube vertices in inertial frame for first frame of animation
    satellite_traces = []
    if mode == SPACECRAFT_ORIENTATION_MODE:
        satellite_traces.append(get_spacecraft_6dof_frame(spacecraft_position[:,0], spacecraft_orientation[:,0],  vertices_body, faces))
    elif mode == SPACECRAFT_TRAJECTORY_MODE:
        satellite_traces.extend(get_spacecraft_3dof_frame(spacecraft_position[:,0], spacecraft_position[0,:1], spacecraft_position[1,:1], spacecraft_position[2,:1]))

    # Create traces for initial positions
    celestial_traces = []
    for body in bodies:
        r = solar_system_data[body]["r"][0]
        if mode == SPACECRAFT_ORIENTATION_MODE:
            celestial_traces.append(get_celestial_6dof_frame(body, r))
        elif mode == SPACECRAFT_TRAJECTORY_MODE:
            x_trail = solar_system_data[body]["r"][:1,0]
            y_trail = solar_system_data[body]["r"][:1,1]
            z_trail = solar_system_data[body]["r"][:1,2]
            celestial_traces.extend(get_celestial_3dof_frame(body, r, x_trail, y_trail, z_trail))

    # Initial frame with satellite and celestial bodies, then frames will update these traces to create animation
    for trace in satellite_traces:
        fig.add_trace(trace)
    for trace in celestial_traces:
        fig.add_trace(trace)
    
    """ Create additional frames for animation """
    frames = []
    for i in range(length):
        frame_data = [] # All data for a speciific frame goes here, then added to frames list
        
        if mode == SPACECRAFT_ORIENTATION_MODE:
            frame_data.append(get_spacecraft_6dof_frame(spacecraft_position[:,i], spacecraft_orientation[:,i], vertices_body, faces))
        elif mode == SPACECRAFT_TRAJECTORY_MODE:
            x_trail = spacecraft_position[0,:i+1]
            y_trail = spacecraft_position[1,:i+1]
            z_trail = spacecraft_position[2,:i+1]
            frame_data.extend(get_spacecraft_3dof_frame(spacecraft_position[:,i], x_trail, y_trail, z_trail))

        for body in bodies:
            r = solar_system_data[body]["r"][i]
            if mode == SPACECRAFT_ORIENTATION_MODE:
                frame_data.append(get_celestial_6dof_frame(body, r)) 
            elif mode == SPACECRAFT_TRAJECTORY_MODE:
                x_trail = solar_system_data[body]["r"][:i+1,0]
                y_trail = solar_system_data[body]["r"][:i+1,1]
                z_trail = solar_system_data[body]["r"][:i+1,2]
                frame_data.extend(get_celestial_3dof_frame(body, r, x_trail, y_trail, z_trail))

        # Makes a plotly frame from the data, adds to list
        frames.append(
            go.Frame(
                data=frame_data,
                name=str(i),
            )
        ) 

    fig.frames = frames # After collecting all frames, applies them to the figure
    display_plot(fig, length) # Calls function to add sliders/buttons and show figure

# -------------------------------------------------------------------------------------------------------------------------------------- #
#   Legacy display settings/call.                                                                                                        #
# -------------------------------------------------------------------------------------------------------------------------------------- #

def display_plot(fig, length):
    """
    Legacy function for displaying plotly generated graphs from the coordination system plotting function.
    """
    # Create slider steps for frame swaps, alloing for scrollable timeline
    sliders = [{
        "currentvalue": {"prefix": "Step: "},
        "pad": {"t": 50},
        "steps": [
            {
                "args": [
                    [str(i)],
                    {
                        "frame": {"duration": 0, "redraw": True},
                        "mode": "immediate"
                    }
                ],
                "label": str(i),
                "method": "animate"
            }
            for i in range(length)
        ]
    }]    

    # Adds play/pause buttons for automatic animation
    updatemenus = [{
        "type": "buttons",
        "direction": "left",
        "pad": {"r": 10, "t": 70},
        "showactive": False,
        "buttons": [
            {
                "label": "Play",
                "method": "animate",
                "args": [
                    None,
                    {
                        "frame": {"duration": 20, "redraw": True},
                        "fromcurrent": True,
                        "transition": {"duration": 0}
                    }
                ]
            },
            {
                "label": "Pause",
                "method": "animate",
                "args": [
                    [None],
                    {
                        "frame": {"duration": 0, "redraw": False},
                        "mode": "immediate",
                        "transition": {"duration": 0}
                    }
                ]
            }
        ]
    }]
    
    # Updates the figure to apply slider and buttons to it
    fig.update_layout(
        scene=dict(
            xaxis_title="X (km)",
            yaxis_title="Y (km)",
            zaxis_title="Z (km)",
            aspectmode="data"
        ),
        sliders=sliders,
        updatemenus=updatemenus
    )

    fig.show()

# -------------------------------------------------------------------------------------------------------------------------------------- #
#   animate_spacecraft_attitude()                                                                                                        #
# -------------------------------------------------------------------------------------------------------------------------------------- #

def animate_spacecraft_attitude(t, q, start_index, end_index):
    """  
    Animates/visualizes orientation of spacecraft without referenece to surrounding bodies.
    - Simply generates model and spins it according to mission quaternions.
    - Not used within main visualization structure.
    - TODO: Include as display in GUI.
    """
    # Generate spacecraft geometry
    vertices_body, faces = create_spacecraft()

    for i in range(len(start_index)):

        interval = range(start_index[i], end_index[i])
        fig = go.Figure()

        # Initial frame with satellite, then frames will update these traces to create animation
        fig.add_trace(get_spacecraft_6dof_frame(np.zeros(3), q[:,start_index[i]], vertices_body, faces))

        # Only rotating spacecraft, position is fixed at origin for this animation, to better visualize attitude changes.
        frames = []
        for j in interval:
            frames.append(
                go.Frame(
                    data=get_spacecraft_6dof_frame(np.zeros(3), q[:,j], vertices_body, faces),
                    name=str(j)
                )
            )

        fig.update_layout(
            title=f"Spacecraft Attitude | Interval {[i]} | t={t[start_index[i]]:.2f}-{t[end_index[i]-1]:.2f}s"
        )
        
        fig.frames = frames
        display_plot(fig, len(interval))