from typing import Any, Dict

from dataclasses import dataclass

from matplotlib.patches import Rectangle
from matplotlib.text import Annotation
import matplotlib.colors as mpcolours


@dataclass
class Sample:
    name: str
    metadata: Dict[str, Any]


@dataclass
class LocRange:
    center: float
    width: float


@dataclass
class SampleLocation:
    sample: Sample
    x: LocRange
    y: LocRange


@dataclass
class BboxView:
    rect: Rectangle
    label: Annotation


@dataclass
class SampleViz:
    location: SampleLocation
    artists: BboxView | None = None

    def show_box(self, ax, callback=None):
        xy = (
            self.location.x.center - self.location.x.width / 2,
            self.location.y.center - self.location.y.width / 2,
        )
        self.artists = BboxView(
            Rectangle(
                xy,
                self.location.x.width,
                self.location.y.width,
                facecolor=mpcolours.to_rgba("r", 0.5),
                edgecolor="k",
            ),
            Annotation(
                self.location.sample.name,
                xy,
                xytext=(1, -1),
                va="top",
                textcoords="offset points",
                picker=True,
            ),
        )
        ax.add_patch(self.artists.rect)
        ax.add_artist(self.artists.label)

        def on_pick(event):
            if event.artist is self.artists.label:
                callback(self.location.sample)

        if callback:
            ax.figure.canvas.mpl_connect("pick_event", on_pick)
