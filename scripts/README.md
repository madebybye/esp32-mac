Fusion 360 API scripts. Each defines `run(context)`; run them from Fusion's Scripts and Add-Ins panel (or through a
Fusion MCP server, in which case define `__file__` first so the scripts can find the repo folder).

1. `import_step.py` - imports `../reference/ESP32-S3-Touch-AMOLED-1.8-3D.stp` (Waveshare's board model) into an empty design.
2. `build.py` - rebuilds FacePlate, Body and FitGauge from the parameters at its top. Safe to re-run: it deletes the
   previous parts, re-places the board and rebuilds.
3. `checks.py` - interference and ray-cast checks. One interference is expected: the pocket is cut 0.4 mm shallower
   than the case, so the face plate holds the board on the pocket's floor rim.
4. `export.py` - writes `../MiniMac.f3d`, `../stl/MiniMac_<part>.stl` and `../step/MiniMac_<part>.step`.
