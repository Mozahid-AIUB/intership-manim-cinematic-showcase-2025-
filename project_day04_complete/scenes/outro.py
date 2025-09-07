from manim import *

class Outro(Scene):
    def construct(self):
        thank_you = Text("Thank You for Watching!", font_size=48, color=YELLOW)
        self.play(GrowFromCenter(thank_you))
        self.wait(2)
        self.play(FadeOut(thank_you))
