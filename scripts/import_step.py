import adsk.core, adsk.fusion, time
import os
# The repo folder is the parent of this scripts folder. Fusion's Scripts panel defines __file__; when the script is
# executed as a string (e.g. through the Fusion MCP server) set it first: __file__ = '/path/to/repo/scripts/import_step.py'
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run(_context: str):
    app = adsk.core.Application.get()
    des = adsk.fusion.Design.cast(app.activeProduct)
    rc = des.rootComponent
    im = app.importManager
    t0 = time.time()
    opts = im.createSTEPImportOptions(os.path.join(REPO, 'reference', 'ESP32-S3-Touch-AMOLED-1.8-3D.stp'))
    opts.isViewFit = True
    ok = im.importToTarget(opts, rc)
    print('imported', ok, 'in %.1fs' % (time.time()-t0))
    print('root occurrences', rc.occurrences.count, 'root bodies', rc.bRepBodies.count)
    for o in rc.occurrences:
        bb = o.boundingBox
        mn = [round(v*10,3) for v in bb.minPoint.asArray()]
        mx = [round(v*10,3) for v in bb.maxPoint.asArray()]
        print('OCC', o.name, 'min(mm)', mn, 'max(mm)', mx, 'children', o.childOccurrences.count, 'bodies', o.bRepBodies.count)
