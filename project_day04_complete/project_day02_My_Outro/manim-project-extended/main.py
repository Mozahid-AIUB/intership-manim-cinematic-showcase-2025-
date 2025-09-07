from manim import *
from scenes.intro import Intro
from scenes.main_content import MainContent
from scenes.outro import Outro


class FinalVideo(Scene):
    def construct(self):
        # Intro
        intro = Intro()
        intro.construct()
        self.add(*intro.mobjects)  # add intro elements

        self.wait(1)

        # Main Content
        main_content = MainContent()
        main_content.construct()
        self.add(*main_content.mobjects)  # add main content elements

        self.wait(1)

        # Outro
        outro = Outro()
        outro.construct()
        self.add(*outro.mobjects)  # add outro elements

        self.wait(1)
