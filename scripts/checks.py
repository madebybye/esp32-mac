import adsk.core, adsk.fusion, math
TILT = 6.0; S_T, C_T = math.sin(math.radians(TILT)), math.cos(math.radians(TILT))
def tilt_world(x, zl, d=0.0): return adsk.core.Point3D.create(x*0.1, (zl*S_T + d*C_T)*0.1, (zl*C_T - d*S_T)*0.1)
def ray_hits(rc, o, d):
    pts = adsk.core.ObjectCollection.create()
    hits = rc.findBRepUsingRay(o, d, adsk.fusion.BRepEntityTypes.BRepFaceEntityType, -1.0, True, pts)
    return [(hits.item(k).body.name, [round(v*10,2) for v in pts.item(k).asArray()]) for k in range(hits.count)]
def run(_context: str):
    app = adsk.core.Application.get(); des = adsk.fusion.Design.cast(app.activeProduct); rc = des.rootComponent
    bodies = {}
    for i in range(rc.occurrences.count):
        o = rc.occurrences.item(i)
        if o.component.name.startswith('Waveshare') or o.component.name.startswith('SlicerModifier') or o.component.name == 'FitGauge': continue
        for b in o.bRepBodies: bodies[o.component.name] = b
    c = adsk.core.ObjectCollection.create()
    for b in bodies.values(): c.add(b)
    res = des.analyzeInterference(des.createInterferenceInput(c))
    print('interference results:', res.count)
    for k in range(res.count):
        r = res.item(k)
        try: vol = round(r.interferenceBody.volume*1000, 3)
        except Exception: vol = None
        print('   ', r.entityOne.name, 'x', r.entityTwo.name, 'vol mm3', vol)
    print('    (one result is expected: DeviceCaseEnvelope x Body, ~97 mm3 where the device meets the pocket floor rim.\n     The pocket is cut 0.4 mm shallower than the case (POCKET_D) so the plate presses the device onto that rim.)')
    n_in = adsk.core.Vector3D.create(0, C_T, -S_T)
    print('ray @ window centre:', ray_hits(rc, tilt_world(0, 40.0, -10), n_in)[:4])
    print('ray @ channel (zl=14):', ray_hits(rc, tilt_world(0, 14.0, -10), n_in)[:4])
    print('ray @ BOOT (x=10, zl=20.7):', ray_hits(rc, tilt_world(10.0, 20.7, -10), n_in)[:3])
    env = [b for n, b in bodies.items() if n.startswith('Device case')][0]
    mm = app.measureManager
    for n, b in bodies.items():
        if b is env: continue
        print('min dist envelope->%s mm' % n, round(mm.measureMinimumDistance(env, b).value*10, 3), '| bbox', [round(v*10,1) for v in b.boundingBox.minPoint.asArray()], [round(v*10,1) for v in b.boundingBox.maxPoint.asArray()], 'vol', round(b.volume,2))
    app.activeViewport.fit(); app.activeViewport.refresh()
