from typing import Callable
from collections.abc import Sequence

from ophyd.signal import DerivedSignal, Signal
from ophyd import Device, Component as _Cpt


class GrandDerivedSignal(DerivedSignal):
    """
    A version of DerivedSignal That extracts from the grantparent class.
    """

    def __init__(self, derived_from, *, parent: Device, **kwargs):
        if isinstance(derived_from, str):
            derived_from = getattr(parent.parent, derived_from)
        return super().__init__(derived_from, parent=parent, **kwargs)


class CrystalChannel(GrandDerivedSignal):
    def __init__(self, derived_from, *, write_access=False, **kwargs):
        super().__init__(derived_from, write_access=write_access, **kwargs)

    def inverse(self, value: float) -> float:
        func = self.parent.parent._func
        offset = self.parent.offset.get()

        return func(value + offset)


class Crystal(Device):
    """
    A class to simulate a single analyzer crystal on the BAD detectors.
    """

    offset = _Cpt(Signal, kind="config")
    value = _Cpt(CrystalChannel, "angle", kind="hinted", lazy=True, name="")

    def __init__(self, *args, offset, **kwargs):
        super().__init__(*args, **kwargs)
        self.offset.set(offset)
        self.value.name = self.name


class DetectorBase(Device):
    angle = _Cpt(Signal, kind="hinted", value=0)

    def __init__(self, *args, func, **kwargs):
        self._func = func
        super().__init__(*args, **kwargs)


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
