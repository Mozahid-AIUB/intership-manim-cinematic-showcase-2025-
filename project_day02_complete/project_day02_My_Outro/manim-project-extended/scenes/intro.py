from manim import *
import random

PURE_PINK = "#ff69b4"
LOGO_GLOW_COLOR = "#ff1493"
TAGLINE_COLOR = PURE_PINK
TITLE_COLOR = DARK_GRAY
LIGHT_STREAK_COLOR = "#ffb6c1"

class Intro(Scene):
    def construct(self):
        # ----------------------
        # 1. Cool Whitish Gradient Background
        # ----------------------
        bg_rect = Rectangle(width=config.frame_width, height=config.frame_height)
        bg_rect.set_stroke(width=0)
        # Set initial fill as soft white
        bg_rect.set_fill(color="#f8f8f8", opacity=1)
        self.add(bg_rect)

        # Add a subtle gradient effect using two overlapping rectangles
        gradient_top = Rectangle(width=config.frame_width, height=config.frame_height/2)
        gradient_top.set_fill(color="#ffffff", opacity=0.3)
        gradient_top.set_stroke(width=0)
        gradient_top.move_to(UP*config.frame_height/4)

        gradient_bottom = Rectangle(width=config.frame_width, height=config.frame_height/2)
        gradient_bottom.set_fill(color="#e8e8e8", opacity=0.3)
        gradient_bottom.set_stroke(width=0)
        gradient_bottom.move_to(DOWN*config.frame_height/4)

        self.add(gradient_top, gradient_bottom)

        # ----------------------
        # 2. Logo and Glow
        # ----------------------
        logo = ImageMobject("assets/images/logo.png")
        logo.scale(0.8)
        logo.set_opacity(0)

        glow = SurroundingRectangle(logo, color=LOGO_GLOW_COLOR, buff=0.25)
        glow.set_stroke(width=12)
        glow.set_opacity(0)

        tagline = Text("Innovate. Learn. Excel.", font_size=36, color=TAGLINE_COLOR)
        tagline.next_to(logo, DOWN, buff=0.5).shift(RIGHT * 6)

        title = Text("ImransLab", font_size=64, color=TITLE_COLOR)
        title.next_to(logo, UP, buff=1.0).shift(UP * 2)

        # Particle sparkles
        particles = VGroup(*[
            Dot(point=[random.uniform(-6,6), random.uniform(-3,3),0], radius=0.05, color=PURE_PINK)
            for _ in range(15)
        ])

        # Light streaks
        streaks = VGroup()
        for y in [-2, -1, 0, 1, 2]:
            s = Line([-7,y,0], [7,y,0])
            s.set_stroke(width=2, color=LIGHT_STREAK_COLOR, opacity=0.3)
            streaks.add(s)
        self.add(streaks, particles)

        # ----------------------
        # 3. Logo Fade-In and Glow
        # ----------------------
        self.play(
            AnimationGroup(
                FadeIn(logo, scale=0.5, run_time=1),
                logo.animate.set_opacity(1).set_run_time(1),
                FadeIn(glow, run_time=1),
                lag_ratio=0.3
            )
        )

        self.play(
            AnimationGroup(
                glow.animate.set_stroke(width=16).scale(1.05).set_opacity(0.8),
                logo.animate.scale(1.05),
                run_time=0.6,
                lag_ratio=0.2
            )
        )
        self.play(glow.animate.set_opacity(0), run_time=0.3)

        # ----------------------
        # 4. Light Streaks Move
        # ----------------------
        self.play(*[s.animate.shift(RIGHT*14).set_opacity(0) for s in streaks], run_time=2, rate_func=linear)

        # ----------------------
        # 5. Tagline + Title Slide-In
        # ----------------------
        self.play(
            AnimationGroup(
                tagline.animate.shift(LEFT * 6).rotate(PI/36),
                title.animate.shift(DOWN * 2).scale(1.05).rotate(-PI/60),
                run_time=2,
                lag_ratio=0.2
            )
        )

        # ----------------------
        # 6. Particles Move
        # ----------------------
        self.play(
            *[p.animate.shift(UP*random.uniform(0.5,1)).set_opacity(0) for p in particles],
            run_time=1.5,
            lag_ratio=0.05
        )

        # ----------------------
        # 7. Final Glow Pulse
        # ----------------------
        final_glow = SurroundingRectangle(logo, color=LOGO_GLOW_COLOR, buff=0.3)
        final_glow.set_stroke(width=18, opacity=0.8)
        self.add(final_glow)
        self.play(final_glow.animate.set_opacity(0.5).scale(1.1), run_time=0.6, rate_func=there_and_back)
        self.play(FadeOut(final_glow), run_time=0.2)

        # ----------------------
        # 8. Clean Fade-Out
        # ----------------------
        self.play(
            AnimationGroup(
                FadeOut(logo, shift=UP),
                FadeOut(tagline, shift=DOWN),
                FadeOut(title, shift=UP),
                FadeOut(gradient_top),
                FadeOut(gradient_bottom),
                bg_rect.animate.set_fill(opacity=0),
                run_time=1.5,
                lag_ratio=0.2
            )
        )
