from manim import *
from scenes.sunshield import SunshieldPallets, SunshieldMidBoom, SunshieldTension
from scenes.mirrors import SecondaryDeploy, PrimaryWingDeploy
from scenes.l2_explainer import L2Scene


class MasterScene(Scene):
    def construct(self):
        """Run all deployment sub-scenes sequentially as a single cinematic."""
        scene_classes = [
            SunshieldPallets,
            SunshieldMidBoom,
            SunshieldTension,
            SecondaryDeploy,
            PrimaryWingDeploy,
            L2Scene,
        ]

        for cls in scene_classes:
            s = cls()
            # render each scene's construct in the current scene context
            s.construct()
