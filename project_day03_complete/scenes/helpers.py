import numpy as np

# Linear interpolation
def lerp(a, b, t):
    return a + t * (b - a)

# Smoothstep easing
def smoothstep(t):
    return t*t*(3 - 2*t)

# Hohmann-like arc from Earth to Mars (simplified)
def hohmann_like_arc(earth_pos, mars_pos, t):
    t_smooth = smoothstep(t)
    return lerp(np.array(earth_pos), np.array(mars_pos), t_smooth)

# Placeholder updaters for HUD
def orbital_velocity_from_arc(t):
    return 7.8 + t  # km/s placeholder

def radius_from_focus(t):
    return 300 + 10*t  # km placeholder

def map_t_to_transit_time(t):
    return int(180*t)  # days placeholder

def compute_from_altitude_and_time(t):
    return t*100  # m/s placeholder

def integrate_vertical_motion(t):
    return t*2  # km placeholder

def scene_elapsed_time(t):
    return t

def linear_percent_from_time(t, duration=6):
    return min(max((t/duration)*100, 0), 100)

def derivative_of_altitude(t):
    return -9.8*t  # m/s placeholder

def distance_to_terrain():
    return 0  # placeholder

def phase_from_time(t):
    if t < 5: return "Entry"
    if t < 10: return "Retro Burn"
    return "Touchdown"
