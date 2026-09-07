import adsk.core, adsk.fusion, os
# The repo folder is the parent of this scripts folder. Fusion's Scripts panel defines __file__; when the script is
# executed as a string (e.g. through the Fusion MCP server) set it first: __file__ = '/path/to/repo/scripts/export.py'
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def run(_context: str):
    app = adsk.core.Application.get(); des = adsk.fusion.Design.cast(app.activeProduct); rc = des.rootComponent
    em = des.exportManager
    out = REPO
    for d in (os.path.join(out, 'stl'), os.path.join(out, 'step')): os.makedirs(d, exist_ok=True)
    print('f3d', em.execute(em.createFusionArchiveExportOptions(os.path.join(out, 'MiniMac.f3d'))))
    for i in range(rc.occurrences.count):
        oc = rc.occurrences.item(i); n = oc.component.name
        if n not in ('FacePlate', 'Body', 'FitGauge'): continue
        oc.isLightBulbOn = True                       # Fusion exports nothing for a hidden component
        for b in oc.bRepBodies: b.isLightBulbOn = True
        o = em.createSTLExportOptions(oc, os.path.join(out, 'stl', 'MiniMac_%s.stl' % n))
        o.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh; o.isBinaryFormat = True
        print('stl', n, em.execute(o))
        print('step', n, em.execute(em.createSTEPExportOptions(os.path.join(out, 'step', 'MiniMac_%s.step' % n), oc.component)))
