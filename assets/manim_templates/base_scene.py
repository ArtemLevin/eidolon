from manim import *

class ExplainerScene(Scene):
    def construct(self):
        pass

def render_beat(scene: Scene, beat_title: str, visuals: list[str], seconds: float):
    title = Text(beat_title).to_edge(UP)
    scene.play(Write(title))
    scene.wait(seconds * 0.7)
    scene.play(FadeOut(title))
