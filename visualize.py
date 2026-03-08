import plotly.graph_objects as go
import numpy as np

from geometry import create_cube, create_sphere
from attitude import get_spacecraft_inertial

"""
TODO
Known Ideas/Issues
- Allow panning/zooming over 3D-space
- 1000 timesteps seems for iterating over ten year span for orbital visualizations
- Change time-bar at the bottom to show dates/years
- Change planet marker/sizes appropriately
- Include satellite
    - By default, the camera should be focused on the satellite, and zoomed appropriately

The satellite orientation is currently being integrated over small time frames,
such as 200 seconds, with 0.2s step sizes. The orbital visualization takes place
over 10-years, only doing 1000 steps (still). There is a major discrepancy in what's possible to model
in terms of satellite data and solar system data.

Proposed solutions?
- Separate simulation times for attitude dynamics, orbital emphemeris, and animation framees.
    - Interpolate when necessary.
- Downscale time-length of orbital simulation
    - For spacecraft maneuver visualization, a day, or even hours, could be enough.
    - Can divide into mission segments, such as launch, earth orbit, transfer, approach
    - Create brief simulations for each.

"""

def plot_system(solar_system_data, spacecraft_position, spacecraft_orientation):
    
    bodies = list(solar_system_data.keys()) # earth, venus, jupiter, europa, sun
    length = len(solar_system_data[bodies[0]]["r"]) # should be equal to time_steps

    # Create figure
    fig = go.Figure()

    """ Create inital traces for first frame """
    # Get initial cube vertices in inertial frame for first frame of animation
    satellite_trace = get_spacecraft_frame(spacecraft_position[:,0], spacecraft_orientation[:,0])

    # Create traces for initial positions
    celestial_traces = []
    for body in bodies:
        r = solar_system_data[body]["r"][0]
        celestial_traces.extend(get_celestial_frame(body, r, [r[0]], [r[1]], [r[2]])) 

    # Initial frame with satellite and celestial bodies, then frames will update these traces to create animation
    fig.add_trace(satellite_trace)
    for trace in celestial_traces:
        fig.add_trace(trace)
    
    """ Create additional frames for animation """
    frames = []
    for i in range(length):
        frame_data = [] # All data for a speciific frame goes here, then added to frames list
        
        frame_data.append(get_spacecraft_frame(spacecraft_position[:,i], spacecraft_orientation[:,i]))
        
        for body in bodies:
            r = solar_system_data[body]["r"][i]
            x_trail = solar_system_data[body]["r"][:i+1,0]
            y_trail = solar_system_data[body]["r"][:i+1,1]
            z_trail = solar_system_data[body]["r"][:i+1,2]
            frame_data.extend(get_celestial_frame(body, r, x_trail, y_trail, z_trail)) 
            
        # Makes a plotly frame from the data, adds to list
        frames.append(go.Frame(data=frame_data, name=str(i),)) 

    fig.frames = frames # After collecting all frames, applies them to the figure
    display_plot(fig, length) # Calls function to add sliders/buttons and show figure

def get_celestial_frame(body, r, x_trail, y_trail, z_trail):

    body_radii = {
        "earth": 6371,
        "venus": 6052,
        "sun": 696340,
        "jupiter": 69911,
        "europa": 1560
    }

    # Orbit trail, might take out of graph, timespans too short to matter much
    trail_frame = go.Scatter3d(
        x=x_trail,
        y=y_trail,
        z=z_trail,
        mode="lines",
        line=dict(width=2),
        showlegend=False
    )
    
    # Sphere for planet
    x, y, z = create_sphere(r, body_radii[body])

    body_frame = go.Surface(
        x=x,
        y=y,
        z=z,
        showscale=False,
        name=body,
        opacity=1
    )

    return [body_frame, trail_frame]

def get_spacecraft_frame(r, q):

    """ Placeholder geometry, will replace later """
    # Generate spacecraft geometry
    vertices_body, edges = create_cube(size=100)
    cube_i = [0,0,0,1,1,2,4,4,5,6,2,3] # Define triangular faces
    cube_j = [1,2,3,2,5,3,5,6,6,7,6,7]
    cube_k = [2,3,1,5,6,7,6,7,4,4,3,4]

    cube = get_spacecraft_inertial(
        vertices_body,
        r,
        q
    )

    frame = go.Mesh3d(
        x=cube[:,0],
        y=cube[:,1],
        z=cube[:,2],
        i=cube_i,
        j=cube_j,
        k=cube_k,
        color="black",
        opacity=0.9,
        showscale=False
    )

    return frame

def display_plot(fig, length):

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