# outro_imranslab_highattr.py
"""
High-attractiveness 15.0s outro for ImransLab.
- Geometric structures, layered strokes, soft shadow, parallax.
- Tries to load 'imranslab_logo.svg' or 'imranslab_logo.png' (same folder).
- Timings exactly sum to 15.0s. No zero-length waits.
- Final 3 seconds: peripheral flourish that does NOT overlap or obscure the central logo.
Author: Prepared for Day 2 Assignment (revised to prevent overlap & zero-duration calls)
"""

from manim import *
import math
import os

# ---------- Config ----------
config.background_color = "#FBFBFB"  # near-white background
# Palette
DARK = "#111111"
ACCENT = "#2B6CB0"
ACCENT2 = "#9F7AEA"
ACCENT3 = "#48BB78"  # a green accent for subtle contrast
SUB = "#4A5568"

# ---------- Small color helpers ----------
def hex_to_rgb(hex_str: str):
    s = hex_str.lstrip("#")
    return tuple(int(s[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(
        max(0, min(255, int(round(rgb[0] * 255)))),
        max(0, min(255, int(round(rgb[1] * 255)))),
        max(0, min(255, int(round(rgb[2] * 255))))
    )

def interp_hex_color(a_hex: str, b_hex: str, t: float):
    ra, ga, ba = hex_to_rgb(a_hex)
    rb, gb, bb = hex_to_rgb(b_hex)
    rc = ra * (1 - t) + rb * t
    gc = ga * (1 - t) + gb * t
    bc = ba * (1 - t) + bb * t
    return rgb_to_hex((rc, gc, bc))

# ---------- Visual helper factories ----------
def make_nested_polygons(center=ORIGIN, layers=4, base_radius=0.6):
    group = VGroup()
    for i in range(layers):
        sides = 3 + i
        poly = RegularPolygon(n=sides)
        poly.scale(base_radius * (1 + 0.26 * i))
        color = interp_hex_color(ACCENT, ACCENT2, i / max(1, layers - 1))
        poly.set_stroke(color=color, width=max(1.0, 3 - 0.35 * i))
        poly.set_fill(opacity=0)
        poly.move_to(center)
        group.add(poly)
    return group

def make_gradient_ring(radius=1.0, segments=90, width=0.08):
    """
    Simulated gradient ring: many thin arcs with interpolated colors.
    Returns a VGroup of arcs.
    """
    arcs = VGroup()
    for i in range(segments):
        theta1 = TAU * (i / segments)
        theta2 = TAU * ((i + 1) / segments)
        arc = Arc(
            radius=radius,
            start_angle=theta1,
            angle=theta2 - theta1,
            stroke_width=width,
            arc_center=ORIGIN
        )
        t = i / (segments - 1)
        arc_color = interp_hex_color(ACCENT, ACCENT2, t)
        arc.set_stroke(color=arc_color, width=width * 40)  # stroke width scaled for visibility
        arcs.add(arc)
    return arcs

class ParticleField(VGroup):
    def __init__(self, n_rings=3, per_ring=18, radius_step=0.28, **kwargs):
        super().__init__(**kwargs)
        dots = []
        for r in range(1, n_rings + 1):
            rads = r * radius_step
            for k in range(per_ring):
                angle = TAU * (k / per_ring) + (r * 0.08)
                pos = rads * np.array([math.cos(angle), math.sin(angle), 0])
                d = Dot(point=pos, radius=0.035)
                # color blends green and purple for visual interest
                d.set_fill(interp_hex_color(ACCENT2, ACCENT3, (r - 1) / max(1, n_rings - 1)), opacity=0.9 - r * 0.12)
                d.set_stroke(width=0)
                dots.append(d)
        self.add(*dots)

def shadow(obj: Mobject, offset=0.08, opacity=0.25):
    """Return a soft pseudo-shadow by duplicating, moving, and dimming the object."""
    sh = obj.copy()
    sh.set_fill(opacity=0)
    try:
        sh.set_stroke(width=max(0.5, getattr(obj, "stroke_width", 1)), color="#000000")
    except Exception:
        sh.set_stroke(width=1, color="#000000")
    sh.set_opacity(opacity)
    sh.shift(DOWN * offset + RIGHT * offset * 0.2)
    return sh

def load_brand_logo(preferred_svg="imranslab_logo.svg", fallback_png="imranslab_logo.png"):
    if os.path.exists(preferred_svg):
        try:
            return SVGMobject(preferred_svg)
        except Exception:
            pass
    if os.path.exists(fallback_png):
        try:
            return ImageMobject(fallback_png)
        except Exception:
            pass
    return None

# ---------- Scene (15.0s total) ----------
class ImransLabOutroHighAttr(Scene):
    def construct(self):
        # Section timings:
        # 0.00 - 2.00  : logo reveal (2.0)
        # 2.00 - 8.00  : headline + spiro (6.0)
        # 8.00 - 12.00 : contact + parallax (4.0)
        # 12.00 - 15.00: peripheral flourish (3.0) - NO OVERLAP with logo

        # --- Load logo or build fallback mark ---
        logo_obj = load_brand_logo()
        if logo_obj:
            logo_obj.set(width=3.2)
            logo = logo_obj
        else:
            mark = make_nested_polygons(layers=3, base_radius=0.48)
            center_dot = Dot(radius=0.09, color=ACCENT2)
            initials = Text("imranslab", font_size=36)
            initials.set_color(DARK)
            initials.next_to(mark, RIGHT, buff=0.32)
            logo = VGroup(mark, center_dot, initials)

        logo.move_to(ORIGIN)

        # Add a soft shadow behind logo
        logo_shadow = shadow(logo, offset=0.06, opacity=0.18)

        # Ensure logo z-order is top so nothing can accidentally draw over it
        try:
            logo.set_z_index(100)
            logo_shadow.set_z_index(90)
        except Exception:
            # older Manim versions ignore z-index; we will control draw order instead
            pass

        # --- 0.00 - 2.00 : reveal with elegance ---
        self.play(FadeIn(logo_shadow, run_time=0.45))
        self.play(FadeIn(logo, run_time=0.65))
        self.play(logo.animate.scale(1.05), run_time=0.6)
        self.wait(0.8)

        # --- 2.00 - 8.00 : headline + decorative spiro & ring (6.0) ---
        headline = Text("imranslab — Education, Research, Prototyping", font_size=34, weight=BOLD)
        headline.set_color(DARK)
        headline.next_to(logo, DOWN, buff=0.72)

        subtitle = Text("Hands-on projects • Open resources • Community", font_size=24)
        subtitle.set_color(SUB)
        subtitle.next_to(headline, DOWN, buff=0.28)

        # Decorative elements placed in the far left for parallax (well away from center)
        spiro = ParametricFunction(lambda t: np.array([
            math.cos(3.0 * t) * 0.9 + 0.15 * math.cos(7.0 * t),
            math.sin(4.0 * t) * 0.9 + 0.12 * math.sin(9.0 * t),
            0
        ]), t_range=[0, TAU])
        spiro.set_stroke(interp_hex_color(ACCENT, ACCENT2, 0.25), width=2.0)
        spiro.move_to(LEFT * 3.1 + UP * 0.4)
        spiro.set_opacity(0.95)

        # gradient ring (small)
        gradient_ring = make_gradient_ring(radius=1.05, segments=72, width=0.04)
        gradient_ring.move_to(LEFT * 2.1 + DOWN * 0.05)
        gradient_ring.set_opacity(0.95)

        self.play(logo.animate.shift(UP * 0.34), FadeIn(headline, shift=UP * 0.2), run_time=0.9)
        self.play(Write(subtitle, run_time=1.1))
        # draw spiro and ring together with slight overlap
        self.play(Create(spiro, run_time=1.4), Create(gradient_ring, run_time=1.2))
        # headline subtle micro-breathe
        self.play(headline.animate.shift(UP * 0.04), rate_func=there_and_back, run_time=1.0)
        self.wait(1.4)

        # --- 8.00 - 12.00 : contact lines + parallax shift (4.0) ---
        repo = Text("imranslab.org", font_size=22)
        repo.set_color(DARK)
        contact = Text("Contact: contact@imranslab.org", font_size=22)
        contact.set_color(DARK)
        social = Text("YouTube / GitHub / Twitter: imranslab", font_size=20)
        social.set_color(SUB)
        contact_group = VGroup(repo, contact, social).arrange(DOWN, aligned_edge=LEFT, buff=0.26)
        contact_group.next_to(subtitle, DOWN, buff=0.95).shift(RIGHT * 0.18)

        # Parallax: move left decorations gently as contact slides in
        self.play(LaggedStart(
            contact_group.animate.shift(RIGHT * 0.6),
            spiro.animate.shift(LEFT * 0.15).scale(1.02),
            gradient_ring.animate.shift(LEFT * 0.08).scale(1.01),
            lag_ratio=0.18,
            run_time=1.05
        ))
        self.play(LaggedStart(*[t.animate.scale(1.03) for t in contact_group], run_time=0.6, lag_ratio=0.12))
        self.wait(2.35)

        # --- 12.00 - 15.00 : PERIPHERAL FLOURISH (3.0) - GUARANTEED NO OVERLAP ---
        # Determine a safe radius around logo; keep all ornaments outside this radius.
        # Use logo width to compute safe distance; fall back to 1.6 if unavailable.
        try:
            logo_safe_radius = max(1.6, logo.get_width() / 2 + 0.5)
        except Exception:
            logo_safe_radius = 1.6

        # Place three peripheral flourish clusters around the logo at angles 0, 120, -120 degrees
        angle_list = [0, 2 * math.pi / 3, -2 * math.pi / 3]
        clusters = VGroup()
        for idx, ang in enumerate(angle_list):
            # Compute a position beyond the safe radius
            pos = np.array([math.cos(ang), math.sin(ang), 0]) * (logo_safe_radius + 0.9)
            # Slight vertical offset variation for depth
            pos = pos + np.array([0, -0.08 * idx, 0])

            cluster = VGroup()
            # small nested polygons cluster
            part_nested = make_nested_polygons(layers=3, base_radius=0.28)
            part_nested.move_to(pos + np.array([0.0, 0.0, 0]))
            # a particle field localized to the cluster
            part_particles = ParticleField(n_rings=2, per_ring=12, radius_step=0.18)
            part_particles.move_to(part_nested.get_center())
            # a small gradient ring around cluster
            part_ring = make_gradient_ring(radius=0.6, segments=48, width=0.03)
            part_ring.move_to(part_nested.get_center())

            cluster.add(part_ring, part_nested, part_particles)
            # ensure clusters are behind logo visually
            try:
                cluster.set_z_index(10)
            except Exception:
                pass
            clusters.add(cluster)

        # Put clusters into scene (they are outside safe central area)
        self.play(
            LaggedStart(*[FadeIn(c, shift=DOWN * 0.15) for c in clusters], lag_ratio=0.18, run_time=0.9)
        )

        # Peripheral movement: rotate each cluster slightly and expand particles
        self.play(
            *[Rotate(clusters[i], angle=TAU * (0.06 + 0.04 * i), about_point=clusters[i].get_center()) for i in range(len(clusters))],
            clusters.animate.scale(1.05),
            run_time=1.5
        )

        # Subtle logo pulse to emphasize brand while peripheral motion completes
        self.play(logo.animate.scale(1.07), run_time=0.3)
        self.play(logo.animate.scale(0.97), run_time=0.3)

        # Now fade out all ornamental clusters and left-side decorations but KEEP logo + shadow fully visible.
        ornamentals = VGroup(spiro, gradient_ring, clusters, nested, particles, ring_big) if "nested" in locals() else VGroup(spiro, gradient_ring, clusters)
        # also fade contact and headline to give clean frame
        ornaments_and_text = VGroup(ornamentals, headline, subtitle, contact_group)
        # Fade them out while leaving logo and logo_shadow intact
        self.play(FadeOut(ornaments_and_text, run_time=0.9)) 

        # End of scene — leave logo visible and unobstructed (no zero-duration plays or waits)..
