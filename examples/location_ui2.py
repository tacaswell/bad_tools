from __future__ import annotations

import bluesky.plans as bp
import numpy as np
from bluesky import RunEngine
from bluesky.callbacks.best_effort import BestEffortCallback

from bad_tools.sim import make_sample_rack

bec = BestEffortCallback()
bec.disable_table()

x, y, det = make_sample_rack(3 * np.random.randn(15) + 13, 5)

det.kind = "hinted"

RE = RunEngine()
RE.subscribe(bec)

RE(bp.grid_scan([det], y, 5, 20, 15, x, 1, 15, 200))
