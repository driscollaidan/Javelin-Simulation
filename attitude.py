import numpy as np

def quaternion_to_dcm(q):

    """
    Converts quaternion [q0, q1, q2, q3] to direction cosine matrix (3x3).
    - Returns inertial-to-body frame DCM.
    """

    q0, q1, q2, q3 = q

    C = np.array([
        [1 - 2*(q2**2 + q3**2),  2*(q1*q2 - q0*q3),      2*(q1*q3 + q0*q2)],
        [2*(q1*q2 + q0*q3),      1 - 2*(q1**2 + q3**2),  2*(q2*q3 - q0*q1)],
        [2*(q1*q3 - q0*q2),      2*(q2*q3 + q0*q1),      1 - 2*(q1**2 + q2**2)]
    ])

    return C

def quaternion_conjugate(q):
    return np.array([q[0], -q[1], -q[2], -q[3]])

def quaternion_multiply(q, p):
    """
    Hamilton product of two quaternions.
    
    Both must be scalar-first:
    - q = [q0, q1, q2, q3]
    - p = [p0, p1, p2, p3]
    """

    q0, q1, q2, q3 = q
    p0, p1, p2, p3 = p

    scalar = q0*p0 - q1*p1 - q2*p2 - q3*p3

    v1 = q0 * np.array([p1, p2, p3])
    v2 = p0 * np.array([q1, q2, q3])
    v3 = np.cross([q1, q2, q3], [p1, p2, p3])

    vector = v1 + v2 + v3

    return np.concatenate(([scalar], vector))