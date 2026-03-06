import matplotlib.pyplot as plt
import plotly.graph_objects as go

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

def plot_system(solar_system_data, spacecraft_position):
    
    bodies = list(solar_system_data.keys()) # earth, venus, jupiter, europa, sun
    length = len(solar_system_data[bodies[0]]["r"]) # should be equal to time_steps

    # Adjusted marker sizes for better visualization, loosely rooted in actual size
    body_sizes = {
        "earth": 8, # Earth radius: 3,959 miles
        "venus": 7, # Venus radius: 3,760 mils
        "sun": 40, # Sun radius: 432,690 miles
        "jupiter": 20, # Jupiter radius: 44,423 miles
        "europa": 4, # Europa radius: 969.84 milees
    }

    # Create figure
    fig = go.Figure()

    # Create traces for initial positions
    for body in bodies:
        r = solar_system_data[body]["r"][0]

        # Empty path trail for first frame
        fig.add_trace(
            go.Scatter3d(
                x=[r[0]],
                y=[r[1]],
                z=[r[2]],
                mode="lines",
                line=dict(width=2),
                showlegend=False
            )
        )

        # Body marker
        fig.add_trace(
            go.Scatter3d(
                x = [r[0]],
                y = [r[1]],
                z = [r[2]],
                mode="markers", # plotly mode
                marker=dict(size=body_sizes[body]), # consider changing size per body
                name=body # current body
            )
        )
    
    # Create animation frames
    frames = []
    for i in range(length):
        frame_data = []
        for body in bodies:
            r = solar_system_data[body]["r"][i]
            # Orbit trail
            frame_data.append(
                go.Scatter3d(
                    x=solar_system_data[body]["r"][:i+1, 0],
                    y=solar_system_data[body]["r"][:i+1, 1],
                    z=solar_system_data[body]["r"][:i+1, 2],
                    mode="lines",
                    line=dict(width=2),
                    showlegend=False
                )
            )
            # Current position for body
            frame_data.append(
                go.Scatter3d(
                    x = [r[0]],
                    y = [r[1]],
                    z = [r[2]],
                    mode="markers", # plotly mode
                    marker=dict(size=body_sizes[body]), # consider changing size per body
                    name=body # current body
                )
            )
        frames.append(go.Frame(data=frame_data, name=str(i))) # Makes a plotly frame from the data, adds to list
    fig.frames = frames # After collecting all frames, applies them to the figure

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