import numpy as np
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, callback, callback_context
import json
from scipy.interpolate import CubicSpline

from dynamics import simulate_6DoF
from visualize import build_6dof_frame, get_spacecraft_6dof_frame, get_pointing_traces, get_full_system_bounds_trace
from geometry import create_spacecraft
from helpers import seed, random_float, process_time
from graphing import quaternion_plot, angular_velocity_plot
from orbitals import load_planetary_data, load_spacecraft_3dof

def init_6dof():
    """
    Establishes all initial data needs and conditions for 6DoF GUI.
    """
    bodies = ["sun", "venus", "earth", "moon", "jupiter", "europa"]
    t_vec, solar_system_data = load_planetary_data(bodies)

    # Assemble splines for interpolating planetary body positions.
    splines = {}
    for body in bodies:
        splines[body] = CubicSpline(t_vec, solar_system_data[body]["r"])

    # Get cached 3dof spacecraft data. Results in 512 points
    with open("trajectory/rank_004.json") as file:
        data = json.load(file)

    t_sc, r_sc, v_sc = load_spacecraft_3dof(data)
    splines["spacecraft"] = CubicSpline(t_sc, r_sc)
    splines["velocity"] = CubicSpline(t_sc, v_sc)

    # Generates placeholder spacecraft geometry for 6DoF visualization.
    vertices_body, faces = create_spacecraft() 
    I = np.diag([1, 2, 0.5]) 

    # Initialize randomization
    seed()

    mission_times = ["2034-Jul-05 17:48:02", "2034-Oct-07 17:57:01", "2034-Nov-21 15:25:06", "2035-Dec-24 04:00:11",
                     "2036-Aug-24 10:17:40", "2037-Feb-24 22:01:54", "2038-Nov-09 02:57:53", "2039-Feb-09 19:54:58",
                     "2041-Apr-20 20:43:16"]

    for i in range(len(mission_times)):
        mission_times[i] = process_time(mission_times[i])

    # Mission options
    mission_options = [
        {"label": "Launch | 2034-Jul-05", "value": mission_times[0]},
        {"label": "DSM 1 | 2034-Oct-07", "value": mission_times[1]},
        {"label": "Venus Flyby | 2034-Nov-21", "value": mission_times[2]},
        {"label": "DSM 2 | 2035-Dec-24", "value": mission_times[3]},
        {"label": "Earth Flyby 1 | 2036-Aug-24", "value": mission_times[4]},
        {"label": "DSM 3 | 2037-Feb-24", "value": mission_times[5]},
        {"label": "Earth Flyby 2 | 2038-Nov-09", "value": mission_times[6]},
        {"label": "DSM 4 | 2039-Feb-09", "value": mission_times[7]},
        {"label": "Arrival (Jupiter) | 2041-Apr-20", "value": mission_times[8]},
    ]

    mission_display = {
        mission_options[0]["value"]: ["earth"], 
        mission_options[1]["value"]: ["earth"],
        mission_options[2]["value"]: ["venus"],
        mission_options[4]["value"]: ["earth"],
        mission_options[8]["value"]: ["jupiter", "europa"],
    }

    return bodies, splines, vertices_body, faces, I, t_sc, mission_options, mission_display

def run_gui_6dof():

    bodies, splines, vertices_body, faces, I, t_sc, mission_options, mission_display = init_6dof()

    app = Dash(__name__)

    app.layout = html.Div([

        html.Div([

            # LEFT COLUMN (controls + main 3D plot)
            html.Div([

            html.Label("Select Mission Phase"),
            dcc.Dropdown(
                id="mission-select",
                options=mission_options,
                value=mission_options[0]["value"],
                placeholder="Choose event"
            ),

                dcc.Graph(
                    id="attitude-anim",
                    style={"height": "100%", "width": "100%"},
                    config={"responsive": True}
                ),

            ], style={
                "width": "40%",
                "height": "80vh",
                "display": "flex",
                "flexDirection": "column",
                "gap": "10px"
            }),

            html.Div([

                dcc.Graph(
                    id="display",
                    style={"height": "50%", "width": "100%"}
                ),

                html.Div([
                    dcc.Graph(
                        id="quat-plot",
                        style={"width": "50%", "height": "100%"}
                    ),
                    dcc.Graph(
                        id="omega-plot",
                        style={"width": "50%", "height": "100%"}
                    ),
                ], style={
                    "display": "flex",
                    "height": "50%",
                    "width": "100%"
                }),

            ], style={
                "width": "60%",
                "height": "80vh",
                "display": "flex",
                "flexDirection": "column"
            })

        ], style={
            "display": "flex",
            "height": "80vh"
        }),

        html.Button("Play / Pause", id="play"),

        dcc.Slider(
            id="slider",
            min=0,
            max=199,
            step=1,
            value=0
        ),

        dcc.Interval(id="anim", interval=600, disabled=True),
        dcc.Store(id="index", data=0),
        dcc.Store(id="cache"),
    ])

    @callback(
        Output("display", "figure"),
        Output("quat-plot", "figure"),
        Output("omega-plot", "figure"),
        Output("attitude-anim", "figure"),
        Output("cache", "data"),
        Input("index", "data"),
        Input("mission-select", "value"),
        State("cache", "data"),
    )
    def update(k, t0, cache):
        
        if k is None:
            k = 0
        else:
            k = k

        if t0 is None:
            t0 = t_sc[0]

        r0 = splines["spacecraft"](t0)
        v0 = splines["velocity"](t0)

        w0 = np.array([random_float(0, 1), random_float(0, 1), random_float(0, 1)])
        q0 = np.array([random_float(0, 1), random_float(0, 1), random_float(0, 1), random_float(0, 1)])

        # Load cache if it exists.
        if cache is not None and np.isclose(cache.get("t0"), t0):
            r = np.array(cache["r"])
            v = np.array(cache["v"])
            w = np.array(cache["w"])
            q = np.array(cache["q"])
            t_sim = np.array(cache["t_sim"])

        # Run simulation if needed.
        else:
            r, v, w, q = simulate_6DoF(I, r0, v0, w0, q0, t0, bodies)
            t_sim = np.linspace(0, 200, r.shape[1])

        # Cache simulation.
        cache = {
            "t0": t0,
            "t_sim": t_sim.tolist(),
            "r": r.tolist(),
            "v": v.tolist(),
            "w": w.tolist(),
            "q": q.tolist()
        }

        k = k % len(t_sim)

        r_sc = r[:, k]
        q_sc = q[:, k]
    
        r_planets = {}
        for body in bodies:
            r_planets[body] = splines[body](t0 + t_sim[k])

        # Establishing distance-based telemetry data needs.
        selected_bodies = mission_display.get(t0)
        if selected_bodies is not None:
            selected_bodies = mission_display.get(t0, 0)

            distances = {}
            for body in selected_bodies:
                distances[body] = np.linalg.norm(r_planets[body] - r_sc)

        # Creating telemetry for 6DoF solar system display.
        telemetry_6dof = []
        telemetry_6dof.append(f"Spacecraft Position (wrt Sun): [{r_sc[0]:,.2f}, {r_sc[1]:,.2f}, {r_sc[2]:,.2f}] km       ")
        telemetry_6dof.append(f"Spacecraft Velocity (wrt Sun): [{v[:,k][0]:.2f}, {v[:,k][1]:.2f}, {v[:,k][2]:.2f}] km/s")

        if selected_bodies:
            telemetry_6dof.append("")
            for body in selected_bodies:
                telemetry_6dof.append(f"Distance to {body.capitalize()}: {distances[body]:,.2f} km")
        telemetry_6dof = "<br>".join(telemetry_6dof)

        annotations_6dof = [dict(
            text=telemetry_6dof,
            x=0.6,
            y=1,
            xref="paper",
            yref="paper",
            xanchor="right",
            yanchor="top",
            align="left",
            showarrow=False,
            font=dict(size=12, color="white"),
            bgcolor="rgba(0,0,0,0.6)"
        )]

        traces = build_6dof_frame(r_sc, q_sc, vertices_body, faces, r_planets, bodies)
        traces.append(get_full_system_bounds_trace())

        fig = go.Figure(data=traces)

        fig.update_layout(
            annotations=annotations_6dof,
            autosize=True,
            uirevision="constant",
            scene=dict( 
                xaxis=dict(
                    showticklabels=False, title="",
                    backgroundcolor="rgb(20, 20, 20)",
                    gridcolor="rgb(60, 60, 60)",
                    zerolinecolor="rgb(80, 80, 80)",
                ),
                yaxis=dict(
                    showticklabels=False, title="",
                    backgroundcolor="rgb(20, 20, 20)",
                    gridcolor="rgb(60, 60, 60)",
                    zerolinecolor="rgb(80, 80, 80)",
                ),
                zaxis=dict(
                    showticklabels=False, title="",
                    backgroundcolor="rgb(20, 20, 20)",
                    gridcolor="rgb(60, 60, 60)",
                    zerolinecolor="rgb(80, 80, 80)",
                ),
                aspectmode="data",
            ),
            plot_bgcolor="rgb(10, 10, 10)",
            margin=dict(l=0, r=0, b=0, t=0),
            legend=dict(
                y=0.85,
                bgcolor="rgba(0,0,0,0.8)",
                font=dict(color="white")
            )
        )

        quat_fig = quaternion_plot(t_sim, q, k)
        quat_fig.update_layout(autosize=True, uirevision="constant", height=400)

        omega_fig = angular_velocity_plot(t_sim, w, k)
        omega_fig.update_layout(autosize=True, uirevision="constant", height=400)

        # Move spacecraft to origin for spacecraft visualization
        origin = r_sc.copy()
        r_sc_centered = r_sc - origin
        r_planets_centered = {
            body: r_planets[body] - origin
            for body in r_planets
        }
        anim_trace = get_spacecraft_6dof_frame(r_sc_centered, q_sc, vertices_body, faces)
        pointing_traces = get_pointing_traces(r_sc_centered, r_planets_centered, bodies)

        anim_fig = go.Figure(data=(anim_trace + pointing_traces))
        anim_fig.update_layout(
            autosize=True, 
            uirevision="constant", 
            height=450,
            scene=dict(
                xaxis=dict(
                    showticklabels=False, title="",
                    backgroundcolor="rgb(20, 20, 20)",
                    gridcolor="rgb(60, 60, 60)",
                    zerolinecolor="rgb(80, 80, 80)",
                ),
                yaxis=dict(
                    showticklabels=False, title="",
                    backgroundcolor="rgb(20, 20, 20)",
                    gridcolor="rgb(60, 60, 60)",
                    zerolinecolor="rgb(80, 80, 80)",
                ),
                zaxis=dict(
                    showticklabels=False, title="",
                    backgroundcolor="rgb(20, 20, 20)",
                    gridcolor="rgb(60, 60, 60)",
                    zerolinecolor="rgb(80, 80, 80)",
                ),
                aspectmode="data",
            ),
            plot_bgcolor="rgb(10, 10, 10)",
            margin=dict(l=0, r=0, b=0, t=0),
            legend=dict(
                y=0.85,
                bgcolor="rgba(0,0,0,0.8)",
                font=dict(color="white")
            )
        )

        return fig, quat_fig, omega_fig, anim_fig, cache

    @callback(
        Output("anim", "disabled"),
        Input("play", "n_clicks"),
        State("anim", "disabled"),
        prevent_initial_call=True
    )
    def toggle(_, d): return not d

    @callback(
        Output("index", "data"),
        Input("anim", "n_intervals"),
        Input("slider", "drag_value"),
        State("index", "data"),
        State("anim", "disabled"),
    )
    def step(n, slider_val, k, paused):
        if k is None:
            k = 0

        ctx = callback_context.triggered_id

        if ctx == "slider" and slider_val is not None:
            return slider_val
        if not paused:
            return k + 1
        return k
    
    @callback(
        Output("slider", "value"),
        Input("index", "data"),
    )
    def sync_slider(k):
        if k is None:
            return 0
        return k

    app.run(debug=True)