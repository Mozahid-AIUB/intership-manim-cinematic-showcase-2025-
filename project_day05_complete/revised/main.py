# main.py
from manim import *
from manim import config
import math
import numpy as np
import random
from typing import List

# --------------------
# Small utilities
# --------------------
def hex_to_rgb_tuple(h: str):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def lerp_color_hex(a: str, b: str, t: float) -> str:
    ra, ga, ba = hex_to_rgb_tuple(a)
    rb, gb, bb = hex_to_rgb_tuple(b)
    r = int(round(ra + (rb - ra) * t))
    g = int(round(ga + (gb - ga) * t))
    b = int(round(ba + (bb - ba) * t))
    return f"#{r:02x}{g:02x}{b:02x}"

def there_and_back_with_pause(t):
    # custom rate func: go then small pause at end
    if t < 0.85:
        return there_and_back(t / 0.85)
    else:
        return 1.0

# --------------------
# Main cinematic scene (MasterScene)
# --------------------
class MasterScene(MovingCameraScene):
    """
    Cinematic JWST deployment + L2 explainer with a deep background and
    an Earth->L2 transfer visualization (moving telescope + sunshield orientation).
    """

    def construct(self):
        # Build background first (updaters run continuously)
        self.init_background_components()
        self.add_vignette_and_grade()
        self.intro()
        self.deployment_sequence()
        self.l2_explainer()  # includes transfer animation now
        self.outro()

    # --------------------
    # Background initialization
    # --------------------
    def init_background_components(self):
        self.bg_far = self.create_starfield(n=140, radius=0.012, speed_range=(0.2, 0.6), z_index=0)
        self.bg_mid = self.create_starfield(n=110, radius=0.018, speed_range=(0.6, 1.4), z_index=1)
        self.bg_near = self.create_starfield(n=60, radius=0.03, speed_range=(1.6, 3.0), z_index=2, twinkle_stronger=True)

        self.nebula = self.create_nebula(blobs=5)
        self.galaxy = self.create_spiral_galaxy(arms=2, points=220, spiral_tightness=0.25)

        # Comet emitter: schedule updater by attaching it to an invisible Dot (dummy)
        self._comet_particles = []
        self._comet_chance = 0.09
        self._comet_dummy = Dot(radius=0.001, fill_opacity=0)
        self._comet_dummy.add_updater(self._comet_emitter_updater)

        # Camera clock for sway/updater
        self._camera_clock = ValueTracker(0.0)
        self.camera.frame.add_updater(self._camera_sway)

        # Add background objects in z order
        self.add(self.bg_far)
        self.add(self.nebula)
        self.add(self.galaxy)
        self.add(self.bg_mid)
        self.add(self.bg_near)
        # keep the comet dummy active (must be added to the scene)
        self.add(self._comet_dummy)

    # --------------------
    # Updater suspend / resume helpers (fix deepcopy/pickle errors)
    # --------------------
    def _suspend_critical_updaters(self):
        try:
            self.camera.frame.remove_updater(self._camera_sway)
        except Exception:
            pass
        try:
            self._comet_dummy.remove_updater(self._comet_emitter_updater)
        except Exception:
            pass

    def _resume_critical_updaters(self):
        try:
            self.camera.frame.add_updater(self._camera_sway)
        except Exception:
            pass
        try:
            self._comet_dummy.add_updater(self._comet_emitter_updater)
        except Exception:
            pass

    # --------------------
    # Starfield factory
    # --------------------
    def create_starfield(self, n=100, radius=0.02, speed_range=(0.5, 1.5), z_index=0, twinkle_stronger=False):
        group = VGroup()
        half_w = config.frame_width / 2
        half_h = config.frame_height / 2
        for i in range(n):
            x = random.uniform(-half_w - 1, half_w + 1)
            y = random.uniform(-half_h - 1, half_h + 1)
            star = Dot(radius=radius).move_to(np.array([x, y, 0]))
            star.base_opacity = random.uniform(0.18, 0.85)
            star.phase = random.uniform(0, TAU)
            star.twinkle_speed = random.uniform(speed_range[0], speed_range[1])
            color_choice = random.random()
            if color_choice < 0.05:
                star.set_fill("#ffd8b3", opacity=star.base_opacity)
            elif color_choice > 0.92:
                star.set_fill("#cfe6ff", opacity=star.base_opacity)
            else:
                star.set_fill(WHITE, opacity=star.base_opacity)

            def make_twinkle(s, stronger=twinkle_stronger):
                def tw(s_obj, dt):
                    s_obj.phase += dt * s_obj.twinkle_speed
                    amp = 0.6 if stronger else 0.45
                    s_obj.set_opacity(max(0.06, s_obj.base_opacity * (0.75 + amp * abs(math.sin(s_obj.phase)))))
                return tw
            star.add_updater(make_twinkle(star))
            group.add(star)
        group.set_z_index(z_index)
        return group

    # --------------------
    # Nebula factory
    # --------------------
    def create_nebula(self, blobs=5):
        neb = VGroup()
        palette = ["#12203a", "#26304a", "#2b1a3f", "#1e2240", "#2a1630"]
        for i in range(blobs):
            radius = random.uniform(2.6, 4.2) - i * 0.2
            blob = Circle(radius=radius, fill_color=palette[i % len(palette)], fill_opacity=0.025 + i * 0.02, stroke_opacity=0)
            blob.shift(np.array([random.uniform(-3.0, 3.0) + i*0.4, random.uniform(-0.9, 1.6) - i*0.25, 0]))
            vx = random.uniform(0.004, 0.014) * (0.6 + i*0.16)
            vy = random.uniform(-0.004, 0.009) * (0.6 + i*0.1)
            def drift_factory(b, vx=vx, vy=vy):
                def drift(b_obj, dt):
                    b_obj.shift(np.array([vx * dt, vy * dt, 0]))
                return drift
            blob.add_updater(drift_factory(blob))
            neb.add(blob)
        neb.set_z_index(-1)
        return neb

    # --------------------
    # Spiral galaxy factory
    # --------------------
    def create_spiral_galaxy(self, arms=2, points=200, spiral_tightness=0.2):
        g = VGroup()
        center = np.array([-3.0, 1.2, 0])
        base_color = "#cfcfe8"
        for i in range(points):
            t = random.random() * 6.5
            arm = i % arms
            r = (0.25 + t * spiral_tightness) * (0.6 + 0.8 * random.random())
            theta = t + (arm * (2*math.pi / arms))
            x = r * math.cos(theta) + center[0] + random.uniform(-0.38, 0.38) * 0.04
            y = r * math.sin(theta) + center[1] + random.uniform(-0.38, 0.38) * 0.02
            d = Dot(radius=random.uniform(0.007, 0.02)).move_to(np.array([x, y, 0]))
            d.set_fill(base_color, opacity=0.12 + 0.6 * (1 - r / 3.5))
            d.add_updater(lambda m, dt, c=center: m.rotate(0.0006 * dt, about_point=c))
            g.add(d)
        core = Circle(radius=0.18, fill_color="#fff0c4", fill_opacity=0.06, stroke_opacity=0)
        core.move_to(center)
        g.add(core)
        g.set_z_index(-0.5)
        return g

    # --------------------
    # Comet emitter and updater (runs via invisible dot)
    # --------------------
    def _comet_emitter_updater(self, m, dt):
        if random.random() < self._comet_chance * dt:
            self.spawn_comet()
        to_remove = []
        for particle in list(self._comet_particles):
            particle["t"] += dt
            p = particle["mobject"]
            p.shift(particle["v"] * dt)
            p.shift(np.array([0.0, -0.04 * dt * particle["t"], 0]))
            new_op = max(0.0, particle["start_opacity"] * (1 - particle["t"]/particle["lifespan"]))
            p.set_opacity(new_op)
            p.scale(1 - 0.12 * dt)
            if particle["t"] >= particle["lifespan"]:
                to_remove.append(particle)
        for pr in to_remove:
            try:
                self.remove(pr["mobject"])
            except Exception:
                pass
            if pr in self._comet_particles:
                self._comet_particles.remove(pr)

    def spawn_comet(self):
        half_w = config.frame_width / 2
        half_h = config.frame_height / 2
        pos = np.array([random.uniform(-half_w, half_w), half_h + 0.3, 0])
        angle = random.uniform(-1.4, -0.2)
        speed = random.uniform(4.0, 7.0)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        length = random.randint(5, 12)
        group = VGroup()
        base_color = "#ffd9b3"
        for i in range(length):
            d = Dot(radius=0.02 * (1.0 - 0.02*i)).move_to(pos + np.array([-vx*i*0.03, -vy*i*0.03, 0]))
            d.set_fill(base_color, opacity=0.9 * (1 - i / length))
            group.add(d)
            self.add(d)
        particle_info = {
            "mobject": group,
            "v": np.array([vx * 0.26, vy * 0.26, 0]),
            "t": 0.0,
            "lifespan": random.uniform(1.4, 2.6),
            "start_opacity": 0.95,
        }
        self._comet_particles.append(particle_info)

    # --------------------
    # Vignette / grade / lens flare
    # --------------------
    def add_vignette_and_grade(self):
        vign = VGroup()
        steps = 6
        for i in range(steps):
            c = Circle(radius=config.frame_width*0.9 - i*0.3, fill_color=BLACK, fill_opacity=0.03 + i*0.04, stroke_opacity=0)
            vign.add(c)
        vign.set_z_index(50)
        self.add(vign)
        grade = Rectangle(width=config.frame_width+1, height=config.frame_height+1)
        grade.set_fill("#0b1020", opacity=0.02)
        grade.set_z_index(49)
        self.add(grade)
        self.bloom_container = VGroup()
        self.add(self.bloom_container)

    def lens_flare(self, center_point, scale=1.0):
        flare = VGroup()
        radii = [0.06, 0.12, 0.24, 0.45]
        for i, r in enumerate(radii):
            c = Circle(radius=r*scale, fill_opacity=0.18/(i+0.9), fill_color=YELLOW, stroke_opacity=0)
            c.move_to(center_point + RIGHT * (0.02 * i))
            flare.add(c)
        for j in range(4):
            seg = Ellipse(width=0.12*scale*(1+j*0.7), height=0.02*scale).rotate(PI/8 * (j-1))
            seg.set_fill(YELLOW, opacity=0.04)
            seg.move_to(center_point + RIGHT * (0.1 + j*0.06))
            flare.add(seg)
        flare.set_z_index(60)
        return flare

    # --------------------
    # Camera sway
    # --------------------
    def _camera_sway(self, frame, dt):
        self._camera_clock.set_value(self._camera_clock.get_value() + dt)
        tval = self._camera_clock.get_value()
        dx = 0.045 * math.sin(tval * 0.38)
        dy = 0.02 * math.cos(tval * 0.65)
        rot = 0.004 * math.sin(tval * 0.12)
        frame.shift(np.array([dx * dt * 6.0, dy * dt * 6.0, 0]))
        frame.rotate(rot * dt)

    # --------------------
    # Intro / Outro
    # --------------------
    def intro(self):
        brand = Text("ImransLab", font_size=64, weight=BOLD)
        title = Text("JWST — Unfolding in Space", font_size=36)
        title.next_to(brand, DOWN)
        grp = VGroup(brand, title)
        grp.set_z_index(80)
        self.play(FadeIn(grp, shift=UP), run_time=1.0)
        self.wait(0.6)
        self.play(grp.animate.to_edge(UP), run_time=0.8, rate_func=smooth)
        self.wait(0.5)

    def outro(self):
        credits = VGroup(
            Text("ImransLab", font_size=28, weight=BOLD),
            Text("Cinematic JWST — Deployment + L2 explainer", font_size=16),
            Text("Scene: automated visualization", font_size=12),
        ).arrange(DOWN, aligned_edge=LEFT, center=False).to_edge(DOWN + LEFT)
        credits.set_z_index(80)
        self.play(FadeIn(credits), run_time=0.9)
        self.wait(1.2)
        self.play(FadeOut(credits), run_time=0.6)

    # --------------------
    # Deployment sequence (unchanged except suspend/resume used earlier)
    # --------------------
    def deployment_sequence(self):
        sun = Circle(radius=0.8, fill_color=YELLOW, fill_opacity=1.0).to_edge(LEFT, buff=0.6)
        sun_label = Text("Sun", font_size=20).next_to(sun, DOWN)
        lf = self.lens_flare(sun.get_center(), scale=1.6)
        bloom = VGroup(
            Circle(radius=1.8, fill_color=YELLOW, fill_opacity=0.06, stroke_opacity=0).move_to(sun.get_center()),
            Circle(radius=2.8, fill_color=YELLOW, fill_opacity=0.03, stroke_opacity=0).move_to(sun.get_center()),
        )
        bloom.set_z_index(45)
        self.bloom_container.add(bloom)

        pallets = VGroup()
        for i in range(2):
            p = RoundedRectangle(width=0.46, height=0.22, corner_radius=0.03).set_fill("#4b4b4b", 1)
            p.shift(np.array([-1.1 + i*0.8, -0.5, 0]))
            p.set_z_index(20)
            pallets.add(p)

        shield_layers = self.create_sunshield_layers()
        shield_group = VGroup(*shield_layers, pallets).to_edge(LEFT, buff=1).set_z_index(18)

        bus = Rectangle(width=1.12, height=0.78).set_fill("#666666", 1).move_to(shield_group.get_center() + RIGHT * 3.05)
        panels = VGroup(
            Rectangle(width=0.18, height=0.42).set_fill("#2c3e50", 1).next_to(bus, LEFT, buff=0.06),
            Rectangle(width=0.18, height=0.42).set_fill("#2c3e50", 1).next_to(bus, RIGHT, buff=0.06),
        )
        dta = Rectangle(width=0.28, height=0.56).set_fill("#999999", 1).next_to(bus, UP, buff=0)

        primary = self.create_primary_mirror(hex_radius=0.185)
        primary_group = VGroup(primary)
        primary_group.move_to(bus.get_center() + RIGHT * 0.6 + UP * 0.5)
        primary_group.set_z_index(30)

        sec_body, tripod_lines = self.create_secondary_tripod()
        sec_group = VGroup(sec_body, *tripod_lines)
        sec_group.move_to(primary_group.get_top() + LEFT * 0.9)
        sec_group.set_z_index(30)

        layer_tracker = ValueTracker(0)
        hud_layers = DecimalNumber(0).add_updater(lambda m: m.set_value(layer_tracker.get_value()))
        mission_timer = ValueTracker(0.0)
        timer_display = DecimalNumber(0, num_decimal_places=1).add_updater(lambda m: m.set_value(mission_timer.get_value()))
        hud_label = Text("Layers:", font_size=18)
        timer_label = Text("t (days):", font_size=18)
        hud_bg = RoundedRectangle(corner_radius=0.08, width=2.4, height=0.4).set_fill("#08090a", 0.6).set_stroke(width=0)
        hud_group = VGroup(hud_bg, hud_label, hud_layers, timer_label, timer_display)
        hud_group.arrange(RIGHT, buff=0.25).to_corner(UR).shift(LEFT*0.2)
        hud_group.set_z_index(80)

        self.play(FadeIn(sun), FadeIn(sun_label), FadeIn(lf), FadeIn(bloom), run_time=1.0)
        self.wait(0.06)
        self.play(FadeIn(shield_group), FadeIn(bus), DrawBorderThenFill(dta), FadeIn(panels), run_time=1.0)
        self.play(FadeIn(primary_group), FadeIn(sec_group), run_time=0.9)
        self.add(hud_group)

        # Temporarily suspend critical updaters to avoid deepcopy/pickle issues
        self._suspend_critical_updaters()
        self.play(self.camera.frame.animate.scale(0.82).move_to(shield_group.get_center() + RIGHT * 1.1),
                  run_time=1.15, rate_func=smooth)
        self._resume_critical_updaters()

        # 1) Pallet release & DTA extension (animated)
        self.play(LaggedStart(*[p.animate.shift(DOWN*0.25 + RIGHT*0.06).set_fill("#3e3e3e") for p in pallets], lag_ratio=0.08),
                  dta.animate.shift(UP*1.5), run_time=1.6)
        self.play(mission_timer.animate.set_value(0.5), run_time=0.6)

        # 2) mid-booms extend
        left_mid = Line(bus.get_center(), bus.get_center() + LEFT*1.45, stroke_width=4).set_z_index(22)
        right_mid = Line(bus.get_center(), bus.get_center() + RIGHT*1.45, stroke_width=4).set_z_index(22)
        self.add(left_mid, right_mid)
        self.play(GrowFromCenter(left_mid), GrowFromCenter(right_mid), bus.animate.shift(LEFT*0.05), run_time=1.05)
        self.play(mission_timer.animate.set_value(1.3), run_time=0.5)

        # 3) tension solar shield layers with tether visuals
        for i, layer in enumerate(shield_layers, start=1):
            tether = Line(pallets[0].get_top() + RIGHT*0.1, layer.get_bottom() + RIGHT*0.05, stroke_width=1, stroke_color="#a3a3a3")
            tether.set_z_index(25)
            self.play(Create(tether), layer.animate.set_fill(opacity=1).scale(1.01), run_time=0.45)
            layer_tracker.set_value(i)
            self.play(mission_timer.animate.set_value(round(1.2 + 0.3*i, 1)), run_time=0.25)
            self.wait(0.06)

        # 4) secondary boom + tripod deploy
        self.play(sec_group.animate.shift(RIGHT*0.62 + UP*0.22), run_time=0.95)
        self.play(LaggedStart(*[GrowFromCenter(l) for l in tripod_lines], lag_ratio=0.11), run_time=0.9)
        self.play(mission_timer.animate.set_value(3.0), run_time=0.5)

        # 5) primary wing deployment (left wing) with motion trail
        center = primary.get_center()
        left_wing = VGroup(*[m for m in primary if m.get_center()[0] < center[0]])
        if len(left_wing) > 0:
            hinge_point = left_wing.get_right()
            self.play(LaggedStart(*[m.animate.set_fill(color="#FFD27A") for m in left_wing], lag_ratio=0.03), run_time=0.46)
            self.play(left_wing.animate.shift(LEFT*0.03 + DOWN*0.02), run_time=0.22)
            self.add_motion_trail(left_wing, hinge_point, -PI*0.42, steps=8)
            self.play(Rotate(left_wing, angle=-PI*0.42, about_point=hinge_point), run_time=1.2, rate_func=there_and_back_with_pause)
            self.play(mission_timer.animate.set_value(4.5), run_time=0.5)

        # camera pull back to show assembled telescope
        self._suspend_critical_updaters()
        self.play(self.camera.frame.animate.scale(1.12).move_to(primary_group.get_center()).shift(UP*0.12),
                  run_time=1.0, rate_func=smooth)
        self._resume_critical_updaters()

        self.wait(0.6)
        glint = Circle(radius=0.14, fill_color="#fff6b3", fill_opacity=0.11).move_to(primary_group.get_center() + UP*0.15 + RIGHT*0.18)
        self.play(FadeIn(glint), glint.animate.scale(1.6).set_opacity(0.02), run_time=0.9)
        self.play(FadeOut(glint), run_time=0.5)
        self.wait(0.4)

    # --------------------
    # L2 explainer + Transfer visualization (fixed dashed trajectory)
    # --------------------
    def l2_explainer(self):
        # Clear foreground but preserve background updaters by re-adding them
        self.clear()
        self.add(self.bg_far, self.nebula, self.galaxy, self.bg_mid, self.bg_near, self._comet_dummy)
        # re-add overlays
        self.add_vignette_and_grade()

        # Sun and Earth placement
        sun = Circle(radius=0.58, fill_color=YELLOW, fill_opacity=1).to_edge(LEFT)
        earth = Circle(radius=0.28, fill_color=BLUE, fill_opacity=1).to_edge(RIGHT, buff=3)
        sun_label = Text("Sun", font_size=20).next_to(sun, DOWN)
        earth_label = Text("Earth", font_size=20).next_to(earth, DOWN)

        # L2 point
        l2_pos = earth.get_center() + RIGHT * 1.6
        l2 = Dot(point=l2_pos, color=WHITE)
        l2_label = Text("L2", font_size=18).next_to(l2, UP)
        halo = Circle(radius=0.6, color=WHITE).move_to(l2.get_center()).set_stroke(WHITE, 0.8).set_fill(opacity=0)
        orbit = Circle(radius=0.45).move_to(l2.get_center()).set_stroke(WHITE, 0.35, opacity=0.6)

        # show sun-earth line for alignment context
        sun_earth_line = Line(sun.get_right(), earth.get_left(), stroke_width=2, stroke_opacity=0.45).set_stroke(WHITE, 1, opacity=0.45)
        sun_earth_label = Text("Sun–Earth line", font_size=14).next_to(sun_earth_line.get_center(), DOWN*0.8)

        # dashed transfer trajectory (smooth bezier-like path)
        start = earth.get_center()
        end = l2.get_center()
        ctrl1 = start + (end - start) * 0.28 + UP * 1.2
        ctrl2 = start + (end - start) * 0.68 + UP * 0.6
        path_points = [start, ctrl1, ctrl2, end]

        # underlying smooth path (used for MoveAlongPath)
        traj = VMobject()
        traj.set_points_smoothly([*path_points])
        traj.set_stroke(WHITE, 2, opacity=0.65)
        traj.set_z_index(40)

        # create a dashed visual copy using DashedVMobject (correct method for dashed curves)
        dashed_traj = DashedVMobject(traj, num_dashes=38, dashed_ratio=0.5)
        dashed_traj.set_stroke(WHITE, 2, opacity=0.65)
        dashed_traj.set_z_index(40)

        # Telescope icon (small group: body + mirror + sunshield)
        telescope_body = Rectangle(width=0.22, height=0.12, fill_color="#6c6c6c", fill_opacity=1, stroke_opacity=0)
        telescope_mirror = Circle(radius=0.045, fill_color="#D4AF37", fill_opacity=0.95).next_to(telescope_body, LEFT, buff=0.04)
        sunshield_rect = Rectangle(width=0.34, height=0.06, fill_color="#d2a86f", fill_opacity=0.9, stroke_opacity=0)
        telescope_icon = VGroup(sunshield_rect, telescope_body, telescope_mirror)
        telescope_icon.arrange(RIGHT, buff=0.02)
        telescope_icon.move_to(start)
        telescope_icon.set_z_index(60)

        # initial sunshield orientation
        initial_angle = math.atan2(telescope_icon.get_center()[1] - sun.get_center()[1],
                                   telescope_icon.get_center()[0] - sun.get_center()[0])
        sunshield_rect.rotate(initial_angle + PI/2, about_point=sunshield_rect.get_center())

        traj_label = Text("Transfer trajectory", font_size=16).next_to(traj.get_center(), UP*0.6)
        dist_label = Text("≈ 1.5 million km", font_size=16).next_to(l2, DOWN)

        # show map: Sun, Earth, L2, sun-earth line, trajectory
        self.play(FadeIn(sun), FadeIn(sun_label), FadeIn(earth), FadeIn(earth_label), run_time=0.9)
        self.play(Create(sun_earth_line), Write(sun_earth_label), run_time=0.8)
        self.wait(0.2)
        self.play(FadeIn(l2), Write(l2_label))
        self.play(Create(halo), run_time=0.6)
        self.play(Create(orbit), run_time=0.8)
        # create dashed visual trajectory
        self.play(Create(dashed_traj), Write(traj_label), run_time=1.0)
        self.play(Write(dist_label), run_time=0.6)

        # Animate telescope moving along the underlying smooth path (traj)
        self.play(FadeIn(telescope_icon), run_time=0.45)

        # updater to orient the sunshield to face away from Sun (so it blocks Sun)
        sunshield_rect.add_updater(lambda m, dt, sun_ref=sun, tel_ref=telescope_icon: m.set_angle(
            math.atan2(sun_ref.get_center()[1] - tel_ref.get_center()[1],
                       sun_ref.get_center()[0] - tel_ref.get_center()[0]) + PI/2
        ))

        # Move along the underlying traj; suspend critical updaters to avoid deepcopy issues
        self._suspend_critical_updaters()
        self.play(MoveAlongPath(telescope_icon, traj, run_time=3.0, rate_func=smooth))
        self._resume_critical_updaters()

        # show blocking triangle to demonstrate sunshield orientation
        block_triangle = Polygon(sun.get_right(), telescope_icon.get_left() + UP*0.06, telescope_icon.get_left() + DOWN*0.06)
        block_triangle.set_fill("#000000", opacity=0.55).set_stroke(width=0)
        block_triangle.set_z_index(55)
        self.play(FadeIn(block_triangle), run_time=0.6)
        self.wait(1.0)

        # cleanup updater on sunshield to prevent later side-effects
        try:
            sunshield_rect.clear_updaters()
        except Exception:
            pass

        self.wait(0.6)

    # --------------------
    # Helpers reused from earlier code
    # --------------------
    def create_sunshield_layers(self):
        layers = []
        widths = [2.8, 2.6, 2.4, 2.2, 2.0]
        n = len(widths)
        for idx, w in enumerate(widths, start=1):
            rect = RoundedRectangle(width=w, height=0.38, corner_radius=0.05)
            t = idx / (n + 1)
            color = lerp_color_hex('#f0d9b5', '#c9a86f', t)
            rect.set_fill(color, opacity=0.78 - idx*0.06)
            rect.set_stroke('#222222', 0.35)
            seam = Line(rect.get_left() + RIGHT*0.08, rect.get_right() + LEFT*0.08, stroke_width=0.6, stroke_color="#b8a07a").shift(UP*0.02)
            micro = VGroup()
            for m in range(6):
                tiny = Line(ORIGIN, RIGHT*0.08).rotate(random.uniform(0, TAU)).set_stroke(width=0.4, opacity=0.08)
                tiny.shift(rect.get_center() + np.array([random.uniform(-w/2+0.1, w/2-0.1), random.uniform(-0.16, 0.16), 0]))
                micro.add(tiny)
            group = VGroup(rect, seam, micro)
            group.shift(UP * (idx * 0.12))
            group.set_z_index(18 + idx)
            layers.append(group)
        return layers

    def create_primary_mirror(self, hex_radius=0.15):
        hexes = VGroup()
        size = hex_radius
        positions = []
        for q in range(-2, 3):
            for r in range(-2, 3):
                if abs(q + r) <= 2:
                    positions.append((q, r))
        if len(positions) > 18:
            positions.pop()
        for i, (q, r) in enumerate(positions):
            x = size * 3/2 * q
            y = size * math.sqrt(3) * (r + q/2)
            h = RegularPolygon(n=6, start_angle=PI/6, radius=size)
            tint = 0.92 - (i % 3) * 0.05
            h.set_fill("#D4AF37", opacity=tint)
            h.set_stroke('#5a4b2f', 0.6)
            h.move_to(np.array([x, y, 0]))
            inner = RegularPolygon(n=6, start_angle=PI/6, radius=size*0.92)
            inner.set_stroke('#2b2b2b', 0.12)
            inner.move_to(h.get_center())
            if random.random() < 0.18:
                highlight = Arc(radius=size*0.55, angle=PI*0.6, stroke_width=1.2).move_to(h.get_center()).rotate(random.uniform(-0.8, 0.8))
                highlight.set_stroke("#fff7d2", 0.5, opacity=0.12)
                hexes.add(VGroup(h, inner, highlight))
            else:
                hexes.add(VGroup(h, inner))
        hexes.set_z_index(30)
        return hexes

    def create_secondary_tripod(self):
        sec = Circle(radius=0.12, fill_color="#d9d2b4", fill_opacity=1).set_stroke('#8a6d2f', 0.6)
        lines = VGroup(
            Line(ORIGIN, LEFT*0.4 + DOWN*0.5, stroke_width=2),
            Line(ORIGIN, RIGHT*0.4 + DOWN*0.5, stroke_width=2),
            Line(ORIGIN, DOWN*0.55, stroke_width=2),
        )
        for l in lines:
            l.shift(sec.get_center())
        return sec, lines

    def add_motion_trail(self, mobject, about_point, angle, steps=6):
        ghosts = VGroup()
        for s in range(1, steps+1):
            frac = s / (steps + 1)
            copy = mobject.copy().set_opacity(max(0.03, 0.28*(1-frac)))
            copy.rotate(angle * frac, about_point=about_point)
            copy.shift(np.array([frac*0.01, -frac*0.002, 0]))
            copy.set_stroke(width=0)
            for sub in copy:
                if hasattr(sub, "set_fill"):
                    try:
                        sub.set_fill(sub.get_fill_color(), opacity=sub.get_fill_opacity()*0.8)
                    except Exception:
                        pass
            ghosts.add(copy)
        ghosts.set_z_index(25)
        self.add(ghosts)
        self.play(LaggedStart(*[FadeOut(g, run_time=0.6) for g in ghosts], lag_ratio=0.03), run_time=0.6)

# End of file
