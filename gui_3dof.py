import numpy as np
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, callback, callback_context
import json
from scipy.interpolate import CubicSpline

from orbitals import load_planetary_data, load_spacecraft_3dof
from visualize import build_3dof_frame

def run_gui_3dof():
    
    bodies = ["sun", "earth", "venus", "jupiter", "europa"]
    t_vec, solar_system_data = load_planetary_data(bodies)

    # Assemble splines for interpolating planetary body positions.
    splines = {}
    for body in bodies:
        splines[body] = CubicSpline(t_vec, solar_system_data[body]["r"])

    with open("trajectory/rank_004.json", "r") as file:
        data = json.load(file)

    t_sc, r_sc, _ = load_spacecraft_3dof(data)
    splines["spacecraft"] = CubicSpline(t_sc, r_sc)

    t_display = np.linspace(t_vec[0], t_vec[-1], 600)

    app = Dash(__name__)

    app.layout = html.Div([
        html.H3("3DoF Orbital View"),

        dcc.Graph(
            id="display-3dof",
            style={"height": "80vh"}
        ),

        html.Button("Play / Pause", id="play"),
        dcc.Slider(
            id="slider",
            min=0,
            max=len(t_display) - 1,
            step=1,
            value=0
        ),

        dcc.Interval(id="anim", interval=50, disabled=True),
        dcc.Store(id="index", data=0)
    ])

    @callback(
        Output("display-3dof", "figure"),
        Input("index", "data"),
    )
    def update(k):
        if k is None:
            k = 0
        else:
            k = k

        k = k % len(t_display)
        t = t_display[k]

        r_now = splines["spacecraft"](t)
        t_hist = np.linspace(t_sc[0], t, 200)
        traj = splines["spacecraft"](t_hist)

        r_planets = {}
        for body in bodies:
            r_planets[body] = splines[body](t)

        traces = build_3dof_frame(r_planets, r_now, traj)

        fig = go.Figure(data=traces)

        fig.update_layout(
            uirevision="constant",
            scene=dict(
                xaxis=dict(
                    range=[-8.5e8, 8.5e8],
                    backgroundcolor="rgb(20, 20, 20)",
                    gridcolor="rgb(60, 60, 60)",
                    zerolinecolor="rgb(80, 80, 80)",
                ),
                yaxis=dict(
                    range=[-8.5e8, 8.5e8],
                    backgroundcolor="rgb(20, 20, 20)",
                    gridcolor="rgb(60, 60, 60)",
                    zerolinecolor="rgb(80, 80, 80)",
                ),
                zaxis=dict(
                    range=[-8.5e8, 8.5e8],
                    backgroundcolor="rgb(20, 20, 20)",
                    gridcolor="rgb(60, 60, 60)",
                    zerolinecolor="rgb(80, 80, 80)",
                ),
                aspectmode="cube",
                bgcolor="rgb(10, 10, 10)"   
            ),
            paper_bgcolor="rgb(10, 10, 10)",  
            plot_bgcolor="rgb(10, 10, 10)",   
            margin=dict(l=0, r=0, b=0, t=0)
        )

        return fig

    @callback(
        Output("anim", "disabled"),
        Input("play", "n_clicks"),
        State("anim", "disabled"),
        prevent_initial_call=True
    )
    def toggle(_, disabled):
        return not disabled

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