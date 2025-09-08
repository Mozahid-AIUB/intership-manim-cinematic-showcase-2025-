from manim import *


def build_sunshield_parts():
    """Return pallets, dta, layers, left_rod, right_rod positioned consistently."""
    pallets = Rectangle(width=6.4, height=0.6).set_fill(GREY_B, opacity=1).to_edge(DOWN, buff=1)

    dta = Rectangle(width=0.28, height=0.9).set_fill(GREY_D, opacity=1)
    dta.next_to(pallets, UP, buff=0.15)

    # Create 5 layers from inner (small) to outer (large)
    layers = VGroup()
    base_width = 5.2
    base_height = 1.6
    for i in range(5):
        # outer layers slightly wider
        w = base_width + (4 - i) * 0.22
        h = base_height + (4 - i) * 0.06
        rect = RoundedRectangle(width=w, height=h, corner_radius=0.06)
        shade = interpolate_color(GREY_B, GREY_D, i / 4)
        rect.set_fill(shade, opacity=0.85 - i * 0.06).set_stroke(width=1)
        rect.next_to(dta, UP, buff=0.08 + i * 0.02)
        layers.add(rect)

    left_rod = Line(pallets.get_left() + RIGHT * 0.3, dta.get_left() + LEFT * 0.05, stroke_width=6).set_color(GREY_D)
    right_rod = Line(pallets.get_right() + LEFT * 0.3, dta.get_right() + RIGHT * 0.05, stroke_width=6).set_color(GREY_D)

    return pallets, dta, layers, left_rod, right_rod


class SunshieldPallets(Scene):
    """Pallet release and DTA extension (prepares telescope for sunshield work)."""

    def construct(self):
        title = Text("Sunshield: pallets & DTA", font_size=30).to_edge(UP)
        self.play(FadeIn(title))

        pallets, dta, layers, left_rod, right_rod = build_sunshield_parts()
        pallets_label = Text("Pallets (stowed)", font_size=18).next_to(pallets, DOWN, buff=0.1)
        dta_label = Text("DTA", font_size=18).next_to(dta, RIGHT, buff=0.1)

        self.play(FadeIn(pallets), Write(pallets_label))
        self.wait(0.2)

        self.play(FadeIn(dta), Write(dta_label))
        # extend DTA upward
        self.play(dta.animate.shift(UP * 0.8), run_time=1.2)
        self.wait(0.6)


class SunshieldMidBoom(Scene):
    """Mid-boom extension: shows rods/booms that support sunshield deployment."""

    def construct(self):
        title = Text("Sunshield: mid-boom", font_size=30).to_edge(UP)
        self.play(FadeIn(title))

        pallets, dta, layers, left_rod, right_rod = build_sunshield_parts()
        # Show pallets/dta in stowed/extended positions
        self.add(pallets, dta)
        self.play(dta.animate.shift(UP * 0.8), run_time=1.0)

        # create booms
        self.play(Create(left_rod), Create(right_rod), run_time=1.0)
        self.wait(0.6)


class SunshieldTension(Scene):
    """Layer tensioning sequence with labels (Layer 1 → Layer 5)."""

    def construct(self):
        title = Text("Sunshield: layer tensioning", font_size=30).to_edge(UP)
        self.play(FadeIn(title))

        pallets, dta, layers, left_rod, right_rod = build_sunshield_parts()
        # place dta extended
        dta.shift(UP * 0.8)
        self.add(pallets, dta)

        # initial faded layers
        for layer in layers:
            layer.set_opacity(0.5)
            self.add(layer)

        labels = VGroup(*[
            Text(f"Layer {i+1}", font_size=16).set_color(WHITE).next_to(layers[i], DOWN, buff=0.05)
            for i in range(len(layers))
        ])

        for lb in labels:
            lb.set_opacity(0)

        self.play(LaggedStart(*[
            Succession(
                labels[i].animate.set_opacity(1),
                layers[i].animate.set_opacity(1).scale(1.01)
            ) for i in range(len(layers))
        ], lag_ratio=0.25), run_time=2.0)

        note = Text("Sun-facing side at bottom — telescope points away from Sun", font_size=14).to_edge(UR)
        self.play(FadeIn(note))
        self.wait(1)
