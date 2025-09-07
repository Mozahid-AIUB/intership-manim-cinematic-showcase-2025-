from manim import *
import random
import numpy as np

# Color palette
PURE_PINK = "#ff69b4"
LOGO_GLOW_COLOR = "#ff1493"
TEXT_COLOR = "#333333"
HIGHLIGHT_COLOR = "#ff69b4"
BG_COLOR_TOP = "#f8f8f8"
BG_COLOR_BOTTOM = "#e8e8e8"
PARTICLE_COLOR = PURE_PINK
STREAK_COLOR = "#ffb6c1"
ACCENT_BLUE = "#4169e1"
ACCENT_PURPLE = "#9370db"

class MainContent(Scene):
    def construct(self):
        # Total animation time: ~3 minutes
        self.camera.background_color = WHITE
        
        # ----------------------
        # 1. Animated Background with Grid
        # ----------------------
        bg_rect = Rectangle(
            width=config.frame_width * 1.2, 
            height=config.frame_height * 1.2,
            fill_color=BG_COLOR_TOP,
            fill_opacity=1,
            stroke_width=0
        )
        self.add(bg_rect)
        
        # Create a subtle grid pattern
        grid = VGroup()
        for x in np.arange(-7, 7, 1):
            for y in np.arange(-4, 4, 1):
                dot = Dot(point=[x, y, 0], radius=0.02, color=ACCENT_BLUE, fill_opacity=0.1)
                grid.add(dot)
        self.add(grid)
        
        # ----------------------
        # 2. Title Animation with Advanced Effects
        # ----------------------
        title = Text("TEAM INNOVATORS", font_size=72, color=TEXT_COLOR, weight=BOLD)
        subtitle = Text("Pushing Creative Boundaries", font_size=36, color=TEXT_COLOR)
        subtitle.next_to(title, DOWN, buff=0.3)
        
        title_group = VGroup(title, subtitle)
        title_group.move_to(UP * 2.5)
        
        # Animated title reveal
        for letter in title:
            self.play(Write(letter), run_time=0.1)
        self.play(Write(subtitle), run_time=1.5)
        
        # Add shimmer effect to title
        title_highlight = title.copy()
        title_highlight.set_color(LOGO_GLOW_COLOR)
        self.play(
            title_highlight.animate.set_opacity(0.7),
            run_time=1,
            rate_func=there_and_back
        )
        self.remove(title_highlight)
        
        # ----------------------
        # 3. Team Members Introduction with Cards
        # ----------------------
        members = [
            {"name": "Naved", "role": "Lead Developer", "fact": "Loves AI & Machine Learning"},
            {"name": "Rakib", "role": "Creative Director", "fact": "Passionate about UI/UX Design"},
            {"name": "Demo", "role": "Project Manager", "fact": "Expert in Agile Methodologies"}
        ]
        
        # Create professional member cards
        member_cards = VGroup()
        for i, member in enumerate(members):
            # Card with gradient background
            card = RoundedRectangle(
                width=5, 
                height=2.5, 
                corner_radius=0.3,
                fill_color=WHITE,
                fill_opacity=0.95,
                stroke_color=ACCENT_BLUE,
                stroke_width=3
            )
            
            # Add subtle shadow effect
            card.shadow = Rectangle(
                width=5.1, 
                height=2.6, 
                fill_color=BLACK,
                fill_opacity=0.2,
                stroke_width=0
            )
            card.shadow.move_to(card.get_center() + DOWN*0.05 + RIGHT*0.05)
            
            # Member info with proper styling
            name_text = Text(member["name"], font_size=38, color=TEXT_COLOR, weight="BOLD")
            role_text = Text(member["role"], font_size=26, color=ACCENT_BLUE)
            fact_text = Text(member["fact"], font_size=22, color=TEXT_COLOR)
            
            # Position text elements
            name_text.move_to(card.get_top() + DOWN * 0.5)
            role_text.next_to(name_text, DOWN, buff=0.2)
            fact_text.next_to(role_text, DOWN, buff=0.3)
            
            # Group everything
            card_group = VGroup(card.shadow, card, name_text, role_text, fact_text)
            card_group.move_to(UP * (1 - i * 2.5))
            member_cards.add(card_group)
        
        # Animate cards entering with stagger effect
        for i, card in enumerate(member_cards):
            card.save_state()
            card.move_to(UP * 3 + RIGHT * random.uniform(-2, 2))
            card.set_opacity(0)
            
        self.play(
            AnimationGroup(*[
                card.animate.restore().set_opacity(1)
                for card in member_cards
            ], lag_ratio=0.3),
            run_time=2.5
        )
        
        # ----------------------
        # 4. Interactive Member Highlights
        # ----------------------
        for i, card in enumerate(member_cards):
            # Highlight current card
            self.play(
                card.animate.scale(1.15).set_stroke(color=HIGHLIGHT_COLOR, width=4),
                *[other.animate.set_opacity(0.4) for j, other in enumerate(member_cards) if j != i],
                run_time=1
            )
            
            # Create orbiting particles around the highlighted card
            particles = VGroup()
            for angle in np.linspace(0, 2*PI, 12, endpoint=False):
                particle = Dot(
                    point=card.get_center(),
                    radius=0.04,
                    color=random.choice([PURE_PINK, ACCENT_BLUE, ACCENT_PURPLE]),
                    fill_opacity=0.8
                )
                particles.add(particle)
                
            # Animate particles in orbit
            self.play(
                AnimationGroup(*[
                    particle.animate.move_to(
                        card.get_center() + 1.2 * np.array([np.cos(angle), np.sin(angle), 0])
                    )
                    for particle, angle in zip(particles, np.linspace(0, 2*PI, 12, endpoint=False))
                ], lag_ratio=0.1),
                run_time=1.5
            )
            
            # Pulse effect for the fact text
            fact_box = SurroundingRectangle(card[4], color=ACCENT_PURPLE, buff=0.1, stroke_width=2)
            self.play(Create(fact_box), run_time=0.5)
            self.play(fact_box.animate.set_stroke(width=4), run_time=0.3)
            self.play(FadeOut(fact_box), run_time=0.5)
            
            # Return to normal state
            self.play(
                card.animate.scale(1/1.15).set_stroke(color=ACCENT_BLUE, width=3),
                *[other.animate.set_opacity(1) for j, other in enumerate(member_cards) if j != i],
                FadeOut(particles),
                run_time=1
            )
            
            self.wait(0.3)
        
                # 5. Team Collaboration Visualization (fixed)
        # ----------------------
        # Arrange cards in an arc manually
        n = len(member_cards)
        radius = 3
        angles = np.linspace(-PI/3, PI/3, n)  # spread cards over 120 degrees

        for card, angle in zip(member_cards, angles):
            target_pos = np.array([radius * np.cos(angle), radius * np.sin(angle), 0])
            self.play(card.animate.move_to(target_pos), run_time=1.5, rate_func=smooth)

        # Create connecting lines between team members
        connections = VGroup()
        center_point = ORIGIN

        for card in member_cards:
            connection = Line(
                center_point,
                card.get_center(),
                stroke_color=ACCENT_PURPLE,
                stroke_width=2.5
            )
            connections.add(connection)

        self.play(
            LaggedStart(*[Create(conn) for conn in connections], lag_ratio=0.3),
            run_time=2
        )
        
        # ----------------------
        # 6. Final Team Presentation
        # ----------------------
        team_circle = Circle(radius=3.5, color=ACCENT_BLUE, stroke_width=5, fill_opacity=0.1)
        team_text = Text("INNOVATION TEAM", font_size=42, color=ACCENT_BLUE, weight="BOLD")
        team_text.move_to(ORIGIN)
        
        self.play(
            FadeOut(connections),
            member_cards.animate.scale(0.8).move_to(ORIGIN),
            run_time=1.5
        )
        
        self.play(
            Create(team_circle),
            Write(team_text),
            run_time=1.5
        )
        
        # Rotate the entire team presentation
        self.play(
            Rotate(VGroup(team_circle, member_cards, team_text), PI/3),
            run_time=2,
            rate_func=smooth
        )
        
        # ----------------------
        # 7. Grand Finale
        # ----------------------
        finale_text = Text("Thank You!", font_size=78, color=HIGHLIGHT_COLOR, weight="BOLD")
        finale_subtext = Text("Team Innovators", font_size=36, color=ACCENT_BLUE)
        finale_subtext.next_to(finale_text, DOWN, buff=0.3)
        
        finale_group = VGroup(finale_text, finale_subtext)
        
        self.play(
            FadeOut(team_circle),
            FadeOut(team_text),
            member_cards.animate.scale(0.7).set_opacity(0.3).arrange(RIGHT, buff=1).move_to(DOWN * 1.5),
            run_time=1.5
        )
        
        self.play(
            Write(finale_text),
            Write(finale_subtext),
            run_time=1.5
        )
        
        # Final particle explosion effect
        final_particles = VGroup()
        for _ in range(60):
            particle = Dot(
                point=finale_text.get_center(),
                radius=random.uniform(0.03, 0.1),
                color=random.choice([PURE_PINK, ACCENT_BLUE, ACCENT_PURPLE]),
                fill_opacity=0.9
            )
            angle = random.uniform(0, 2*PI)
            distance = random.uniform(3, 6)
            target_pos = particle.get_center() + distance * np.array([np.cos(angle), np.sin(angle), 0])
            final_particles.add(particle)
            
            self.add(particle)
            self.play(
                particle.animate.move_to(target_pos).set_opacity(0),
                run_time=2,
                rate_func=smooth
            )
        
        # Hold the final frame
        self.wait(3)
        
        # Smooth exit
        self.play(
            FadeOut(finale_group),
            FadeOut(member_cards),
            FadeOut(final_particles),
            run_time=2
        )