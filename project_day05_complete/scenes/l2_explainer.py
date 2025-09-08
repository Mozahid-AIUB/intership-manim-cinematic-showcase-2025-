from manim import *
import math


class L2Scene(Scene):
    def construct(self):
        title = Text("L2 Orbit Explainer", font_size=36).to_edge(UP)
        self.play(FadeIn(title))

        sun = Circle(radius=1.0, fill_opacity=1, color=YELLOW).shift(LEFT * 4)
        earth = Circle(radius=0.5, fill_opacity=1, color=BLUE).shift(ORIGIN)
        # L2 positioned roughly to the right of Earth in the diagram
        l2 = Dot(color=YELLOW).move_to(RIGHT * 2.2)

        earth_orbit = Circle(radius=1.6, stroke_color=WHITE, stroke_width=2).move_to(LEFT * 0.2)

        self.play(FadeIn(sun), FadeIn(earth), Create(earth_orbit), FadeIn(l2))
        self.wait(0.6)

        label = Text("JWST at L2", font_size=18).next_to(l2, UP)
        dist = Text("~1.5M km", font_size=16).next_to(l2, RIGHT, buff=0.1)
        self.play(Write(label), Write(dist))

        # halo orbit loop around L2 (parametric)
        halo = ParametricFunction(
            lambda t: l2.get_center() + np.array([0.28 * math.cos(t), 0.12 * math.sin(t), 0]),
            t_range=np.array([0, TAU]), stroke_color=YELLOW, stroke_width=2,
        )

        # small JWST icon moving on halo (triangle)
        jwst_icon = RegularPolygon(3).scale(0.12).set_fill(WHITE, opacity=1).move_to(halo.points[0])

        self.play(Create(halo), run_time=1.0)
        self.play(MoveAlongPath(jwst_icon, halo), run_time=3.0, rate_func=linear)

        caption = Text("L2: balance of gravity and orbital motion in rotating frame", font_size=16).to_edge(DOWN)
        self.play(Write(caption))
        self.wait(1.2)
