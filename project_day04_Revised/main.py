from manim import *
import numpy as np
import random

def create_rocket(scale=0.9):
    # compact rocket from original file, returned as VGroup with .flames property
    body = RoundedRectangle(corner_radius=0.32, width=1.0, height=2.4,
                            fill_color="#CCCCCC", fill_opacity=1, stroke_color=BLACK, stroke_width=2)
    nose = Polygon(
        np.array([0, 1.45, 0]),
        np.array([-0.6, 0.65, 0]),
        np.array([0.6, 0.65, 0]),
    ).set_fill("#FF8C00", opacity=1).set_stroke(BLACK, 2)
    nose.next_to(body, UP, buff=-0.02)

    booster_left = RoundedRectangle(corner_radius=0.18, width=0.45, height=1.9,
                                    fill_color="#D9534F", fill_opacity=1, stroke_color=BLACK, stroke_width=2)
    booster_right = booster_left.copy()
    booster_left.next_to(body, LEFT, buff=0.06).shift(DOWN * 0.08)
    booster_right.next_to(body, RIGHT, buff=0.06).shift(DOWN * 0.08)

    window_top = RoundedRectangle(corner_radius=0.07, width=0.45, height=0.35,
                                  fill_color="#88D7FF", fill_opacity=1, stroke_color=BLACK, stroke_width=2)
    window_bottom = RoundedRectangle(corner_radius=0.06, width=0.32, height=0.26,
                                     fill_color="#5BC0DE", fill_opacity=1, stroke_color=BLACK, stroke_width=2)
    window_top.move_to(body.get_center() + UP * 0.25)
    window_bottom.move_to(body.get_center() + DOWN * 0.25)

    fin_left = Polygon(
        np.array([-0.65, -0.2, 0]),
        np.array([-1.1, -0.5, 0]),
        np.array([-0.2, -0.55, 0]),
    ).set_fill("#9E9E9E", opacity=1).set_stroke(BLACK, 1.5)

    fin_right = Polygon(
        np.array([0.65, -0.2, 0]),
        np.array([1.1, -0.5, 0]),
        np.array([0.2, -0.55, 0]),
    ).set_fill("#9E9E9E", opacity=1).set_stroke(BLACK, 1.5)

    flame_outer = Polygon(
        np.array([0.15, -0.05, 0]),
        np.array([-0.45, -1.05, 0]),
        np.array([0.45, -1.05, 0]),
    ).set_fill("#FF6A00", opacity=1).set_stroke("#FF3B00", 1)

    flame_mid = Polygon(
        np.array([0.0, -0.05, 0]),
        np.array([-0.32, -0.85, 0]),
        np.array([0.32, -0.85, 0]),
    ).set_fill("#FFD24C", opacity=1).set_stroke("#FF8C00", 0.8)

    flame_core = Polygon(
        np.array([0.0, -0.05, 0]),
        np.array([-0.12, -0.55, 0]),
        np.array([0.12, -0.55, 0]),
    ).set_fill("#FF3B00", opacity=1).set_stroke("#FF8C00", 0.6)

    flames = VGroup(flame_outer, flame_mid, flame_core).shift(DOWN * 1.15)

    rocket = VGroup(body, nose, booster_left, booster_right, window_top, window_bottom, fin_left, fin_right, flames)
    rocket.scale(scale)
    rocket.flames = flames  # attach for easy access
    return rocket

def make_parallax_stars(n=60, spread=8, color="#FFF9C4", scale_range=(0.03, 0.12)):
    # returns VGroup of dots for a star layer
    stars = VGroup()
    for _ in range(n):
        r = random.uniform(*scale_range)
        x = random.uniform(-spread, spread)
        y = random.uniform(-spread/2, spread/2)
        dot = Circle(radius=r, fill_color=color, fill_opacity=1, stroke_opacity=0).move_to([x, y, 0])
        stars.add(dot)
    return stars

def quadratic_bezier(p0, p1, p2, t):
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2

# Easing function used by animations (Manim accepts any callable t->[0,1])
def ease_out_expo(t: float) -> float:
    # exponential ease-out: fast start, slow finish
    if t <= 0:
        return 0.0
    if t >= 1:
        return 1.0
    return 1.0 - 2 ** (-10 * t)

def s1_launch(scene: MovingCameraScene):
    """
    Cinematic liftoff with automatic transition to "space mode":
    - while low (in atmosphere): dense particles, big glow, clouds visible
    - after crossing altitude threshold: reduce atmosphere effects, rocket scales down (appears farther),
      particle spawn rate decreases, flames become tighter/longer on the rocket tail,
      starfield/background becomes more visible.
    """
    scene.camera.frame.save_state()
    scene.camera.background_color = "#07162a"
    bg_glow = VGroup(
        Circle(radius=12, fill_color="#07162a", fill_opacity=1, stroke_opacity=0),
        Circle(radius=7, fill_color="#0e2b3d", fill_opacity=0.45, stroke_opacity=0).shift(UP * 1.2)
    )
    scene.add(bg_glow)

    # Rocket + pad
    rocket = create_rocket(scale=0.38)
    rocket.move_to(np.array([0.0, -3.2, 0]))
    scene.add(rocket)
    pad = RoundedRectangle(corner_radius=0.1, width=3.2, height=0.12,
                           fill_color="#111214", fill_opacity=1, stroke_color=BLACK, stroke_width=1)
    pad.move_to(rocket.get_bottom() + DOWN * 0.06)
    scene.add(pad)

    # clouds and glow layers
    def make_clouds(center_x=0.0, n=18):
        group = VGroup()
        for i in range(n):
            r = random.uniform(0.18, 0.9)
            x = center_x + random.uniform(-1.2, 1.2)
            y = rocket.get_bottom()[1] + random.uniform(-0.1, 0.6)
            c = Circle(radius=r, fill_color=WHITE, fill_opacity=0.0, stroke_opacity=0).move_to([x, y, 0])
            group.add(c)
        return group
    clouds = make_clouds(n=20)
    scene.add(clouds)

    glow_layers = VGroup(
        Circle(radius=0.18, fill_color="#FF8C00", fill_opacity=0.0, stroke_opacity=0).move_to(rocket.get_bottom()),
        Circle(radius=0.38, fill_color="#FF3B00", fill_opacity=0.0, stroke_opacity=0).move_to(rocket.get_bottom()),
        Circle(radius=0.9, fill_color="#FFB86B", fill_opacity=0.0, stroke_opacity=0).move_to(rocket.get_bottom()),
    )
    scene.add(glow_layers)

    # particle pool + traced trail
    particle_count = 120
    particles = VGroup()
    for _ in range(particle_count):
        p = Dot(radius=random.uniform(0.02, 0.06), color=random.choice(["#FF3B00", "#FF6A00", "#FFD24C"]))
        p.move_to(rocket.get_bottom() + np.array([random.uniform(-0.15, 0.15), random.uniform(-0.08, 0.08), 0]))
        p.v = np.array([0.0, 0.0, 0.0])
        p.life = 0.0
        p.set_opacity(0.0)
        particles.add(p)
    scene.add(particles)

    trail = TracedPath(lambda: rocket.get_bottom(), stroke_color="#FF6A00", stroke_width=2.0, dissipating_time=3.2)
    scene.add(trail)

    # ascent path
    start = rocket.get_center()
    control = start + np.array([0.0, 3.8, 0.0])
    apex = start + np.array([0.0, 11.8, 0.0])
    path = ParametricFunction(lambda t: quadratic_bezier(start, control, apex, t), t_range=(0, 1), color=LIGHT_GREY, stroke_width=0.0)
    scene.add(path)

    # small altitude tracker (optional)
    alt = ValueTracker(start[1])
    alt_display = always_redraw(lambda: DecimalNumber(int(alt.get_value())).set_color(WHITE).scale(0.6).to_corner(UL).shift(RIGHT * 0.2))
    scene.add(alt_display)

    # countdown + ignition (kept same behaviour)
    center_pos = np.array([0, 0.8, 0])
    for label in ["3", "2", "1", "0"]:
        txt = Text(label, font_size=160, weight=BOLD).move_to(center_pos).set_color(WHITE)
        scene.play(FadeIn(txt, scale=1.6), run_time=0.45, rate_func=there_and_back)
        if label == "0":
            scene.wait(0.06)
            scene.play(
                glow_layers[2].animate.set_fill("#FFB86B", opacity=0.55).scale(1.6),
                glow_layers[1].animate.set_fill("#FF3B00", opacity=0.9).scale(1.2),
                glow_layers[0].animate.set_fill("#FF8C00", opacity=1.0).scale(1.05),
                run_time=0.18,
                rate_func=rush_from
            )
            scene.play(
                LaggedStart(*[
                    c.animate.set_fill(WHITE, opacity=random.uniform(0.75, 0.95)).scale(random.uniform(1.2, 2.4)).shift(UP * random.uniform(0.25, 1.0))
                    for c in clouds
                ], lag_ratio=0.02),
                run_time=0.9,
                rate_func=ease_out_expo
            )
            for p in particles:
                angle = random.uniform(-0.75 * np.pi, -0.25 * np.pi)
                speed = random.uniform(3.2, 7.8)
                p.v = np.array([speed * np.cos(angle), speed * np.sin(angle), 0.0]) * 0.35
                p.life = random.uniform(0.8, 1.6)
                p.set_opacity(1.0)
            scene.play(rocket.flames.animate.set_scale(2.5), run_time=0.14)
            scene.play(scene.camera.frame.animate.scale(0.96), run_time=0.12)
            scene.wait(0.06)
        else:
            scene.wait(0.25)
        scene.play(FadeOut(txt), run_time=0.15)

    # dynamic spawn probability (mutable container so updaters can change it)
    spawn_prob = [0.08]

    # particle physics using the mutable spawn_prob
    def particle_emitter(dt):
        nozzle = rocket.get_bottom()
        # update altitude tracker
        alt.set_value(rocket.get_center()[1])
        for p in particles:
            if p.life > 0:
                p.move_to(p.get_center() + p.v * dt)
                p.v = p.v + np.array([random.uniform(-0.8, 0.8), random.uniform(0.8, 2.4), 0.0]) * dt * 0.6
                p.life -= dt
                p.set_opacity(max(0.0, p.life / 1.6))
            else:
                if random.random() < spawn_prob[0]:
                    p.move_to(nozzle + np.array([random.uniform(-0.12, 0.12), random.uniform(-0.06, 0.06), 0]))
                    angle = random.uniform(-0.6 * np.pi, -0.4 * np.pi)
                    speed = random.uniform(2.6, 5.5)
                    p.v = np.array([speed * np.cos(angle), speed * np.sin(angle), 0.0]) * 0.45
                    p.life = random.uniform(0.6, 1.1)
                    p.set_opacity(random.uniform(0.7, 1.0))

    # camera shake and flame liveliness updaters (unchanged)
    shake_strength = 0.045
    def camera_shake(m, dt):
        t = scene.time
        decay = max(0.0, 1.0 - (t - 0.2) * 0.15)
        offset = np.array([random.uniform(-shake_strength, shake_strength), random.uniform(-shake_strength, shake_strength), 0.0]) * decay
        rot = 0.004 * np.sin(50 * t) * decay
        m.move_to((apex - UP * 3) + offset)
        m.set_angle(rot)

    def flame_live(m, dt):
        # Make flame longer / tighter as rocket reaches space (space-mode increases core flare)
        base = 1.9 + 0.2 * np.sin(scene.time * 28)
        # when in space, increase core length multiplier
        multiplier = 1.0
        if getattr(scene, "_entered_space", False):
            multiplier = 2.6
        for i, sub in enumerate(m.flames):
            sub.set_scale(base * (0.9 + i * 0.06) * multiplier)
            sub.set_fill(["#FF3B00", "#FF6A00", "#FFD24C"][i], opacity=1.0)

    # flight-phase updater: toggles between atmosphere and space modes based on rocket height
    def flight_phase_updater(dt):
        # scene.add_updater passes only dt, so use closure variables (rocket, scene, etc.)
        y = rocket.get_center()[1]
        # threshold altitude where atmosphere effects should reduce
        space_threshold = 5.5
        if y >= space_threshold and not getattr(scene, "_entered_space", False):
            # Enter space: reduce atmospheric visuals, make rocket appear smaller & increase tail flame core
            scene._entered_space = True
            spawn_prob[0] = 0.015       # far fewer particles
            # dim glows & clouds instantly (safe during render)
            for g in glow_layers:
                g.set_fill(g.get_fill_color(), opacity=0.12)
            for c in clouds:
                c.set_fill(WHITE, opacity=0.04)
            # thin the trail for long-distance streak
            trail.set_stroke(width=1.0)
            # scale rocket down once to simulate distance
            rocket.scale(0.62)
            # make flames more concentrated / longer on the core
            for sub in rocket.flames:
                sub.set_fill(sub.get_fill_color(), opacity=1.0)
        # optionally restore some atmosphere if rocket falls back (not used here)

    # attach updaters
    scene.camera.frame.add_updater(camera_shake)
    rocket.add_updater(flame_live)
    scene.add_updater(lambda dt: particle_emitter(dt))
    scene.add_updater(flight_phase_updater)

    # ascend
    move_rocket = MoveAlongPath(rocket, path)
    scene.play(
        move_rocket,
        scene.camera.frame.animate.move_to(apex - UP * 2.4).scale(0.78),
        clouds.animate.shift(UP * 2.2).fade(0.55),
        run_time=6.25,
        rate_func=smooth
    )

    # allow plume to trail and fade
    scene.wait(0.6)

    # cleanup: remove updaters and temporary objects
    scene.camera.frame.remove_updater(camera_shake)
    rocket.clear_updaters()
    scene.remove_updater(lambda dt: particle_emitter(dt))  # best-effort remove
    scene.remove_updater(flight_phase_updater)
    scene.play(
        LaggedStart(*[g.animate.set_opacity(0).scale(0.9) for g in glow_layers], lag_ratio=0.02),
        LaggedStart(*[p.animate.set_opacity(0).shift(DOWN * 0.8) for p in particles], lag_ratio=0.003),
        run_time=1.0
    )
    scene.play(Restore(scene.camera.frame), run_time=1.0)
    scene.remove(trail, path, particles, clouds, pad, glow_layers)

def s2_refuel_orbit(scene: MovingCameraScene):  # 25–40s
    # Set up a planet to orbit around
    planet = Circle(radius=0.9, fill_color="#6B4F3A", fill_opacity=1).to_edge(RIGHT).shift(UP * 0.6)
    ring = Circle(radius=1.6, color="#7ec0ee", stroke_width=2, fill_opacity=0).move_to(planet.get_center())
    scene.add(planet, ring)

    # Rocket smaller, start from left of screen and fly to orbit
    rocket = create_rocket(scale=0.55)
    rocket.move_to(LEFT * 4 + DOWN * 1)
    scene.add(rocket)

    # Traced path for the orbital pass (TracedPath)
    orbit_center = planet.get_center()
    r = 1.6
    t = ValueTracker(0.0)

    # rocket position updater to follow a circular param with ValueTracker
    def orbit_pos(mob):
        theta = TAU * t.get_value()
        pos = orbit_center + np.array([r * np.cos(theta), r * np.sin(theta), 0])
        mob.move_to(pos)
        # simple orientation: point tangent
        dtheta = 1e-3
        p_next = orbit_center + np.array([r * np.cos(theta + dtheta), r * np.sin(theta + dtheta), 0])
        angle = np.arctan2(p_next[1] - pos[1], p_next[0] - pos[0])
        mob.set_angle(angle - PI / 2)

    # Starting approach path (small bezier)
    approach_path = ParametricFunction(
        lambda u: quadratic_bezier(
            rocket.get_center(),
            rocket.get_center() * 0.2 + orbit_center * 0.8,
            orbit_center + LEFT * 1.2,
            u
        ),
        t_range=(0, 1),
        color=YELLOW
    )
    approach_path.set_opacity(0.7)
    scene.add(approach_path)

    # HUD: docking counter
    dock_val = DecimalNumber(0, num_decimal_places=0).to_corner(UR)
    dock_label = Text("DOCK %", font_size=24).next_to(dock_val, DOWN, buff=0.05)
    scene.add(dock_val, dock_label)

    dock_val.add_updater(lambda d: d.set_value(int(t.get_value() * 100)))

    # Run approach then orbit once with traced trail
    traced = TracedPath(rocket.get_center, stroke_color=ORANGE, stroke_width=3, dissipating_time=4)
    scene.add(traced)

    # Approach animation along approach_path
    scene.play(MoveAlongPath(rocket, approach_path), run_time=3.0, rate_func=there_and_back_with_pause if False else smooth)
    # begin circular orbit by animating t
    rocket.add_updater(orbit_pos)
    scene.play(t.animate.set_value(1.0), run_time=5.0, rate_func=linear)
    scene.wait(0.4)
    # cleanup
    rocket.clear_updaters()
    dock_val.clear_updaters()
    scene.remove(approach_path)

def make_dust_puffs(center, n=12, spread=0.6):
    group = VGroup()
    for i in range(n):
        r = random.uniform(0.06, 0.18)
        x = center[0] + random.uniform(-spread, spread)
        y = center[1] + random.uniform(-spread*0.3, spread*0.3)
        c = Circle(radius=r, fill_color="#C25A3B", fill_opacity=0.0, stroke_opacity=0).move_to([x, y, 0])
        group.add(c)
    return group

def add_film_grain(scene, intensity=0.06, count=420):
    """
    Add subtle film grain overlay. Uses camera frame size (fallbacks to safe defaults)
    to position grains in scene coordinates. Returns the VGroup of grain dots.
    """
    grains = VGroup()
    # get scene frame dimensions in scene units (safe fallback)
    frame = getattr(scene, "camera", None)
    if frame is not None and hasattr(scene.camera.frame, "get_width"):
        width = float(scene.camera.frame.get_width())
        height = float(scene.camera.frame.get_height())
    else:
        # safe defaults (approx typical Manim units)
        width, height = 14.0, 8.0

    # limit count to avoid huge slowdowns when called repeatedly
    count = min(count, 800)

    for _ in range(count):
        x = random.uniform(-width / 2, width / 2)
        y = random.uniform(-height / 2, height / 2)
        r = random.uniform(0.002, 0.01) * max(width, height) * 0.02  # scale radius to frame size a bit
        d = Dot(point=[x, y, 0], radius=r, color=WHITE)
        d.set_opacity(random.uniform(0.002, intensity))
        grains.add(d)

    grains.set_z_index(50)
    scene.add(grains)
    return grains

def s3_transfer_or_mars(scene: MovingCameraScene):  # replaced with cinematic transfer + landing
    # Wide setup: Earth left, Mars right (Mars with landing surface)
    scene.camera.frame.save_state()
    earth = Circle(radius=0.6, fill_color="#2D7FD3", fill_opacity=1).to_edge(LEFT).shift(DOWN * 0.3)
    mars = Circle(radius=0.9, fill_color="#B65A2A", fill_opacity=1).to_edge(RIGHT).shift(UP * 0.6)
    # add a subtle surface ellipse for Mars landing region (warm, slightly textured)
    mars_surface = Ellipse(width=1.6, height=0.6, fill_color="#9C4B2D", fill_opacity=0.9, stroke_opacity=0).move_to(mars.get_center() + DOWN * 0.5)
    scene.add(earth, mars, mars_surface)

    # small rocket near Earth ready for transfer
    rocket = create_rocket(scale=0.44)
    rocket.move_to(earth.get_center() + RIGHT * 1.05)
    scene.add(rocket)

    # Transfer arc (cinematic bezier) from near-Earth to a high approach point above Mars
    start = rocket.get_center()
    control = start + np.array([2.6, 4.8, 0.0])  # lift / long arc control
    approach_above_mars = mars.get_center() + np.array([-1.1, 1.4, 0.0])
    transfer_path = ParametricFunction(
        lambda t: quadratic_bezier(start, control, approach_above_mars, t),
        t_range=(0, 1),
        color=YELLOW_A,
        stroke_width=2
    )
    transfer_path.set_opacity(0.65)
    scene.add(transfer_path)

    # traced trail for long transfer
    tracer = TracedPath(lambda: rocket.get_center(), stroke_color="#FFD57A", stroke_width=3, dissipating_time=5.0)
    scene.add(tracer)

    # HUD: distance & ETA (ValueTrackers)
    dist = ValueTracker(100.0)
    eta = ValueTracker(240.0)
    dist_display = always_redraw(lambda: DecimalNumber(dist.get_value(), num_decimal_places=0).to_corner(UR))
    eta_display = always_redraw(lambda: DecimalNumber(int(eta.get_value())).to_corner(UR).shift(DOWN * 0.6))
    scene.add(dist_display, eta_display)

    # Move rocket along transfer path with slow acceleration look
    scene.play(
        MoveAlongPath(rocket, transfer_path),
        dist.animate.set_value(12.0),
        eta.animate.set_value(72.0),
        scene.camera.frame.animate.move_to(transfer_path.get_center()).scale(0.9),
        run_time=7.2,
        rate_func=lambda t: t**1.15  # mild acceleration
    )
    scene.wait(0.35)

    # Begin approach: create a descent arc from approach_above_mars to landing point on mars_surface
    landing_point = mars_surface.get_center() + DOWN * 0.08
    descent_control = approach_above_mars + np.array([0.6, -1.4, 0.0])
    descent_path = ParametricFunction(
        lambda t: quadratic_bezier(approach_above_mars, descent_control, landing_point, t),
        t_range=(0, 1),
        color=ORANGE,
        stroke_width=2
    )
    descent_path.set_opacity(0.0)
    scene.add(descent_path)

    # Add film grain subtly for realism
    grain = add_film_grain(scene, intensity=0.03, count=220)
    grain.set_opacity(0.0)
    scene.play(grain.animate.set_opacity(1.0), run_time=0.8)

    # make dust puffs at landing area (hidden)
    dusts = make_dust_puffs(landing_point, n=12, spread=0.6)
    scene.add(dusts)

    # approach along descent_path with traced descent trail and camera zoom to Mars
    rocket.add_updater(lambda m: m.set_angle(np.arctan2(descent_path.point_from_proportion(min(1, max(0, m.get_center()[1] / 10)))[1] - m.get_center()[1], 1) - PI/2))
    scene.play(
        MoveAlongPath(rocket, descent_path),
        eta.animate.set_value(4.0),
        scene.camera.frame.animate.move_to(mars.get_center()).scale(0.8),
        run_time=4.2,
        rate_func=smooth
    )
    scene.wait(0.1)

    # Landing impact: puff/dust spread + small camera bounce + energy drain HUD
    # Energy tracker to mimic fuel/energy draining on landing
    energy = ValueTracker(100.0)
    energy_display = always_redraw(lambda: DecimalNumber(energy.get_value(), num_decimal_places=0).to_corner(DL))
    scene.add(energy_display)

    # animate dust puffs (scale + fade out)
    scene.play(
        LaggedStart(*[
            d.animate.set_fill("#D98A6A", opacity=0.95).scale(random.uniform(1.8, 3.2)).shift(UP * random.uniform(0.2, 0.9)).set_opacity(0.95)
            for d in dusts
        ], lag_ratio=0.06),
        energy.animate.set_value(12.0),
        scene.camera.frame.animate.shift(UP * 0.06).scale(0.98),
        run_time=1.0,
        rate_func=there_and_back_with_pause if False else lambda t: 1 - (1 - t)**2
    )
    # tiny settle motions and final micro shakes
    scene.play(scene.camera.frame.animate.shift(DOWN * 0.03), run_time=0.35)

    # soft sparks at foot (very small dots)
    sparks = VGroup(*[
        Dot(point=landing_point + np.array([random.uniform(-0.12, 0.12), random.uniform(-0.05, 0.18), 0]),
            radius=random.uniform(0.01, 0.03), color=random.choice(["#FFD24C", "#FF8C00"]))
        for _ in range(8)
    ])
    sparks.set_opacity(0.0)
    scene.add(sparks)
    scene.play(LaggedStart(*[s.animate.set_opacity(1.0).shift(UP * random.uniform(0.06, 0.18)).fade(0.9) for s in sparks], lag_ratio=0.03), run_time=0.9)

    # final settle: fade out tracer, keep rocket on surface, small camera pullback to reveal Mars surface
    scene.play(
        FadeOut(tracer, run_time=0.8),
        scene.camera.frame.animate.move_to(mars.get_center() + RIGHT * 0.2).scale(0.85),
        run_time=1.2
    )
    scene.wait(0.6)

    # cleanup updaters and temporary objects
    rocket.clear_updaters()
    scene.remove(tracer, transfer_path, descent_path)
    # gently fade grain and sparks
    scene.play(grain.animate.set_opacity(0.0), LaggedStart(*[s.animate.set_opacity(0.0) for s in sparks], lag_ratio=0.02), run_time=0.9)

    # keep rocket on Mars surface for the outro or next beat
    scene.camera.frame.restore()

def create_asteroid_belt(n=36, radius_range=(2.6, 4.2), spread_y=1.2, color="#A88B6D"):
    belt = VGroup()
    for i in range(n):
        angle = random.uniform(0, TAU)
        r = random.uniform(*radius_range)
        x = r * np.cos(angle)
        y = r * np.sin(angle) + random.uniform(-spread_y, spread_y)
        size = random.uniform(0.04, 0.14)
        rock = Ellipse(width=size * random.uniform(0.6, 1.4), height=size * random.uniform(0.4, 1.0),
                       fill_color=color, fill_opacity=1, stroke_opacity=0).move_to([x, y, 0])
        rock.rotate(random.uniform(0, TAU))
        belt.add(rock)
    # gentle rotation to simulate belt motion
    belt.add_updater(lambda m, dt: m.rotate(0.0008 * dt))
    return belt

def create_gas_giant(center=RIGHT * 4 + UP * 0.6, base_radius=0.9, band_colors=("#C47B2E", "#D89B5A")):
    layers = VGroup()
    # create layered rings for bands
    for i in range(6):
        r = base_radius * (1.0 + i * 0.12)
        color = band_colors[i % len(band_colors)]
        c = Circle(radius=r, fill_color=color, fill_opacity=0.85 - i * 0.08, stroke_opacity=0).move_to(center)
        c.rotate(i * 0.07)
        layers.add(c)
    # subtle tilt and slow rotation
    layers.add_updater(lambda m, dt: m.rotate(0.0006 * dt))
    return layers

def create_additional_stations(scene: MovingCameraScene, count=2):
    """
    Create small extra stations. Requires scene for time-based updaters.
    """
    group = VGroup()
    positions = [UP * 1.8 + RIGHT * 0.6, UP * 0.4 + RIGHT * 2.2]
    for i in range(count):
        pos = positions[i % len(positions)] + np.array([random.uniform(-0.6, 0.6), random.uniform(-0.3, 0.3), 0])
        core = RoundedRectangle(corner_radius=0.04, width=0.34, height=0.14, fill_color="#9AA6B2", fill_opacity=1)
        panel_l = Rectangle(width=0.36, height=0.08, fill_color="#2F6B8F", fill_opacity=0.95).next_to(core, LEFT, buff=0.06)
        panel_r = Rectangle(width=0.36, height=0.08, fill_color="#2F6B8F", fill_opacity=0.95).next_to(core, RIGHT, buff=0.06)
        panels = VGroup(panel_l, panel_r)
        st = VGroup(core, panels).move_to(pos)

        # Updater uses scene.time via closure; signature (m, dt) expected by Manim
        def station_updater(m, dt, t0=random.uniform(0, 6)):
            m.rotate(0.0012 * dt)
            # small bob based on global scene.time
            bob = UP * 0.0004 * np.sin(0.8 * (scene.time + t0)) * dt
            m.shift(bob)

        st.add_updater(station_updater)
        group.add(st)
    return group

def create_space_vignette(scene: MovingCameraScene):
    """
    Enhanced space vignette — replaces previous simpler function.
    Adds: layered starfields, sun glow, Earth, Mars, gas giant, asteroid belt,
    multiple stations & satellites with subtle parallax updaters. Designed to be error-less.
    """
    # star layers
    far = make_parallax_stars(n=110, spread=34, color="#DCEEFF", scale_range=(0.02, 0.045))
    mid = make_parallax_stars(n=72, spread=22, color="#EAF6FF", scale_range=(0.03, 0.07))
    near = make_parallax_stars(n=44, spread=16, color="#FFFFFF", scale_range=(0.05, 0.11))
    far.set_z_index(0); mid.set_z_index(1); near.set_z_index(2)

    # sun with layered glows
    sun = Circle(radius=1.6, fill_color="#FFB84D", fill_opacity=0.95, stroke_opacity=0).to_corner(UR).shift(LEFT * 0.8 + DOWN * 0.35)
    sun_glow1 = Circle(radius=3.0, fill_color="#FF8C00", fill_opacity=0.06, stroke_opacity=0).move_to(sun.get_center())
    sun_glow2 = Circle(radius=5.6, fill_color="#FF7A2A", fill_opacity=0.03, stroke_opacity=0).move_to(sun.get_center())
    sun_group = VGroup(sun_glow2, sun_glow1, sun).set_z_index(0)
    sun_group.add_updater(lambda m, dt: m.shift(RIGHT * 0.0005 * np.sin(scene.time * 0.12) * dt))

    # planets
    earth = Circle(radius=1.0, fill_color="#2D7FD3", fill_opacity=1).move_to(LEFT * 3.2 + DOWN * 0.5)
    earth_shade = Circle(radius=1.05, fill_color="#07162a", fill_opacity=0.16).move_to(earth.get_center()).shift(LEFT * 0.36 + DOWN * 0.18)
    mars = Circle(radius=0.9, fill_color="#B65A2A", fill_opacity=1).move_to(RIGHT * 3.4 + UP * 0.9)
    mars_ring = Circle(radius=1.7, stroke_color="#D9825A", stroke_width=1.6, fill_opacity=0).move_to(mars.get_center()).rotate(0.38)

    # gas giant (farther out) for visual depth
    gas = create_gas_giant(center=RIGHT * 5 + UP * -0.2, base_radius=0.7, band_colors=("#A45A2D", "#C07B43"))
    gas.set_z_index(0)

    # orbital stations & small extras
    main_station = VGroup(
        RoundedRectangle(corner_radius=0.07, width=0.6, height=0.28, fill_color="#8A8A8A", fill_opacity=1),
        Rectangle(width=1.02, height=0.14, fill_color="#1F6B9A", fill_opacity=0.9)
    ).arrange(RIGHT, buff=0.08).move_to(RIGHT * 1.6 + UP * 1.05)
    main_station.set_z_index(3)

    extra_stations = create_additional_stations(scene, count=2)
    sats = VGroup(*[Dot(point=np.array([random.uniform(-6, 6), random.uniform(-3, 4), 0]),
                        radius=random.uniform(0.02, 0.06), color="#E9EEF8") for _ in range(10)])
    sats.set_z_index(2)

    # asteroid belt between planets for cinematic interest
    belt = create_asteroid_belt(n=40, radius_range=(2.6, 4.0), spread_y=1.1)
    belt.set_z_index(1)

    # subtle parallax updaters
    far.add_updater(lambda m, dt: m.shift(LEFT * 0.0018 * dt))
    mid.add_updater(lambda m, dt: m.shift(LEFT * 0.0042 * dt))
    near.add_updater(lambda m, dt: m.shift(LEFT * 0.009 * dt))
    sats.add_updater(lambda m, dt: m.shift(LEFT * 0.0024 * dt))
    main_station.add_updater(lambda m, dt: m.rotate(0.001 * dt))

    # assemble
    bg_group = VGroup(far, mid, near, sun_group, earth, earth_shade, mars, mars_ring, gas, belt, main_station, extra_stations, sats)
    scene.add(bg_group)
    return bg_group

def load_project_logo(path="assets/imranslab_logo.svg", fallback_text="Imrans Lab"):
    """
    Try to load an SVG logo from assets/. If missing, return a simple Text fallback.
    Save the Imrans Lab logo SVG at: project_folder/assets/imranslab_logo.svg
    """
    try:
        logo = SVGMobject(path)
        # normalize size and remove excessive stroke if any
        logo.set_height(1.2)
        logo.set_z_index(60)
        return logo
    except Exception:
        return Text(fallback_text, font_size=48, weight=BOLD).set_color(WHITE)

class MasterScene(MovingCameraScene):
    def construct(self):
        self.camera.frame.save_state()
        self.camera.background_color = "#07162a"

        # add persistent space vignette (planets, sun, station, parallax stars)
        space_bg = create_space_vignette(self)

        # sequence of beats
        s1_launch(self)
        s2_refuel_orbit(self)
        s3_transfer_or_mars(self)

        # Outro using Imrans Lab logo + credit (place assets/imranslab_logo.svg in project)
        logo = load_project_logo("assets/imranslab_logo.svg", fallback_text="Imrans Lab")
        credit = Text("developed by mozahid", font_size=28).set_color("#E6E6E6").to_edge(DOWN).shift(RIGHT*0.6)
        # center logo and subtle reveal
        logo.move_to(ORIGIN).set_opacity(0.0)
        self.play(FadeIn(logo, scale=0.9), run_time=1.0)
        self.play(logo.animate.set_opacity(1.0), run_time=0.6)
        # show small credit, then hold and crossfade to black
        self.play(FadeIn(credit, shift=UP * 0.2), run_time=0.7)
        self.wait(1.0)
        self.play(FadeOut(VGroup(logo, credit)), run_time=0.9)