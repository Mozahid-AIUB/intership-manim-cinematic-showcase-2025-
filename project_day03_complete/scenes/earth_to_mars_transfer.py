# src/earth_to_mars_transfer.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # allow import from parent

from manim import *
from manim.mobject.opengl.opengl_vectorized_mobject import OpenGLVMobject
from helpers import hohmann_like_arc  # ensure this function exists

class EarthToMarsTransfer(ThreeDScene):
    def construct(self):
        # --- Create Earth and Mars (low resolution spheres) ---
        earth = Sphere(radius=4.5, resolution=(16,16), color=BLUE).move_to([-5,0,0])
        mars = Sphere(radius=3, resolution=(12,12), color=RED).move_to([10,0,0])
        self.add(earth, mars)

        # --- Create Transfer Arc (OpenGL-compatible) ---
        arc_points = [hohmann_like_arc([-2,0,0], [8,0,0], t/50) for t in range(31)]
        arc = OpenGLVMobject()
        arc.set_points_as_corners(arc_points)
        arc.set_stroke(BLUE, width=2)
        self.add(arc)

        # --- Starship follows arc ---
        # Body of the starship
        body = Cylinder(radius=0.5, height=3, resolution=(8, 8), color=WHITE)
        body.rotate(PI/2, axis=UP)

        # Nose cone (pencil tip)
        nose = Cone(radius=1.0, height=2.5, resolution=12, color=GRAY)
        nose.rotate(PI/2, axis=UP)
        nose.next_to(body, RIGHT, buff=0)  # attach to the front of the cylinder

        flame = Cone(radius=0.3, height=0.6, resolution=6, color=ORANGE)
        flame.rotate(PI/2, axis=UP)
        flame.next_to(body, LEFT, buff=0) 
                
        # Combine into a starship
        starship = VGroup(body, nose, flame)
        starship.move_to(arc_points[0])

        self.add(starship)

        # --- Camera settings ---
        self.set_camera_orientation(phi=65 * DEGREES, theta=35 * DEGREES)
        self.begin_ambient_camera_rotation(rate=0.01)  # slowly rotate for 3D effect

        # --- HUD placeholders ---
        vel_text = DecimalNumber(0, num_decimal_places=2).to_corner(UL)
        alt_text = DecimalNumber(0, num_decimal_places=2).next_to(vel_text, DOWN)
        tof_text = DecimalNumber(0, num_decimal_places=2).next_to(alt_text, DOWN)
        self.add(vel_text, alt_text, tof_text)

        # --- HUD Updaters ---
        def hud_updater(mob):
            # t goes from 0 to 1 based on animation progress
            # self.time gives scene time in seconds
            t = self.time
            mob[0].set_value(t*0.1)  # velocity
            mob[1].set_value(t*0.2)  # altitude
            mob[2].set_value(t*0.05) # time of flight

        hud_group = VGroup(vel_text, alt_text, tof_text)
        hud_group.add_updater(hud_updater)

        # --- Animate starship along the arc ---
        self.play(
            MoveAlongPath(starship, arc),
            run_time=12,
            rate_func=smooth
        )

        # Remove updaters after animation
        hud_group.clear_updaters()
