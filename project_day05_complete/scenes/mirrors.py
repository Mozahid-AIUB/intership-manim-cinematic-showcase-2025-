from manim import *
import math


def build_primary_mirror():
    """Return primary VGroup, left_wing, right_wing positioned for scene use."""
    counts = [3, 4, 5, 4, 2]
    hexes = []
    hex_size = 0.38
    hex_w = hex_size * 2
    vert = hex_size * 1.8
    x_offset = - (max(counts) - 1) * hex_w / 2
    for row_idx, count in enumerate(counts):
        row_x = x_offset + (max(counts) - count) * hex_w / 2
        for j in range(count):
            h = RegularPolygon(6, start_angle=PI / 6)
            h.scale(hex_size)
            h.set_fill("#D4AF37", opacity=1).set_stroke(DARK_GREY, 1)
            h.move_to(RIGHT * (row_x + j * hex_w) + UP * (vert * (len(counts) / 2 - row_idx)))
            hexes.append(h)

    primary = VGroup(*hexes)
    primary.to_edge(DOWN, buff=1.2)

    seam_x = primary.get_center()[0]
    left_wing = VGroup(*[h for h in hexes if h.get_center()[0] < seam_x])
    right_wing = VGroup(*[h for h in hexes if h.get_center()[0] >= seam_x])
    return primary, left_wing, right_wing


def build_secondary():
    sec = Circle(radius=0.22).set_fill(GREY_A, opacity=1).set_stroke(BLACK, 1)
    tripod = VGroup(
        Line(sec.get_center(), sec.get_center() + DOWN * 0.9, stroke_width=3),
        Line(sec.get_center(), sec.get_center() + LEFT * 0.9 + DOWN * 0.6, stroke_width=3),
        Line(sec.get_center(), sec.get_center() + RIGHT * 0.9 + DOWN * 0.6, stroke_width=3),
    )
    secondary = VGroup(sec, tripod)
    return secondary


class SecondaryDeploy(Scene):
    """Secondary mirror boom deployment (tripod + small translation)."""

    def construct(self):
        title = Text("Secondary mirror: boom deploy", font_size=30).to_edge(UP)
        self.play(FadeIn(title))

        primary, left_wing, right_wing = build_primary_mirror()
        secondary = build_secondary()
        # place secondary in front of primary
        secondary.move_to(primary.get_top() + UP * 0.6)

        # Start with secondary stowed (lower)
        secondary.shift(DOWN * 0.6)
        self.play(FadeIn(primary))
        self.play(FadeIn(secondary))

        # extend boom upward slightly
        self.play(secondary.animate.shift(UP * 0.6), run_time=1.2)
        self.wait(0.6)


class PrimaryWingDeploy(Scene):
    """Primary mirror wing hinge/unfold animation (left + right wings)."""

    def construct(self):
        title = Text("Primary mirror: wing deploy", font_size=30).to_edge(UP)
        self.play(FadeIn(title))

        primary, left_wing, right_wing = build_primary_mirror()
        self.play(FadeIn(primary))

        # hinge left and right wings outward
        hinge_left = left_wing.get_center() + RIGHT * 0.45
        hinge_right = right_wing.get_center() + LEFT * 0.45

        self.play(Rotate(left_wing, angle=-70 * DEGREES, about_point=hinge_left), run_time=1.6)
        self.play(Rotate(right_wing, angle=70 * DEGREES, about_point=hinge_right), run_time=1.6)
        self.wait(0.6)
