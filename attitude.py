import numpy as np

""" ======================================================================================================================================

   Intertial Frame is defined by J2000 standard, with origin at Solar System Barycenter.             
       - X-axis points towards vernal equinox (Earth-based reference).                               
       - Y-axis is orthogonal to X and Z, completing right-handed system.                            
       - Z-axis is perpendicular to elptic plane, positive towards north ecliptic pole.              
                                                                                                     
   Body Frame is defined by spacecraft components.                                                  
       - Z-axis points toward the High-Gain Antenna, pointing to Earth for communications.           
       - X-axis is the Solar Array normal, pointing towards the Sun for optimal power generation.     
       - Y-axis is orthogonal to X and Z, completing right-handed system.                            
                                                                                                     
====================================================================================================================================== """

""" ==================================================================================================================================== # 
#                                                                                                                                        #
#   Quaternion math functions:                                                                                                           #
#   - quaternion_conjugate()                                                                                                             # 
#   - quaternion_multiply()                                                                                                              #
#                                                                                                                                        #
# ==================================================================================================================================== """

# -------------------------------------------------------------------------------------------------------------------------------------- #
#   quaternion_conjugate()                                                                                                               #
# -------------------------------------------------------------------------------------------------------------------------------------- #

def quaternion_conjugate(q):
    """Returns the conjugate of a quaternion (scalar-first convention)."""

    return np.array([q[0], -q[1], -q[2], -q[3]])

# -------------------------------------------------------------------------------------------------------------------------------------- #
#   quaternion_multiply()                                                                                                                #
# -------------------------------------------------------------------------------------------------------------------------------------- #

def quaternion_multiply(q, p):
    """
    Hamilton product of two quaternions (scalar-first convention).
    - q = [q0, q1, q2, q3]
    - p = [p0, p1, p2, p3]
    """

    q0, q1, q2, q3 = q
    p0, p1, p2, p3 = p

    scalar = q0 * p0 - q1 * p1 - q2 * p2 - q3 * p3

    v1 = q0 * np.array([p1, p2, p3])
    v2 = p0 * np.array([q1, q2, q3])
    v3 = np.cross([q1, q2, q3], [p1, p2, p3])

    vector = v1 + v2 + v3

    return np.concatenate(([scalar], vector))

""" ==================================================================================================================================== # 
#                                                                                                                                        #
#   Frame math functions:                                                                                                                #
#   - get_spacecraft_inertial()                                                                                                          # 
#   - quaternion_to_dcm()                                                                                                                #
#   - dcm_to_quaternion()                                                                                                                #
#                                                                                                                                        #
# ==================================================================================================================================== """

# -------------------------------------------------------------------------------------------------------------------------------------- #
#   get_spacecraft_inertial()                                                                                                            #
# -------------------------------------------------------------------------------------------------------------------------------------- #

def get_spacecraft_inertial(vertices_body, r, q):

    """
    Transforms spacecraft geometry from body frame to inertial frame.
    - Returns vertices in inertial frame for visualization.
    """
    C = quaternion_to_dcm(q)
    vertices_inertial = (C @ vertices_body.T).T + r
    return vertices_inertial

# -------------------------------------------------------------------------------------------------------------------------------------- #
#                                                                                                                                        #
#   quaternion_to_dcm:                                                                                                                   #
#      - A: Unpacks quaternion components (q0, q1, q2, q3) from input array.                                                             #
#      - B: Computes and returns the 3x3 direction cosine matrix (DCM) using quaternions.                                                #
#                                                                                                                                        #
# -------------------------------------------------------------------------------------------------------------------------------------- #

def quaternion_to_dcm(q):

    """
    Converts quaternion [q0, q1, q2, q3] to direction cosine matrix (3x3).
    - Returns inertial-to-body frame DCM.
        - C[:,0] = inertial coordinates of body X
        - C[:,1] = inertial coordinates of body Y
        - C[:,2] = inertial coordinates of body Z
    """
    q0, q1, q2, q3 = q                                                              # A

    return np.array([                                                               # B
        [1 - 2*(q2**2 + q3**2),  2*(q1*q2 - q0*q3),      2*(q1*q3 + q0*q2)],
        [2*(q1*q2 + q0*q3),      1 - 2*(q1**2 + q3**2),  2*(q2*q3 - q0*q1)],
        [2*(q1*q3 - q0*q2),      2*(q2*q3 + q0*q1),      1 - 2*(q1**2 + q2**2)]
    ])

# -------------------------------------------------------------------------------------------------------------------------------------- #
#                                                                                                                                        #
#   dcm_to_quaternion:                                                                                                                   #
#      - A: Calculates trace of DCM, sum of diagonal elements. Used to determine formula for numerical stability.                        #
#      - B: If trace, C11 + C22 + C33 is positive, rotation angle is less than 180 degrees, and formula from Sheppard is applied.        #
#            - q0 = 1/2 (sqrt(tr(C) + 1))                                                                                                #
#            - q1 = (C32 - C23) / (4 * q0)                                                                                               #
#            - q2 = (C13 - C31) / (4 * q0)                                                                                               #
#            - q3 = (C21 - C12) / (4 * q0)                                                                                               #
#      - C: If large angle orietnation, use largest diagonal element of C to compute its corresponding quaternion first.                 #
#            . a) If C11 is the largest:                                                                                                 #
#                - q1 = 1/2 (sqrt(1 + C11 - C22 - C33))                                                                                  #
#                - q0 = (C32 - C23) / (4 * q1)                                                                                           #
#                - q2 = (C12 + C21) / (4 * q1)                                                                                           #
#                - q3 = (C13 + C31) / (4 * q1)                                                                                           #
#           . b) If C22 is the largest diagonal, calculate accordingly.                                                                  #
#           . c) If C33 is the largest diagonal, calculate accordingly.                                                                  #
#      - D: Outputs quaternion in scalar-first convention [q0, q1, q2, q3], representing rotation from intertial to body frame.          #   
#                                                                                                                                        #
# -------------------------------------------------------------------------------------------------------------------------------------- #

def dcm_to_quaternion(C):
    """
    Convert 3x3 rotation matrix (DCM) to quaternion [q0, q1, q2, q3] (scalar-first).
    """
    tr = np.trace(C)                                                # A

    if tr > 0:                                                      # B
        s = np.sqrt(tr + 1.0) * 2
        q0 = 0.25 * s
        q1 = (C[2,1] - C[1,2]) / s
        q2 = (C[0,2] - C[2,0]) / s
        q3 = (C[1,0] - C[0,1]) / s
        
    else:                                                           # C
        if (C[0,0] > C[1,1]) and (C[0,0] > C[2,2]):                 # C.a
            s = np.sqrt(1.0 + C[0,0] - C[1,1] - C[2,2]) * 2
            q0 = (C[2,1] - C[1,2]) / s
            q1 = 0.25 * s
            q2 = (C[0,1] + C[1,0]) / s
            q3 = (C[0,2] + C[2,0]) / s

        elif C[1,1] > C[2,2]:                                       # C.b
            s = np.sqrt(1.0 + C[1,1] - C[0,0] - C[2,2]) * 2
            q0 = (C[0,2] - C[2,0]) / s
            q1 = (C[0,1] + C[1,0]) / s
            q2 = 0.25 * s
            q3 = (C[1,2] + C[2,1]) / s

        else:                                                       # C.c
            s = np.sqrt(1.0 + C[2,2] - C[0,0] - C[1,1]) * 2
            q0 = (C[1,0] - C[0,1]) / s
            q1 = (C[0,2] + C[2,0]) / s
            q2 = (C[1,2] + C[2,1]) / s
            q3 = 0.25 * s

    return np.array([q0, q1, q2, q3])                               # D

""" ==================================================================================================================================== # 
#                                                                                                                                        #
#   Pointing Logic functions:                                                                                                            #
#   - body_frame_from_vector()                                                                                                           #
#   - get_pointing_quaternion()                                                                                                          #
#                                                                                                                                        #
# ==================================================================================================================================== """

# -------------------------------------------------------------------------------------------------------------------------------------- #
#                                                                                                                                        #
#   body_frame_from_vector:                                                                                                              #
#      - A: Obtain unit vector for forward direction, defining forward axis.                                                             #
#      - B: If no hint vector provided, picks the inertial X-axis as a reference.                                                        # 
#      - C: Calculates X-axis perpendicular to both Z and the hint, ensuring orthogonality.                                              #
#      - D: Correction to avoid singularity (cross product = zero) when chosen hint vector is clossely aligned with forward vector.      #
#      - E: Normalizes reference axis, making a unit vector for the DCM.                                                                 #
#      - F: Constructs third axis as cross product to ensure orthogonality.                                                              #
#      - G: Returns 3x3 DCM mapping inertial to body frame, each column being the inertial vector of the corresponding body axis.        #
#                                                                                                                                        #
# -------------------------------------------------------------------------------------------------------------------------------------- #

def body_frame_from_vector(forward, target_axis, up_hint=None):
    """
    Builds a direction cosine matrix (DCM) representing the spacecraft body frame in intertial coordinates.
    - Given a desired forward vector (e.g., Earth or Sun pointing), and an optional term to resolve roll ambiguity.
        - "Forward" direction vector.
        - "Up" hint vector.
    """
    forward_body = forward / np.linalg.norm(forward)                          # A
    
    if up_hint is None:                                                       # B  
        if abs(forward_body[0]) < 0.9:
            up_hint = np.array([1.0, 0.0, 0.0])
        else:
            up_hint = np.array([0.0, 1.0, 0.0])

    reference_body = np.cross(up_hint, forward_body)                          # C
    
    if np.linalg.norm(reference_body) < 1e-8:                                 # D
        up_hint = np.array([0.0, 1.0, 0.0])
        reference_body = np.cross(up_hint, forward_body)
    
    reference_body /= np.linalg.norm(reference_body)                          # E 

    cross_body = np.cross(forward_body, reference_body)                       # F
    cross_body /= np.linalg.norm(cross_body)

    axes = {
        "X": (forward_body, cross_body, reference_body),
        "Y": (reference_body, forward_body, cross_body),
        "Z": (reference_body, cross_body, forward_body)
    }

    return np.column_stack(axes[target_axis.upper()])                         # G

# -------------------------------------------------------------------------------------------------------------------------------------- #
#                                                                                                                                        #
#   get_pointing_quaternion:                                                                                                             #
#      - A: Computes forward vector (Nadir) from spacecraft to taget body, defining the body axis.                                       #
#      - B: If reference position is provided, use it as a hint to resolve roll ambiguity.                                               #
#      - C: Construct the body frame DCM from the forward and up vectors.                                                                #
#      - D: Convert the DCM to a quaternion orientation and return.                                                                      #
#                                                                                                                                        #
# -------------------------------------------------------------------------------------------------------------------------------------- #

def get_pointing_quaternion(r_sc, r_target, target_axis, r_ref=None):
    """
    Computes quaternion to point selected body axis of spacecraft (antenna) toward target body.
        - Need to define full attitude (roll).
        - Essentially, uses relative position vectors to define the desired body frame orientation.
    
    Inputs:
        - r_sc: spacecraft position vector in inertial frame.
        - r_target: target body center position vector in inertial frame.
        - target_axis: desired body axis to point at target (e.g., "X", "Y", "Z").
        - r_ref: reference body position vector in inertial frame, used as a hint to resolve roll ambiguity.
    """
    forward = r_target - r_sc                                                 # A

    if r_ref is not None:                                                     # B
        up_hint = r_ref - r_sc
    else:
        up_hint = None                                  

    C_body = body_frame_from_vector(forward, target_axis, up_hint)            # C

    return dcm_to_quaternion(C_body)                                          # D

""" ==================================================================================================================================== # 
#                                                                                                                                        #
#   Guidance Wrapper Functions:                                                                                                          #
#   - Thin wrappers to make control modes and orientation requests easier to implement/read.                                             #
#                                                                                                                                        #
# ==================================================================================================================================== """

# -------------------------------------------------------------------------------------------------------------------------------------- #
#   Wrapper Calls:                                                                                                                       #
# -------------------------------------------------------------------------------------------------------------------------------------- #

EARTH_POINTING = 0
SUN_POINTING = 1

def compute_guidance_quaternion(mode, r_sc, r_earth, r_sun):

    if mode == EARTH_POINTING:
        return earth_pointing(r_sc, r_earth, r_sun)

    elif mode == SUN_POINTING:
        return sun_pointing(r_sc, r_sun, r_earth)

# -------------------------------------------------------------------------------------------------------------------------------------- #
#   Pointing Modes:                                                                                                                      #
# -------------------------------------------------------------------------------------------------------------------------------------- #

def earth_pointing(r_sc, r_earth, r_sun):
    return get_pointing_quaternion(r_sc, r_earth, "Z", r_sun)

def sun_pointing(r_sc, r_sun, r_earth):
    return get_pointing_quaternion(r_sc, r_sun, "X", r_earth)