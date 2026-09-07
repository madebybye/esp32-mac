"""ESP32 Mac: mini retro Mac enclosure for the Waveshare ESP32-S3-Touch-AMOLED-1.8.
Fusion API script (run via the Fusion MCP server or Fusion's Scripts panel) on a design that contains the
imported Waveshare STEP (see import_step.py). Rebuilds FacePlate, Body and FitGauge from the parameters below.
Body prints rear face down (screen side up); FacePlate face up; FitGauge flat.
"""
import adsk.core, adsk.fusion, math
CM = 0.1

# ---- shared parameters (mm) ----
W, H, D = 56.0, 64.0, 58.0
FRONT_D = 18.0; WALL = 2.0; Rbody = 2.5; Rface = 2.0; TILT = 6.0; ZC = 40.0
DEV_W, DEV_H, DEV_T = 45.2, 37.6, 15.0
DEV_R = 5.0; DEV_CX = -0.5
# measured on the first print (Sep 2026): 0.4 mm play across, 0.9 mm play up/down with a 45.8 x 38.2 pocket
DEV_W_MEAS, DEV_H_MEAS, DEV_R_MEAS = 44.9, 37.3, 6.4     # envelope drawn at the real case size
POCKET_W, POCKET_H, POCKET_R = 45.4, 37.7, 6.5          # pocket: 45.0x37.4 .. 45.3x37.7 printed tight, 45.5x37.9 was backed off; 0.25/0.2 mm per side
POCKET_D = DEV_T - 0.4                                  # pocket 0.4 shallower than the case: the plate presses the device onto the floor rim
PANEL_T = 3.5; RECESS_D = 2.0; FRAME = 2.0; SLOPE = 3.0
WIN_TRIM_X = 0.5                                              # v3 window: sampled screen outline, narrowed by this in X
BASE_H = 9.0
SLOT_W, SLOT_H, SLOT_X, SLOT_Z = 22.0, 1.6, 10.0, 12.0
VENT_N, VENT_PITCH, VENT_L, VENT_W = 10, 3.0, 14.0, 1.4   # slots run front-to-back (print as simple notches, no bridging)
VENT_YC = 41.0                               # world Y of the slot band's centre on the top surface
VENT_X = [(i - (VENT_N - 1)/2)*VENT_PITCH for i in range(VENT_N)]
CH_D, CH_H, CH_R = 8.0, 8.0, 1.5             # rear-top chamfer: equal run and rise = 45 deg, so it prints rear-down without
                                             # support. It starts at Y = D - CH_D, which must stay behind the vent slots
                                             # (they end at VENT_YC + VENT_L/2 = 48) and the duct's rear ceiling.
PIN_HOLE_D, PIN_DEPTH_PLATE, PIN_DEPTH_BODY = 3.0, 2.5, 4.0   # press-fit printed pins (holes) between plate and body
PIN_DIA, PIN_H = 2.85, 2.4                                    # pins integrated on the front frame's face
PIN_POS = [(DEV_CX - 25.0, 40.0), (DEV_CX + 25.0, 40.0), (-20.0, 61.7), (20.0, 61.7), (-20.0, 8.0), (20.0, 8.0)]   # 6 pins
TUNNEL_W, TUNNEL_Z0, TUNNEL_Z1 = 16.0, -7.0, 0.0   # cable passage through the foot: 16 wide, floor Z -7, ceiling level with the foot's top (Z 0)
TUNNEL_R = 2.0                               # corner radius of the cable slot, runs up the chute walls and over the lip round too
                                             # (must be < CAV_Z0 - LIP_Z - 0.3 so the rounds can run out against the lip's step)
CHUTE_TOP_Z = 6.0                            # chute polygon's top (inside the cavity air)
CHUTE_WALL_T, CHUTE_FOOT_CH = 2.0, 1.5       # chute front wall: vertical, this far behind the foot's front face (= passage floor thickness); chamfer at its foot
LIP_Z, LEDGE_CH = 2.0, 2.0                   # lip in front of the chute: a 2 mm wall above the underside (same as the floor under the passage),
                                             # its top corner a 45-deg chamfer of this size down into the chute wall
CHUTE_UP_Z = 10.0                            # world Z where the chute's upper wall leaves the cavity's back wall (45 deg down from there)
FOOT_INSET_FRONT = 3.0                          # foot front, measured back from the body's bottom-front edge
CHAN_NARROW = 14.0                            # half-width of the plug/button cavity below the pocket
CAV_Z0 = 5.0                                 # plug cavity floor (along the tilted face) below the device
VENT_DEPTH = 6.0                             # vent slots cut down into the rising duct's ceiling
MOUTH_CH = 0.5                               # lead-in chamfer on the pocket mouth
FLOOR_RECESS, FLOOR_RIM = 1.0, 3.0           # pocket floor recess behind the device, rim it rests on
BTN_HOLE_D = 2.0                             # paperclip holes up through the foot to PWR / BOOT
TUNNEL_EXIT_CH = 0.6                         # chamfer on the cable passage exit (only 1 mm of foot above the passage)
DUCT_HX = (VENT_N - 1)*VENT_PITCH/2 + VENT_W/2   # duct exactly as wide as the whole slot band (14.2)
DUCT_Y1 = 48.0                               # how far back the duct runs
SOUND_ROUTES = ((1.0, 15.0), (-16.0, -12.0))   # X ranges of grooves in the pocket's top wall: the case's speaker holes (centre ~X+8) and mic hole
SOUND_ROUTE_D, SOUND_ROUTE_BACK = 2.0, 5.5    # (~X-14) are on the device's top edge (label icons on the back); groove depth, and how far past the floor it runs
DUCT_FLOOR_Z, DUCT_CEIL_Z = (48.0, 55.5), (57.0, 62.0)   # duct floor / ceiling heights at the pocket floor and at the back: it rises
FEET_D, FEET_DEPTH = 8.0, 1.0
FEET_POS = [(-18.0, 12.0), (18.0, 12.0), (-18.0, 48.0), (18.0, 48.0)]
PIN_TIP_CH = 0.3
GAUGE_T, GAUGE_OFFSET_X = 6.0, 95.0
ENV_OPACITY = 0.9
DEV_T0 = {'SPEC': (-0.043, 0.052, 0.0)}
DEV_PLACE_T = (-0.0505, 0.35, 4.0)

S_T, C_T = math.sin(math.radians(TILT)), math.cos(math.radians(TILT))
NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation

def V(mm): return adsk.core.ValueInput.createByReal(mm*CM)
def P2(x, z): return adsk.core.Point3D.create(x*CM, -z*CM, 0)
def PXY(x, y): return adsk.core.Point3D.create(x*CM, y*CM, 0)
def tilt_world(x, zl, d=0.0):
    return adsk.core.Point3D.create(x*CM, (zl*S_T + d*C_T)*CM, (zl*C_T - d*S_T)*CM)

def rounded_rect(sk, cx, cy, w, h, r, pt=P2):
    lines = sk.sketchCurves.sketchLines; arcs = sk.sketchCurves.sketchArcs
    x0, x1 = cx - w/2, cx + w/2; y0, y1 = cy - h/2, cy + h/2
    r = min(r, w/2, h/2) if r > 0 else 0
    if r <= 1e-6:
        lines.addTwoPointRectangle(pt(x0, y0), pt(x1, y1)); return
    s = math.sqrt(0.5)
    for a, b in [((x0+r, y0), (x1-r, y0)), ((x1, y0+r), (x1, y1-r)), ((x1-r, y1), (x0+r, y1)), ((x0, y1-r), (x0, y0+r))]:
        if math.hypot(b[0]-a[0], b[1]-a[1]) > 1e-4: lines.addByTwoPoints(pt(*a), pt(*b))
    for c, a, b, d in [((x1-r, y0+r), (x1-r, y0), (x1, y0+r), (s, -s)), ((x1-r, y1-r), (x1, y1-r), (x1-r, y1), (s, s)),
                       ((x0+r, y1-r), (x0+r, y1), (x0, y1-r), (-s, s)), ((x0+r, y0+r), (x0, y0+r), (x0+r, y0), (-s, -s))]:
        arcs.addByThreePoints(pt(*a), pt(c[0] + r*d[0], c[1] + r*d[1]), pt(*b))

def polygon(sk, pts, pt):
    for k in range(len(pts)):
        a, b = pts[k], pts[(k + 1) % len(pts)]
        sk.sketchCurves.sketchLines.addByTwoPoints(pt(*a), pt(*b))

def circle(sk, cx, cy, dia, pt=P2):
    sk.sketchCurves.sketchCircles.addByCenterRadius(pt(cx, cy), dia/2*CM)

def profiles(sk, pick='all'):
    profs = [sk.profiles.item(i) for i in range(sk.profiles.count)]
    if pick == 'all':
        c = adsk.core.ObjectCollection.create()
        for p in profs: c.add(p)
        return c
    profs.sort(key=lambda p: p.areaProperties().area)
    return profs[0] if pick == 'min' else profs[-1]

def extrude(comp, prof, start, dist, op, taper_deg=0.0, participants=None, sign=1):
    ext = comp.features.extrudeFeatures
    ei = ext.createInput(prof, op)
    direction = adsk.fusion.ExtentDirections.PositiveExtentDirection if sign > 0 else adsk.fusion.ExtentDirections.NegativeExtentDirection
    ext_def = adsk.fusion.DistanceExtentDefinition.create(V(dist))
    if taper_deg: ei.setOneSideExtent(ext_def, direction, adsk.core.ValueInput.createByReal(math.radians(taper_deg)))
    else: ei.setOneSideExtent(ext_def, direction)
    ei.startExtent = adsk.fusion.OffsetStartDefinition.create(V(sign*start))
    if participants: ei.participantBodies = participants
    return ext.add(ei)

def extrude_sym(comp, prof, half, op, participants=None):
    ext = comp.features.extrudeFeatures
    ei = ext.createInput(prof, op)
    ei.setSymmetricExtent(V(half), False)
    if participants: ei.participantBodies = participants
    return ext.add(ei)

def yz_sketch(comp):
    sk = comp.sketches.add(comp.yZConstructionPlane)
    return sk, (lambda y, z: sk.modelToSketchSpace(adsk.core.Point3D.create(0, y*CM, z*CM)))

def coll(items):
    c = adsk.core.ObjectCollection.create()
    for i in items: c.add(i)
    return c

def fillet(comp, edges, r, chain=True):
    fil = comp.features.filletFeatures; fi = fil.createInput()
    try: fi.edgeSetInputs.addConstantRadiusEdgeSet(coll(edges), V(r), chain)
    except Exception: fi.addConstantRadiusEdgeSet(coll(edges), V(r), chain)
    return fil.add(fi)

def chamfer(comp, edges, d):
    ch = comp.features.chamferFeatures
    try:
        ci = ch.createInput2(); ci.chamferEdgeSets.addEqualDistanceChamferEdgeSet(coll(edges), V(d), True)
    except Exception:
        ci = ch.createInput(coll(edges), True); ci.setToEqualDistance(V(d))
    return ch.add(ci)

def outward_normal(f):
    ok, n = f.evaluator.getNormalAtPoint(f.pointOnFace); return n

def face_by_normal(body, nx, ny, nz, min_area_mm2=0, at=None, axis=None, tol=0.02):
    best = None
    for f in body.faces:
        if f.geometry.surfaceType != adsk.core.SurfaceTypes.PlaneSurfaceType: continue
        n = outward_normal(f)
        if abs(n.x-nx) < tol and abs(n.y-ny) < tol and abs(n.z-nz) < tol and f.area*100 >= min_area_mm2:
            if at is not None:
                mn, mx = bbox_mm(f)
                if abs(mn[axis] - at) > 0.05: continue
            if best is None or f.area > best.area: best = f
    return best

def edges_parallel(body, axis, pred=None):
    out = []
    for e in body.edges:
        g = e.geometry
        if g.curveType != adsk.core.Curve3DTypes.Line3DCurveType: continue
        d = g.startPoint.vectorTo(g.endPoint); d.normalize()
        if abs(abs(d.dotProduct(axis)) - 1) < 1e-3 and (pred is None or pred(e)): out.append(e)
    return out

def at_yz(y, z):
    def f(e):
        g = e.geometry
        return abs((g.startPoint.y+g.endPoint.y)/2*10 - y) < 0.05 and abs((g.startPoint.z+g.endPoint.z)/2*10 - z) < 0.05
    return f

def bbox_mm(b):
    bb = b.boundingBox
    return [round(v*10, 2) for v in bb.minPoint.asArray()], [round(v*10, 2) for v in bb.maxPoint.asArray()]

def new_component(rc, name):
    occ = rc.occurrences.addNewComponent(adsk.core.Matrix3D.create()); occ.component.name = name
    return occ, occ.component

def tilt_setup(comp):
    planes = comp.constructionPlanes; pl = None
    for sgn in (1, -1):
        pi = planes.createInput()
        pi.setByAngle(comp.xConstructionAxis, adsk.core.ValueInput.createByReal(math.radians(sgn*TILT)), comp.xZConstructionPlane)
        p = planes.add(pi); n = p.geometry.normal
        if abs(n.y*S_T + n.z*C_T) < 1e-3: pl = p; break
        p.deleteMe()
    if pl is None: raise RuntimeError('tilted plane failed')
    pl.name = 'FrontTilt'
    sk = comp.sketches.add(pl); pt = lambda x, zl: sk.modelToSketchSpace(tilt_world(x, zl))
    sk.sketchCurves.sketchLines.addTwoPointRectangle(pt(-1, 1), pt(1, 3))
    e = extrude(comp, profiles(sk, 'max'), 0, 2, NEW, sign=1)
    sign = 1 if e.bodies.item(0).boundingBox.maxPoint.y*10 > 1.0 else -1
    e.deleteMe(); sk.deleteMe()
    return pl, sign

def tsk(comp, pl):
    sk = comp.sketches.add(pl)
    return sk, (lambda x, zl: sk.modelToSketchSpace(tilt_world(x, zl)))

def rear_plane(comp, y):
    planes = comp.constructionPlanes
    for sgn in (1, -1):
        pi = planes.createInput(); pi.setByOffset(comp.xZConstructionPlane, V(sgn*y))
        p = planes.add(pi); sk = comp.sketches.add(p); oy = sk.origin.y*10; sk.deleteMe()
        if abs(oy - y) < 0.01: return p
        p.deleteMe()
    raise RuntimeError('offset plane failed')

def front_loft(c, pl):
    """Loft: tilted front rounded-rect (d=0) -> vertical rounded-rect at Y=FRONT_D. Returns body."""
    Hf = H / C_T
    skf, ptf = tsk(c, pl); rounded_rect(skf, 0, Hf/2, W, Hf, Rbody, ptf)
    skr = c.sketches.add(rear_plane(c, FRONT_D))
    ptr = lambda x, z: skr.modelToSketchSpace(adsk.core.Point3D.create(x*CM, FRONT_D*CM, z*CM))
    rounded_rect(skr, 0, H/2, W, H, Rbody, ptr)
    li = c.features.loftFeatures.createInput(NEW)
    li.loftSections.add(profiles(skf, 'max')); li.loftSections.add(profiles(skr, 'max')); li.isSolid = True
    return c.features.loftFeatures.add(li).bodies.item(0)

def device_occ(rc):
    for i in range(rc.occurrences.count):
        o = rc.occurrences.item(i)
        if o.component.name.startswith('Waveshare') or o.name.startswith('ESP32-S3-TOUCH'): return o
    raise RuntimeError('device occurrence not found')

def place_device(rc, des):
    top = device_occ(rc); top.component.name = 'Waveshare ESP32-S3-Touch-AMOLED-1.8 (PCBA+display)'
    R = [[1,0,0,0],[0,C_T,S_T,0],[0,-S_T,C_T,0],[0,0,0,1]]
    for k in range(top.childOccurrences.count):
        o = top.childOccurrences.item(k)
        for attr in ('isGrounded', 'isGroundToParent'):
            try:
                if getattr(o, attr): setattr(o, attr, False)
            except Exception: pass
        t0 = DEV_T0.get('SPEC') if o.name.startswith('SPEC') else (0.0, 0.0, 0.0)
        Rt0 = (t0[1], -t0[2], -t0[0])
        T = [[0,1,0,DEV_PLACE_T[0]+Rt0[0]], [0,0,-1,DEV_PLACE_T[1]+Rt0[1]], [-1,0,0,DEV_PLACE_T[2]+Rt0[2]], [0,0,0,1]]
        Mn = [[sum(R[r][i]*T[i][cc] for i in range(4)) for cc in range(4)] for r in range(4)]
        m = adsk.core.Matrix3D.create(); m.setWithArray([Mn[r][cc] for r in range(4) for cc in range(4)]); o.transform = m
    if des.snapshots.hasPendingSnapshot: des.snapshots.add()
    print('device placed (upright + %.0f deg tilt)' % TILT)

def build_envelope(rc):
    occ, c = new_component(rc, 'Device case envelope 37.6x45.2x15')
    pl, sg = tilt_setup(c); sk, pt = tsk(c, pl)
    rounded_rect(sk, DEV_CX, ZC, DEV_W_MEAS, DEV_H_MEAS, DEV_R_MEAS, pt)
    b = extrude(c, profiles(sk, 'max'), PANEL_T, DEV_T, NEW, sign=sg).bodies.item(0); b.name = 'DeviceCaseEnvelope'
    return b

def active_face(rc):
    top = device_occ(rc)
    disp = [top.childOccurrences.item(k) for k in range(top.childOccurrences.count) if top.childOccurrences.item(k).name.startswith('SPEC-')][0]
    body = disp.bRepBodies.item(0); best = None
    for f in body.faces:
        if f.geometry.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType and 900 < f.area*100 < 1100:
            if best is None or f.area > best.area: best = f
    return best

def active_outline_sketch(c, pl, rc, samples=16, trim_x=0.0):
    """Sketch on the tilted plane containing the display's active-area outline, drawn from sampled edge points
    with exact shared endpoints (a direct projection leaves micron gaps and no closed profile)."""
    act = active_face(rc)
    ces = act.loops.item(0).coEdges
    sk = c.sketches.add(pl)
    chain = []
    for k in range(ces.count):
        ce = ces.item(k); e = ce.edge; ev = e.evaluator
        is_spline = e.geometry.curveType != adsk.core.Curve3DTypes.Line3DCurveType
        ok, t0, t1 = ev.getParameterExtents()
        n = samples if is_spline else 2
        ok, mpts = ev.getPointsAtParameters([t0 + (t1 - t0)*q/(n - 1) for q in range(n)])
        mpts = list(mpts)
        if ce.isOpposedToEdge: mpts.reverse()
        spts = []
        for mp in mpts:
            sp = sk.modelToSketchSpace(mp); spts.append(adsk.core.Point3D.create(sp.x, sp.y, 0))
        chain.append((is_spline, spts))
    if trim_x > 1e-6:   # move each side inward by half the trim (points left of centre go right, right go left)
        xs = [q.x for _, spts in chain for q in spts]; cx = (min(xs) + max(xs))/2; h = trim_x/2*CM
        for _, spts in chain:
            for q in spts: q.x = q.x - h if q.x > cx else q.x + h
    for k in range(len(chain)):
        prev = chain[k - 1][1]; chain[k][1][0] = adsk.core.Point3D.create(prev[-1].x, prev[-1].y, 0)
    curves = []
    for is_spline, spts in chain:
        if is_spline:
            oc = adsk.core.ObjectCollection.create()
            for q in spts: oc.add(q)
            curves.append(sk.sketchCurves.sketchFittedSplines.add(oc))
        else:
            curves.append(sk.sketchCurves.sketchLines.addByTwoPoints(spts[0], spts[-1]))
    return sk, curves

def cut_face_features_projected(c, pl, sg, blk, rc):
    """Window = the display's active-area outline; recess = that outline offset outward by FRAME+SLOPE."""
    sk, curves = active_outline_sketch(c, pl, rc, trim_x=WIN_TRIM_X)
    far = sk.modelToSketchSpace(tilt_world(0, ZC + 60.0))
    sk.offset(coll(curves), adsk.core.Point3D.create(far.x, far.y, 0), (FRAME + SLOPE)*CM)
    for cv in curves: cv.isConstruction = True
    print('recess sketch profiles', sk.profiles.count, 'area mm2', round(profiles(sk, 'max').areaProperties().area*100, 1))
    extrude(c, profiles(sk, 'max'), 0, RECESS_D, CUT, taper_deg=-math.degrees(math.atan2(SLOPE, RECESS_D)), participants=[blk], sign=sg)
    sk, curves = active_outline_sketch(c, pl, rc, trim_x=WIN_TRIM_X)
    print('window sketch profiles', sk.profiles.count, 'area mm2', round(profiles(sk, 'max').areaProperties().area*100, 1), '(active area 985.7)')
    extrude(c, profiles(sk, 'max'), 0, PANEL_T + 1.0, CUT, participants=[blk], sign=sg)
    sk, pt = tsk(c, pl); rounded_rect(sk, SLOT_X, SLOT_Z, SLOT_W, SLOT_H, SLOT_H/2, pt)
    extrude(c, profiles(sk, 'max'), 0, 1.5, CUT, participants=[blk], sign=sg)

def big_rect(sk, pt): rounded_rect(sk, 0, 40.0, 90.0, 130.0, 0, pt)

def cut_pin_holes(c, pl, sg, body, start, depth):
    sk, pt = tsk(c, pl)
    for (px, pz) in PIN_POS: circle(sk, px, pz, PIN_HOLE_D, pt)
    extrude(c, profiles(sk, 'all'), start, depth, CUT, participants=[body], sign=sg)

def build_faceplate(rc):
    occ, c = new_component(rc, 'FacePlate')
    pl, sg = tilt_setup(c)
    plate = front_loft(c, pl); plate.name = 'FacePlate'
    ff = face_by_normal(plate, 0, -C_T, S_T)
    fillet(c, [ff.edges.item(i) for i in range(ff.edges.count)], Rface)
    sk, pt = tsk(c, pl); big_rect(sk, pt)
    extrude(c, profiles(sk, 'max'), PANEL_T, 40.0, CUT, participants=[plate], sign=sg)
    cut_face_features_projected(c, pl, sg, plate, rc)
    cut_pin_holes(c, pl, sg, plate, PANEL_T - PIN_DEPTH_PLATE, PIN_DEPTH_PLATE + 0.5)
    print('FacePlate', bbox_mm(plate), 'faces', plate.faces.count, 'vol', round(plate.volume, 2))
    return plate

def switch_positions(rc):
    """World (X, Y) centres of the two side switches (PWR, BOOT) from the imported model."""
    top = device_occ(rc); out = []
    def walk(o):
        for k in range(o.childOccurrences.count):
            ch = o.childOccurrences.item(k)
            if ch.name.startswith('SWITCH'):
                bb = ch.boundingBox
                out.append(((bb.minPoint.x + bb.maxPoint.x)/2*10, (bb.minPoint.y + bb.maxPoint.y)/2*10))
            walk(ch)
    walk(top)
    return out

def build_body(rc):
    """One solid block (body + foot). Prints rear face down, screen side up, infill does the hollowing."""
    occ, c = new_component(rc, 'Body')
    pl, sg = tilt_setup(c)
    frame = front_loft(c, pl)
    sk = c.sketches.add(c.xZConstructionPlane); rounded_rect(sk, 0, H/2, W, H, Rbody)
    rear = extrude(c, profiles(sk, 'max'), FRONT_D, D - FRONT_D, NEW).bodies.item(0)
    foot_y0 = PANEL_T*C_T + FOOT_INSET_FRONT           # body's bottom-front edge is at Y = PANEL_T*cos(tilt)
    bw, bd = W - 6.0, D - foot_y0                       # foot runs flush to the body's rear face: the whole back prints on the bed
    sk = c.sketches.add(c.xYConstructionPlane); rounded_rect(sk, 0, foot_y0 + (bd + 4.0)/2, bw, bd + 4.0, 2.0, PXY)
    foot = extrude(c, profiles(sk, 'max'), -BASE_H, BASE_H + 0.1, NEW).bodies.item(0)
    sk = c.sketches.add(c.xYConstructionPlane); rounded_rect(sk, 0, D + 5.0, W + 10.0, 10.0, 0, PXY)   # square off the rear corners at Y = D
    extrude(c, profiles(sk, 'max'), -BASE_H - 1.0, BASE_H + 2.0, CUT, participants=[foot])
    ci = c.features.combineFeatures.createInput(rear, coll([frame, foot]))
    ci.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation; ci.isKeepToolBodies = False
    c.features.combineFeatures.add(ci)
    assert c.bRepBodies.count == 1, 'combine left %d bodies' % c.bRepBodies.count
    body = c.bRepBodies.item(0); body.name = 'Body'
    # rear-top chamfer wedge + R1.5 edges, foot bottom chamfer
    sk, pt = yz_sketch(c)
    p1 = (D - CH_D, H); p2 = (D, H - CH_H)
    p0 = (p1[0] - 0.2*CH_D, p1[1] + 0.2*CH_H); p3 = (p2[0] + 0.15*CH_D, p2[1] - 0.15*CH_H)
    polygon(sk, [p0, p3, (D + 4.0, p3[1]), (D + 4.0, H + 6.0), (p0[0], H + 6.0)], pt)
    extrude_sym(c, profiles(sk, 'max'), W, CUT, participants=[body])
    ax = adsk.core.Vector3D.create(1, 0, 0)
    es_top = edges_parallel(body, ax, at_yz(D - CH_D, H))
    rf = face_by_normal(body, 0, 1, 0); rf_edges = [rf.edges.item(i) for i in range(rf.edges.count)]   # body + foot: one face
    body_only = [e for e in rf_edges if bbox_mm(e)[0][2] > -0.01 and e.length*10 > 1.0]   # without the foot edges / 0.5 mm steps
    done = None
    for label, edges in (('all rear-face edges', rf_edges), ('body rear edges only', body_only)):
        try:
            fil = c.features.filletFeatures; fi = fil.createInput()
            fi.edgeSetInputs.addConstantRadiusEdgeSet(coll(es_top), V(CH_R), True)
            fi.edgeSetInputs.addConstantRadiusEdgeSet(coll(edges), V(CH_R), False)
            fil.add(fi); done = label; break
        except Exception as ex: print('rear fillet (%s) failed: %s' % (label, str(ex).splitlines()[0]))
    if done is None: fillet(c, es_top, CH_R, True); done = 'chamfer chain only'
    print('rear fillet:', done)
    bf = face_by_normal(body, 0, 0, -1, at=-BASE_H, axis=2)
    bf_edges = [bf.edges.item(i) for i in range(bf.edges.count)]
    if done == 'all rear-face edges': bf_edges = [e for e in bf_edges if bbox_mm(e)[0][1] < D - CH_R - 0.1]   # rear edge is already the R1.5 round
    try: chamfer(c, bf_edges, 1.0); print('foot bottom chamfer on %d edges' % len(bf_edges))
    except Exception as ex:
        print('foot bottom chamfer failed:', str(ex).splitlines()[0])
        front_only = [e for e in bf_edges if bbox_mm(e)[1][1] < foot_y0 + 2.5]
        try: chamfer(c, front_only, 1.0); print('foot bottom chamfer: front edge only')
        except Exception as ex2: print('foot bottom chamfer skipped:', str(ex2).splitlines()[0])
    # trim the front to the plate's back plane (body region only)
    sk, pt = tsk(c, pl); rounded_rect(sk, 0, 65.0, 90.0, 130.0, 0, pt)
    extrude(c, profiles(sk, 'max'), -20.0, 20.0 + PANEL_T, CUT, participants=[body], sign=sg)
    # device pocket, flush: exactly the case depth; lead-in chamfer on its mouth
    z_bot, z_top = ZC - POCKET_H/2, ZC + POCKET_H/2
    sk, pt = tsk(c, pl); rounded_rect(sk, DEV_CX, ZC, POCKET_W, POCKET_H, POCKET_R, pt)
    extrude(c, profiles(sk, 'max'), PANEL_T, POCKET_D, CUT, participants=[body], sign=sg)
    sk, pt = tsk(c, pl); rounded_rect(sk, DEV_CX, ZC, POCKET_W + 2*MOUTH_CH, POCKET_H + 2*MOUTH_CH, POCKET_R + MOUTH_CH, pt)
    extrude(c, profiles(sk, 'max'), PANEL_T, MOUTH_CH, CUT, taper_deg=-45.0, participants=[body], sign=sg)
    # floor recess behind the device (uniform 3 mm rim, corners concentric with the pocket), joined down to the plug cavity
    rz0 = z_bot + FLOOR_RIM
    sk, pt = tsk(c, pl)
    rounded_rect(sk, DEV_CX, ZC, POCKET_W - 2*FLOOR_RIM, POCKET_H - 2*FLOOR_RIM, max(0.5, POCKET_R - FLOOR_RIM), pt)
    rounded_rect(sk, 0, (z_bot - 1.5 + rz0 + 1.0)/2, 2*CHAN_NARROW, rz0 + 1.0 - (z_bot - 1.5), 0, pt)
    extrude(c, profiles(sk, 'all'), PANEL_T + POCKET_D - 0.1, FLOOR_RECESS + 0.1, CUT, participants=[body], sign=sg)
    # plug / button cavity below the device; its back wall is coplanar with the floor recess (no step)
    sk, pt = tsk(c, pl); rounded_rect(sk, 0, (CAV_Z0 + z_bot + 0.5)/2, 2*CHAN_NARROW, z_bot + 0.5 - CAV_Z0, 0, pt)
    extrude(c, profiles(sk, 'max'), PANEL_T, POCKET_D + FLOOR_RECESS, CUT, participants=[body], sign=sg)
    # cable: one chamfered chute from the cavity floor into a square passage through the foot (all 45 deg or
    # axis-aligned faces, so it prints support-free rear-down), exiting the foot's rear face with a chamfer
    sk, pt = yz_sketch(c)
    d_cav = PANEL_T + POCKET_D + FLOOR_RECESS            # cavity rear wall depth (= recess floor)
    yc, zc = CAV_Z0*S_T + d_cav*C_T, CAV_Z0*C_T - d_cav*S_T   # cavity rear-bottom corner (world Y, Z)
    zl_up = (CHUTE_UP_Z + d_cav*S_T)/C_T                 # point on the cavity's back wall at world Z = CHUTE_UP_Z
    y_up = zl_up*S_T + d_cav*C_T
    y_wall = foot_y0 + CHUTE_WALL_T                      # front wall: vertical, parallel to the foot's front face, 3 mm behind it
    du = CHUTE_UP_Z - TUNNEL_Z1                          # upper wall: 45 deg from the back wall down to the passage ceiling
    ch = CHUTE_FOOT_CH
    z_lip = LIP_Z                                        # lip top (the cavity floor above it stays at CAV_Z0 beside the chute)
    lc = LEDGE_CH                                        # lip's top corner: 45-deg chamfer down into the front wall
    polygon(sk, [(0.0, CHUTE_TOP_Z), (0.0, z_lip), (y_wall - lc, z_lip), (y_wall, z_lip - lc), (y_wall, TUNNEL_Z0 + ch),
                 (y_wall + ch, TUNNEL_Z0), (D + 2.0, TUNNEL_Z0), (D + 2.0, TUNNEL_Z1), (y_up + du, TUNNEL_Z1), (y_up, CHUTE_UP_Z)], pt)
    extrude_sym(c, profiles(sk, 'max'), TUNNEL_W/2, CUT, participants=[body])
    print('lip: top Z %.2f, 45-deg chamfer %.1f into the wall at Y %.2f' % (z_lip, lc, y_wall))
    # round the slot's corners: the concave edges where the floor / ceiling / 45-deg walls meet the side walls
    def slot_corner_edges(passage_only=False):
        out = []
        for e in body.edges:
            ct = e.geometry.curveType
            p0, p1 = e.startVertex.geometry, e.endVertex.geometry
            if abs(abs(p0.x*10) - TUNNEL_W/2) > 0.01 or abs(p0.x - p1.x)*10 > 0.01: continue   # lies in a side wall
            if min(p0.z, p1.z)*10 < TUNNEL_Z0 - 0.01 or max(p0.z, p1.z)*10 > CHUTE_UP_Z + 0.01: continue
            if ct == adsk.core.Curve3DTypes.Arc3DCurveType:                  # the lip round's side edges
                if not passage_only and max(p0.y, p1.y)*10 < D - 0.5: out.append(e)
                continue
            if ct != adsk.core.Curve3DTypes.Line3DCurveType: continue
            dy, dz = abs(p1.y - p0.y)*10, abs(p1.z - p0.z)*10
            horizontal = dz < 0.01 and dy > 1.0
            diagonal = abs(dy - dz) < 0.05 and dy > 1.0
            vertical = dy < 0.01 and dz > 1.0 and max(p0.y, p1.y)*10 < D - 0.5   # the front wall's side edges, not the exit's
            if horizontal or ((diagonal or vertical) and not passage_only): out.append(e)
        return out
    if TUNNEL_R > 0:
        for label, edges in (('chute + passage', slot_corner_edges()), ('passage only', slot_corner_edges(True))):
            try: fillet(c, edges, TUNNEL_R, False); print('cable slot corner radius %.1f on %d edges (%s)' % (TUNNEL_R, len(edges), label)); break
            except Exception as ex: print('cable slot fillet (%s) failed: %s' % (label, str(ex).splitlines()[0]))
    print('chute: front wall at Y %.1f (foot front %.1f), upper wall leaves the cavity back wall at (Y %.1f, Z %.1f), cavity corner (Y %.1f, Z %.1f)' % (y_wall, foot_y0, y_up, CHUTE_UP_Z, yc, zc))
    ff = face_by_normal(body, 0, 1, 0, at=foot_y0 + bd, axis=1)
    loop = [ff.loops.item(k) for k in range(ff.loops.count) if not ff.loops.item(k).isOuter] if ff else []
    if loop:
        for ch_size in (TUNNEL_EXIT_CH, 0.4):
            try: chamfer(c, [loop[0].edges.item(k) for k in range(loop[0].edges.count)], ch_size); print('exit chamfer', ch_size); break
            except Exception as ex: print('exit chamfer', ch_size, 'failed:', str(ex).splitlines()[0])
    else: print('foot exit loop not found')
    # air duct: opens flush in the pocket floor and rises towards the back so warm air convects up to the vents
    def y_floor(z):   # world Y of the pocket floor plane (d = PANEL_T + POCKET_D) at world height z
        zl = (z + (PANEL_T + POCKET_D)*S_T)/C_T
        return zl*S_T + (PANEL_T + POCKET_D)*C_T
    sk, pt = yz_sketch(c)
    polygon(sk, [(y_floor(DUCT_FLOOR_Z[0]) - 0.1, DUCT_FLOOR_Z[0]), (DUCT_Y1, DUCT_FLOOR_Z[1]),
                 (DUCT_Y1, DUCT_CEIL_Z[1]), (y_floor(DUCT_CEIL_Z[0]) - 0.1, DUCT_CEIL_Z[0])], pt)
    extrude_sym(c, profiles(sk, 'max'), DUCT_HX, CUT, participants=[body])
    # sound route: the case's speaker and mic holes sit on the device's top edge, against the pocket's top wall.
    # Grooves in that wall run from the plate's back past the pocket floor into the duct, so sound leaves via the vents.
    z_top = ZC + POCKET_H/2
    sk, pt = tsk(c, pl)
    for (x0, x1) in SOUND_ROUTES: rounded_rect(sk, (x0 + x1)/2, z_top + SOUND_ROUTE_D/2 - 0.05, x1 - x0, SOUND_ROUTE_D + 0.1, 0, pt)
    extrude(c, profiles(sk, 'all'), PANEL_T, POCKET_D + SOUND_ROUTE_BACK, CUT, participants=[body], sign=sg)
    sk = c.sketches.add(c.xYConstructionPlane)
    for xc in VENT_X: rounded_rect(sk, xc, VENT_YC, VENT_W, VENT_L, VENT_W/2, PXY)
    extrude(c, profiles(sk, 'all'), H - VENT_DEPTH, VENT_DEPTH + 1.0, CUT, participants=[body])
    # paperclip holes up through the foot to PWR and BOOT, rubber-feet dimples, foot side grooves
    sk = c.sketches.add(c.xYConstructionPlane)
    for (bx, by) in switch_positions(rc): circle(sk, bx, by, BTN_HOLE_D, PXY)
    extrude(c, profiles(sk, 'all'), -BASE_H - 1.0, BASE_H + 1.0 + 4.5, CUT, participants=[body])
    sk = c.sketches.add(c.xYConstructionPlane)
    for (fx, fy) in FEET_POS: circle(sk, fx, fy, FEET_D, PXY)
    extrude(c, profiles(sk, 'all'), -BASE_H - 1.0, 1.0 + FEET_DEPTH, CUT, participants=[body])
    sk = c.sketches.add(c.xZConstructionPlane)
    for zc in (-7.2, -5.7, -4.2, -2.7):
        rounded_rect(sk,  bw/2 + 1.0, zc, 8.0, 0.9, 0); rounded_rect(sk, -bw/2 - 1.0, zc, 8.0, 0.9, 0)
    extrude(c, profiles(sk, 'all'), 23.0, 14.0, CUT, participants=[body])
    # integrated alignment pins, tips chamfered
    sk, pt = tsk(c, pl)
    for (px, pz) in PIN_POS: circle(sk, px, pz, PIN_DIA, pt)
    extrude(c, profiles(sk, 'all'), PANEL_T - PIN_H, PIN_H + 0.1, JOIN, participants=[body], sign=sg)
    tips = [f for f in body.faces if f.geometry.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType
            and 5.0 < f.area*100 < 8.0 and outward_normal(f).y < -0.9]
    if tips: chamfer(c, [f.edges.item(0) for f in tips], PIN_TIP_CH)
    print('pin tips chamfered:', len(tips))
    print('Body', bbox_mm(body), 'faces', body.faces.count, 'vol', round(body.volume, 2))
    return body

def build_gauge(rc):
    """Fit gauge: 6 mm slab with the pocket, the plug cavity and all six pins, to test fit before the long print."""
    occ, c = new_component(rc, 'FitGauge')
    m = adsk.core.Matrix3D.create(); m.translation = adsk.core.Vector3D.create(GAUGE_OFFSET_X*CM, 0, 0); occ.transform = m
    sk = c.sketches.add(c.xZConstructionPlane); rounded_rect(sk, 0, H/2, W, H, Rbody)
    g = extrude(c, profiles(sk, 'max'), 0.0, GAUGE_T, NEW).bodies.item(0); g.name = 'FitGauge'
    z_bot = ZC - POCKET_H/2
    sk = c.sketches.add(c.xZConstructionPlane)
    rounded_rect(sk, DEV_CX, ZC, POCKET_W, POCKET_H, POCKET_R)
    rounded_rect(sk, 0, (CAV_Z0 + z_bot + 0.5)/2, 2*CHAN_NARROW, z_bot + 0.5 - CAV_Z0, 0)
    extrude(c, profiles(sk, 'all'), -1.0, GAUGE_T + 2.0, CUT, participants=[g])
    sk = c.sketches.add(c.xZConstructionPlane)
    for (px, pz) in PIN_POS: circle(sk, px, pz, PIN_DIA)
    extrude(c, profiles(sk, 'all'), 0.1, -(PIN_H + 0.1), JOIN, participants=[g])
    print('FitGauge', bbox_mm(g))
    return g

def apply_appearance(app, des, rc):
    lib = None
    for i in range(app.materialLibraries.count):
        L = app.materialLibraries.item(i)
        if 'Appearance' in L.name: lib = L; break
    names = [lib.appearances.item(i).name for i in range(lib.appearances.count)]
    def find(keys):
        for k in keys:
            for i, n in enumerate(names):
                if k.lower() in n.lower(): return lib.appearances.item(i)
    def design_copy(a, newname):
        for i in range(des.appearances.count):
            if des.appearances.item(i).name == newname: return des.appearances.item(i)
        return des.appearances.addByCopy(a, newname)
    beige = design_copy(find(['Paek (Beige)', 'Beige', 'Plastic - Matte']), 'MiniMac Platinum')
    for i in range(beige.appearanceProperties.count):
        pr = beige.appearanceProperties.item(i)
        if pr.objectType == adsk.core.ColorProperty.classType():
            try: pr.value = adsk.core.Color.create(222, 216, 200, 255); break
            except Exception: pass
    dark = find(['Plastic - Matte (Black)', 'Black'])
    for i in range(rc.occurrences.count):
        o = rc.occurrences.item(i)
        if o.component.name in PART_NAMES:
            for b in o.bRepBodies: b.appearance = beige
        elif o.component.name.startswith('Device case envelope'):
            for b in o.bRepBodies:
                b.appearance = dark
                try: b.opacity = ENV_OPACITY
                except Exception: pass

PART_NAMES = ('FacePlate', 'Body', 'FitGauge')
OLD_NAMES = ('FrontBezel', 'RearShell', 'Base', 'FrontFrame', 'RearPlate', 'Pins', 'SlicerModifier_PocketFloor')

def run(_context: str):
    app = adsk.core.Application.get(); des = adsk.fusion.Design.cast(app.activeProduct); rc = des.rootComponent
    doomed = [rc.occurrences.item(i) for i in range(rc.occurrences.count)
              if rc.occurrences.item(i).component.name in PART_NAMES + OLD_NAMES
              or rc.occurrences.item(i).component.name.startswith('Device case envelope')]
    for o in doomed: o.deleteMe()
    place_device(rc, des)
    build_envelope(rc)
    build_faceplate(rc); build_body(rc); build_gauge(rc)
    apply_appearance(app, des, rc)
    print('BUILD OK', [rc.occurrences.item(i).component.name for i in range(rc.occurrences.count)])
    app.activeViewport.fit(); app.activeViewport.refresh()
