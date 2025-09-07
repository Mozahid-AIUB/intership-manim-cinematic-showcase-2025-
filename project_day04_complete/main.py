from manim import *

class HelloWorld(Scene):
    def construct(self):
        text = Text("Hello, Manim!", font_size=72)
        self.play(Write(text))           # Animate writing the text
        self.wait(1)
        self.play(text.animate.to_edge(UP))   # Move text upward
        self.wait(1)
        square = Square().shift(DOWN)
        self.play(Create(square))        # Draw a square
        self.play(Rotate(square, PI/4))  # Rotate square
        self.wait(2)
