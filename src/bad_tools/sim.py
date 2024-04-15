from __future__ import annotations

from collections.abc import Callable, Sequence

import numpy as np
import numpy.typing
from ophyd import Component as _Cpt
from ophyd import Device
from ophyd.signal import DerivedSignal, Signal
from ophyd.sim import SynAxis, SynSignal


class GrandDerivedSignal(DerivedSignal):
    """
    A version of DerivedSignal That extracts from the grantparent class.
    """

    def __init__(self, derived_from, *, parent: Device, **kwargs):
        if isinstance(derived_from, str):
            derived_from = getattr(parent.parent, derived_from)
        super().__init__(derived_from, parent=parent, **kwargs)


class CrystalChannel(GrandDerivedSignal):
    def __init__(self, derived_from, *, write_access=False, **kwargs):
        super().__init__(derived_from, write_access=write_access, **kwargs)

    def inverse(self, value: float) -> float:
        func = self.parent.parent._func
        offset = self.parent.offset.get()
        missalign = np.abs(np.clip(self.parent.missalign.get(), -1, 1))

        return func(value + offset) * (1 - missalign)


class Crystal(Device):
    """
    A class to simulate a single analyzer crystal on the BAD detectors.
    """

    offset = _Cpt(Signal, kind="config")
    value = _Cpt(CrystalChannel, "angle", kind="hinted", lazy=True, name="")
    missalign = _Cpt(Signal, kind="config", value=0.5)

    def __init__(self, *args, offset, **kwargs):
        super().__init__(*args, **kwargs)
        self.offset.set(offset)
        self.value.name = self.name


class DetectorBase(Device):
    angle = _Cpt(Signal, kind="hinted", value=0)

    def __init__(self, *args, func, **kwargs):
        self._func = func
        super().__init__(*args, **kwargs)

    @property
    def channels(self):
        return [
            getattr(self, k)
            for k in sorted(self.component_names)
            if isinstance(getattr(self, k), Crystal)
        ]


def make_detector(
    angle_offsets: Sequence[float],
    func: Callable[[float], float],
    *,
    name: str = "det",
) -> Device:
    cls = type(
        "BADSimDetector",
        (DetectorBase,),
        {
            f"ch{n:02d}": _Cpt(Crystal, offset=offset)
            for n, offset in enumerate(angle_offsets)
        },
    )
    return cls(name=name, func=func)


def make_sample_rack(
    centers: np.typing.NDArray,
    heights: np.typing.NDArray,
) -> tuple[Device, Device, Device]:
    x_mtr = SynAxis(name="x")
    y_mtr = SynAxis(name="y")
    N = len(centers)
    locs = np.arange(1, N * 2 + 1, 2)
    tops = centers + (heights / 2.0)
    bottoms = centers - (heights / 2.0)

    def local():
        x = x_mtr.readback.get()
        y = y_mtr.readback.get()

        return np.sum(
            np.exp(-(((x - locs) / 0.5) ** 2) / 2) * (y < tops) * (y > bottoms)
        )

    signal = SynSignal(local, name="det_total")

    return x_mtr, y_mtr, signal
