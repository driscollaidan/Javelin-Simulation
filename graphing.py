import plotly.graph_objects as go

def plot_orientation(t, w, q, start_indexes, end_indexes):

    """
    Outputs interactive Plotly graphs for:
    - Angular Velocities
    - Quaternions

    Only to be used in conjuction with long time periods, taking only useful sections.
    """

    for i in range(len(start_indexes)):

        start = start_indexes[i]
        end = end_indexes[i]

        angular_velocity_plot(t[start:end], w[:, start:end], i)
        quaternion_plot(t[start:end], q[:, start:end], i)

def quaternion_plot(t, q, k):

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=q[0], mode='lines', name='ε1'))
    fig.add_trace(go.Scatter(x=t, y=q[1], mode='lines', name='ε2'))
    fig.add_trace(go.Scatter(x=t, y=q[2], mode='lines', name='ε3'))
    fig.add_trace(go.Scatter(x=t, y=q[3], mode='lines', name='ε4'))
    fig.add_vline(x=t[k], line_dash="dash", line_color="black")

    fig.update_layout(
        title="Quaternion",
        xaxis_title="Time (s)",
        yaxis_title="Quaternion"
    )

    return fig

def angular_velocity_plot(t, w, k):

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=w[0], mode='lines', name='ωx'))
    fig.add_trace(go.Scatter(x=t, y=w[1], mode='lines', name='ωy'))
    fig.add_trace(go.Scatter(x=t, y=w[2], mode='lines', name='ωz'))
    fig.add_vline(x=t[k], line_dash="dash", line_color="black")

    fig.update_layout(
        title="Angular Velocity",
        xaxis_title="Time (s)",
        yaxis_title="Angular Velocity (rad/s)"
    )

    return fig

def find_intervals(q, tol=1e-8, quiet_steps=10):

    """
    Determines relevant frames to display for orientation to reduce compututational cost
    """

    end_indexes = []
    start_indexes = [0]

    lame_count = 0
    match_count = 0
    prev_q0, prev_q1, prev_q2, prev_q3 = [0, 0, 0, 0]

    for i in range(q.shape[1]):
        q0, q1, q2, q3 = q[:, i]

        if abs(q0 - prev_q0) < tol:
            match_count += 1
        if abs(q1 - prev_q1) < tol:
            match_count += 1
        if abs(q2 - prev_q2) < tol:
            match_count += 1
        if abs(q3 - prev_q3) < tol:
            match_count += 1

        if match_count > 2:
            lame_count += 1

        if lame_count >= quiet_steps:
            if len(start_indexes) > len(end_indexes):
                end_indexes.append(i)
            if match_count < 3:
                start_indexes.append(i)
                lame_count = 0
        elif lame_count > 0 and match_count < 3:
            lame_count = 0
                
        prev_q0, prev_q1, prev_q2, prev_q3 = [q0, q1, q2, q3]
        match_count = 0

    if len(start_indexes) > len(end_indexes):
        end_indexes.append(i)

    return start_indexes, end_indexes