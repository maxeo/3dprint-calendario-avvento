"""Calendario Avvento · albero di Natale a scivolo: 24 capsule numerate + capsula 25 con chiave e cassetto nel tronco.

Il nastro verde è uno scivolo chiuso a serpentina: le capsule si caricano dall'ingresso in alto (prima la 1, ultima la 25),
scendono per gravità lungo i rami inclinati e le curve a U, e si prendono una alla volta dall'uscita in basso a sinistra.

Uso (dalla cartella del progetto):
    blender -b --factory-startup --python blender/costruisci.py      (scrive .blend, STL, dati/geometria.json)
oppure nel Blender aperto, via MCP: exec(open(r"D:\\3D Print\\Calendario Avvento\\blender\\costruisci.py", encoding="utf-8").read())
(nel Blender aperto costruisce solo la scena, non scrive file).

Coordinate di montaggio: X verso destra, Y verso il fondo (il davanti guarda verso -Y), Z in alto, piano della base a Z = 0.
"""
import bpy, bmesh, math, json, os
import numpy as np
from mathutils import Matrix, Vector

try:
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
except NameError:                                  # exec() dal Blender aperto
    ROOT = r"D:\3D Print\Calendario Avvento"
SCRIVI = bpy.app.background                        # file solo da riga di comando
STL = os.path.join(ROOT, "stl")

# --- misure (mm) ----------------------------------------------------------
SEG = 96
FONT = r"C:\Windows\Fonts\ariblk.ttf"

# capsule
CAP_D = 42.0              # diametro esterno capsule 1–24 (bocca Ø34,8: ci entra un Ferrero Rocher Ø30 nella stagnola)
CAP25_D = CAP_D           # capsula 25: stessa misura, rossa
CORPO_L = 32.0            # lunghezza del corpo (senza tappo)
PARETE = 1.6              # parete del corpo
COLLO_L = 6.0             # collo filettato su cui si avvita il tappo
FIL_PASSO, FIL_H = 2.0, 0.8                       # filetto: passo e altezza del dente
R_COLLO = CAP_D / 2 - 2.4                         # fondo del filetto maschio (cresta = R_COLLO + FIL_H)
PARETE_COLLO = 1.2                                # parete sotto il fondo del filetto
GIOCO_TAPPO = 0.3                                 # gioco radiale del filetto tappo/collo
TAPPO_CIELO = 1.6
NUM_H = 0.8               # profondità dei numeri incisi nel cielo del tappo (resta 0,8 di cielo)
NUM_GIOCO = 0.1           # numeri da inserire (facoltativi): contorno più stretto del solco, per lato
CAP_LEN = CORPO_L + COLLO_L + TAPPO_CIELO          # lunghezza della capsula chiusa

# scivolo (profilo nel piano XZ, estruso lungo Y)
GIOCO_CAN = 1.5                                   # aria radiale attorno alla capsula 25
RC = CAP25_D / 2 + GIOCO_CAN                      # semi-altezza del canale
T = 5.0                                           # spessore minimo del nastro fra due livelli
T_BOT = 6.0                                       # fondo sotto il ramo più basso (all'uscita)
S = 2 * RC + T                                    # interasse fra due livelli alle curve
RT = S / 2                                        # raggio della mediana nelle curve a U
PEND = 2.0                                        # pendenza dei rami (gradi)
TA = math.tan(math.radians(PEND))
X_USCITA = -75.0                                  # mediana: uscita, curve, ingresso (da basso in alto)
X_CURVE = [68.0, -55.0, 56.0, -42.0, 42.0, -27.0]
X_INGRESSO = 0.0
TAGLI = [0, 2, 4]                                 # il nastro si divide a metà di queste curve (pezzi ≤ 230 sul piatto)
TETTO_USCITA = 27.0                               # il tetto del ramo basso parte qui dopo l'uscita: capsula 1 libera sopra
COL_W, COL_PASSO, COL_MARGINE = 3.0, 60.0, 25.0   # colonnine fra i bordini: larghezza, passo, distanza dalle curve
COL_GIOCO = 0.4                                   # le colonnine finiscono così prima dello spazio dei bussolotti
LIP = 4.0                                         # bordini davanti e dietro: 3 gradini (sporgono verso l'interno del canale)
Y_LIP = 4.0                                       # spessore di ogni bordino
Y_CAP = Y_LIP + 0.8                               # faccia dei tappi
D_TOT = Y_CAP + CAP_LEN + 1.0 + Y_LIP             # profondità del nastro (canale passante, niente parete di fondo)
Y_LIP_DIETRO = D_TOT - Y_LIP                      # inizio del bordino dietro
FERMO = (9.0, 25.0)                               # fermo all'uscita (spessore: ci entra il gancio della pallina; altezza)
PAL_R, PAL_H, PAL_PASSO = 2.4, 0.6, 1.5           # perno filettato delle palline (fondo, dente, passo)
PAL_GIOCO = 0.3                                   # gioco radiale perno/foro
PAL_PERNO, PAL_FORO = 7.0, 8.0                    # lunghezza del perno, profondità del foro
RINFORZO = (8.0, 5.0)                             # rinforzo sul profilo attorno al foro (raggio, sporgenza)

# tronco, cassetto, base
TR_X = 1.5                                        # sotto il baricentro del nastro
TR_W, TR_D, TR_H = 80.0, D_TOT, 70.0
TR_PARETE, TR_FONDO, TR_CIELO = 2.5, 4.0, 4.0
TEN_W, TEN_H, TEN_G = 60.0, 6.0, 0.2              # tenone sul tronco, gioco nella scanalatura del nastro
CASS_GIOCO = 0.4
PANN = 3.0                # spessore del frontale del cassetto
FESSURA = (3.2, 9.0)      # serratura (larghezza, altezza)
BASE = (230.0, 150.0, 5.0)
BASE_Y0 = -60.0
DIAM_FORO = 3.6           # fori per i perni (perni 3,40)
PERNO_D, PERNO_H = 3.40, 2.6

# chiave
CH_S = 2.4                # sezione del gambo e della mappa
CH_MAPPA = 7.6            # lunghezza della mappa (entra nella fessura da 9)
CH_R = 6.0                # raggio esterno dell'anello (deve entrare nella capsula: bocca Ø34,8)

if bpy.app.background:
    bpy.ops.wm.read_factory_settings(use_empty=True)
else:                                               # nel Blender aperto: svuota senza ricaricare (l'addon MCP resta vivo)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    for blocks in (bpy.data.meshes, bpy.data.materials, bpy.data.collections, bpy.data.curves):
        for b in list(blocks):
            blocks.remove(b)
sc = bpy.context.scene
sc.unit_settings.scale_length = 0.001
sc.unit_settings.length_unit = 'MILLIMETERS'


def coll(name, hide=False):
    c = bpy.data.collections.new(name)
    sc.collection.children.link(c)
    c.hide_viewport = c.hide_render = hide
    return c


C_STAMPA, C_MONT = coll("PEZZI_STAMPA", True), coll("PEZZI_MONTATI")
C_TMP = coll("TMP")


def obj_from_bm(bm, name, c):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me)
    c.objects.link(o)
    return o


def boolean(target, tool, op, tolerant=False, self_int=False):
    m = target.modifiers.new("b", 'BOOLEAN')
    m.operation, m.object, m.solver = op, tool, 'EXACT'
    m.use_hole_tolerant = tolerant
    m.use_self = self_int
    bpy.context.view_layer.objects.active = target
    with bpy.context.temp_override(object=target, active_object=target):
        bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(tool)


def merge(objs, name, c):
    """Unisce più oggetti in uno (componenti anche sovrapposti), per un solo booleano."""
    bm = bmesh.new()
    for o in objs:
        me = o.data.copy(); me.transform(o.matrix_world)
        bm.from_mesh(me); bpy.data.meshes.remove(me)
        bpy.data.objects.remove(o)
    return obj_from_bm(bm, name, c)


def prism(poly, z0, z1, name, c):
    bm = bmesh.new()
    bot = [bm.verts.new((x, y, z0)) for x, y in poly]
    top = [bm.verts.new((x, y, z1)) for x, y in poly]
    bm.faces.new(bot[::-1]); bm.faces.new(top)
    for i in range(len(poly)):
        j = (i + 1) % len(poly)
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm(bm, name, c)


def extrude_xz(poly, y0, y1, name="p", c=None):
    """Profilo chiuso nel piano XZ, estruso da y0 a y1."""
    poly = [p for i, p in enumerate(poly) if math.dist(p, poly[i - 1]) > 1e-4]
    bm = bmesh.new()
    fa = [bm.verts.new((x, y0, z)) for x, z in poly]
    re = [bm.verts.new((x, y1, z)) for x, z in poly]
    bm.faces.new(fa); bm.faces.new(re[::-1])
    for i in range(len(poly)):
        j = (i + 1) % len(poly)
        bm.faces.new((fa[i], fa[j], re[j], re[i]))
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm(bm, name, c or C_TMP)


def loft_xz(p0, p1, y0, y1, name="p", c=None):
    """Come extrude_xz, ma la sezione passa da p0 (a y0) a p1 (a y1): stessi vertici, posizioni diverse."""
    bm = bmesh.new()
    fa = [bm.verts.new((x, y0, z)) for x, z in p0]
    re = [bm.verts.new((x, y1, z)) for x, z in p1]
    bm.faces.new(fa); bm.faces.new(re[::-1])
    for i in range(len(p0)):
        j = (i + 1) % len(p0)
        bm.faces.new((fa[i], fa[j], re[j], re[i]))
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm(bm, name, c or C_TMP)


def loft_multi(sezioni, name="p", c=None):
    """Solido da una serie di sezioni [(y, poligono XZ)], tutte con lo stesso numero di vertici.
    Due sezioni consecutive con la stessa y danno un gradino (faccia piana)."""
    bm = bmesh.new()
    rings = [[bm.verts.new((x, y, z)) for x, z in poly] for y, poly in sezioni]
    bm.faces.new(rings[0]); bm.faces.new(rings[-1][::-1])
    n = len(rings[0])
    for a, b in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm(bm, name, c or C_TMP)


def filetto(r_base, h, z0, z1, r_in, passo, seg=72):
    """Tubo filettato (elica destra): raggio esterno da r_base (fondo) a r_base + h (cresta), interno liscio r_in."""
    def prof(f):
        f %= 1.0
        if f < 0.1 or f >= 0.95:
            return 0.0
        if f < 0.45:
            return (f - 0.1) / 0.35
        if f < 0.6:
            return 1.0
        return (0.95 - f) / 0.35
    zs_ = list(np.arange(z0, z1, passo / 8)) + [z1]
    bm = bmesh.new()
    out = []
    for z in zs_:
        ring = []
        for k in range(seg):
            th = 2 * math.pi * k / seg
            r = r_base + h * prof((z - passo * th / (2 * math.pi)) / passo)
            ring.append(bm.verts.new((r * math.cos(th), r * math.sin(th), z)))
        out.append(ring)
    inn = [[bm.verts.new((r_in * math.cos(2 * math.pi * k / seg), r_in * math.sin(2 * math.pi * k / seg), z)) for k in range(seg)]
           for z in (z0, z1)]
    for a, b in zip(out, out[1:]):
        for k in range(seg):
            j = (k + 1) % seg
            bm.faces.new((a[k], a[j], b[j], b[k]))
    for k in range(seg):
        j = (k + 1) % seg
        bm.faces.new((inn[0][k], inn[1][k], inn[1][j], inn[0][j]))
        bm.faces.new((out[0][j], out[0][k], inn[0][k], inn[0][j]))
        bm.faces.new((out[-1][k], out[-1][j], inn[1][j], inn[1][k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm(bm, "filetto", C_TMP)


def box(x0, y0, z0, x1, y1, z1, name, c=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(x1 - x0, y1 - y0, z1 - z0), verts=bm.verts)
    bmesh.ops.translate(bm, vec=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), verts=bm.verts)
    return obj_from_bm(bm, name, c or C_TMP)


def lathe(profile, name, c, seg=SEG):
    profile = [p for i, p in enumerate(profile) if math.dist(p, profile[i - 1]) > 1e-4]
    bm = bmesh.new()
    rings = []
    for r, z in profile:
        if r == 0:
            rings.append([bm.verts.new((0, 0, z))] * seg)
        else:
            rings.append([bm.verts.new((r * math.cos(2 * math.pi * k / seg), r * math.sin(2 * math.pi * k / seg), z))
                          for k in range(seg)])
    for i in range(len(rings)):
        a, b = rings[i], rings[(i + 1) % len(rings)]
        for k in range(seg):
            q = [a[k], a[(k + 1) % seg], b[(k + 1) % seg], b[k]]
            q = [v for j, v in enumerate(q) if v not in q[:j]]
            if len(q) >= 3:
                bm.faces.new(q)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm(bm, name, c)


def cyl(r, z0, z1, name, c=None, seg=SEG):
    return lathe([(0, z0), (r, z0), (r, z1), (0, z1)], name, c or C_TMP, seg)


def cyl_y(r, x, z, y0, y1, name, seg=SEG):
    """Cilindro con asse lungo Y."""
    o = cyl(r, 0, y1 - y0, name, seg=seg)
    # mezzo segmento di rotazione: nessun vertice esattamente sotto il centro
    o.data.transform(Matrix.Translation((x, y0, z)) @ Matrix.Rotation(-math.pi / 2, 4, 'X') @ Matrix.Rotation(math.pi / seg, 4, 'Z'))
    return o


def testo(s, size, depth, name, res=12):
    """Testo pieno (mesh chiusa) centrato in XY, da z = 0 a z = depth. res: risoluzione delle curve del font."""
    cu = bpy.data.curves.new(name, 'FONT')
    cu.body = s
    try:
        cu.font = bpy.data.fonts.load(FONT, check_existing=True)
    except Exception:
        pass
    cu.size, cu.extrude = size, depth / 2
    cu.resolution_u = res
    cu.align_x, cu.align_y = 'CENTER', 'CENTER'
    cu.fill_mode = 'BOTH'
    o = bpy.data.objects.new(name, cu)
    C_TMP.objects.link(o)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    bpy.data.objects.remove(o); bpy.data.curves.remove(cu)
    me.transform(Matrix.Translation((0, 0, depth / 2)))
    bm = bmesh.new(); bm.from_mesh(me); bpy.data.meshes.remove(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm(bm, name, C_TMP)


def numero_inserto(s, size, depth, gioco, name, c=None, res=12):
    """Numero da inserire nel solco: stesso testo del solco con il contorno rientrato di `gioco` (anche i buchi
    di 4, 6, 8, 9, 0 si allargano), spessore depth. Il rientro sulla faccia piana resta chiuso; l'offset della curva no."""
    cu = bpy.data.curves.new(name, 'FONT')
    cu.body = s
    try:
        cu.font = bpy.data.fonts.load(FONT, check_existing=True)
    except Exception:
        pass
    cu.size = size
    cu.resolution_u = res
    cu.align_x, cu.align_y = 'CENTER', 'CENTER'
    cu.fill_mode = 'BOTH'
    o = bpy.data.objects.new(name, cu)
    C_TMP.objects.link(o)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    bpy.data.objects.remove(o); bpy.data.curves.remove(cu)
    bm = bmesh.new(); bm.from_mesh(me); bpy.data.meshes.remove(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    r = bmesh.ops.inset_region(bm, faces=list(bm.faces), thickness=gioco, depth=0, use_even_offset=True, use_boundary=True)
    bmesh.ops.delete(bm, geom=r["faces"], context='FACES')
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    ex = bmesh.ops.extrude_face_region(bm, geom=list(bm.faces))
    bmesh.ops.translate(bm, verts=[e for e in ex["geom"] if isinstance(e, bmesh.types.BMVert)], vec=Vector((0, 0, depth)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm(bm, name, c or C_STAMPA)


def join_into(target, objs, mat_index=0):
    """Aggiunge componenti chiusi (testi, dettagli) senza booleano: lo slicer li unisce."""
    bm = bmesh.new(); bm.from_mesh(target.data)
    for o in objs:
        me = o.data.copy(); me.transform(o.matrix_world)
        n0 = len(bm.faces)
        bm.from_mesh(me); bpy.data.meshes.remove(me)
        bm.faces.ensure_lookup_table()
        for f in bm.faces[n0:]:
            f.material_index = mat_index
        bpy.data.objects.remove(o)
    bm.to_mesh(target.data); bm.free()


def mat(name, rgb, metal=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs[0].default_value = (*rgb, 1)
    for inp in bsdf.inputs:
        if inp.identifier == "Metallic":
            inp.default_value = metal
        elif inp.identifier == "Roughness":
            inp.default_value = 0.35
    return m


def paint(o, m):
    o.data.materials.clear(); o.data.materials.append(m)


def info(o):
    bm = bmesh.new(); bm.from_mesh(o.data)
    nm = sum(1 for e in bm.edges if not e.is_manifold)
    vol = bm.calc_volume(signed=True)
    bm.free()
    co = [o.matrix_world @ v.co for v in o.data.vertices]
    mn = [min(c[i] for c in co) for i in range(3)]; mx = [max(c[i] for c in co) for i in range(3)]
    return {"min": [round(a, 2) for a in mn], "max": [round(a, 2) for a in mx],
            "size": [round(b - a, 2) for a, b in zip(mn, mx)], "volume_mm3": round(vol),
            "peso_PETG_g": round(vol * 1.27e-3, 1), "non_manifold_edges": nm}


def write_stl(o, mp, path):
    import struct
    me = o.data
    me.calc_loop_triangles()
    rot = mp.to_3x3()
    with open(path, "wb") as f:
        f.write(b"Calendario Avvento".ljust(80, b" "))
        f.write(struct.pack("<I", len(me.loop_triangles)))
        for t in me.loop_triangles:
            f.write(struct.pack("<3f", *(rot @ t.normal).normalized()))
            for vi in t.vertices:
                f.write(struct.pack("<3f", *(mp @ me.vertices[vi].co)))
            f.write(b"\0\0")


def montato(o, m, name, M=Matrix()):
    d = bpy.data.objects.new(name, o.data)
    d.matrix_world = M
    C_MONT.objects.link(d)
    return d


M_VERDE = mat("Verde", (0.06, 0.38, 0.2))
M_VERDE_CH = mat("Verde chiaro", (0.12, 0.5, 0.24))
M_BIANCO = mat("Bianco", (0.92, 0.92, 0.9))
M_ROSSO = mat("Rosso", (0.75, 0.05, 0.05))
M_ORO = mat("Oro", (0.95, 0.68, 0.1), 0.6)
M_LEGNO = mat("Legno", (0.38, 0.2, 0.1))
M_NEVE = mat("Neve", (0.97, 0.97, 0.97))

geo = {"pezzi": {}, "controlli": {}}
pieces = {}

# ===========================================================================
# Scivolo: mediana a serpentina (rami inclinati + curve a U), canale = mediana ± RC
# ===========================================================================
Z_PIANO = BASE[2] + TR_H                          # fondo piatto del nastro = cielo del tronco
COSA = math.cos(math.radians(PEND))
ZE = Z_PIANO + T_BOT + RC / COSA                  # quota della mediana all'uscita

xs = [X_USCITA] + X_CURVE + [X_INGRESSO]
legs, turns = [], []                              # rami dall'uscita all'ingresso: ((xa, za), (xb, zb)); curve: (centro, lato)
za = ZE
for i in range(len(xs) - 1):
    xa, xb = xs[i], xs[i + 1]
    zb = za + abs(xb - xa) * TA                   # percorsi dal basso in alto i rami salgono
    legs.append(((xa, za), (xb, zb)))
    if i < len(xs) - 2:
        turns.append(((xb, zb + RT), 1 if xb > xa else -1))
        za = zb + S


def leg_frame(pa, pb):
    L = math.dist(pa, pb)
    d = ((pb[0] - pa[0]) / L, (pb[1] - pa[1]) / L)
    up = (-d[1], d[0]) if d[0] > 0 else (d[1], -d[0])
    return L, d, up


def slab(pa, pb, h_lo, h_hi, ext_a=0.0, ext_b=0.0):
    L, d, u = leg_frame(pa, pb)
    a = (pa[0] - d[0] * ext_a, pa[1] - d[1] * ext_a)
    b = (pb[0] + d[0] * ext_b, pb[1] + d[1] * ext_b)
    return [(a[0] - u[0] * h_lo, a[1] - u[1] * h_lo), (b[0] - u[0] * h_lo, b[1] - u[1] * h_lo),
            (b[0] + u[0] * h_hi, b[1] + u[1] * h_hi), (a[0] + u[0] * h_hi, a[1] + u[1] * h_hi)]


def half_ring(c, side, r_in, r_out, step=3.0):
    a0, a1 = (-90, 90) if side > 0 else (90, 270)
    angs = np.linspace(a0, a1, int(180 / step) + 1)
    out = [(c[0] + r_out * math.cos(math.radians(a)), c[1] + r_out * math.sin(math.radians(a))) for a in angs]
    if r_in <= 0:
        return out
    inn = [(c[0] + r_in * math.cos(math.radians(a)), c[1] + r_in * math.sin(math.radians(a))) for a in angs[::-1]]
    return out + inn


def disco(c, r, step=7.5):
    return [(c[0] + r * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a))) for a in np.arange(0, 360, step)]


def z_on(leg, x):
    (xa, za_), (xb, zb_) = leg
    return za_ + (zb_ - za_) * (x - xa) / (xb - xa)


# --- volume pieno: rami spessi, mezzi dischi nelle curve, cunei fra i rami, fondo piatto ---
H_FUORI = RC + T
EXT = 0.6                                         # i rami entrano un filo nelle curve (niente lamelle al raccordo)
(xe, ze), (xr, zr) = legs[0]
Z_PAV_E = ze - RC / COSA                          # pavimento del canale all'uscita
X_FERMO = xe - CAP_D / 2 - 0.5                    # fine del canale = fermo della capsula 1
EA_USCITA = (xe - X_FERMO) / COSA                 # il ramo basso prosegue fino al fermo
pieni = []
for i, (pa, pb) in enumerate(legs):
    ea = EA_USCITA if i == 0 else EXT
    eb = 0.0 if i == len(legs) - 1 else EXT
    if i == 0:                                    # ramo basso: tetto solo dopo la capsula 1
        pieni.append(extrude_xz(slab(pa, pb, H_FUORI, 0.0, ea, eb), 0, D_TOT))
        L0, d0, _ = leg_frame(pa, pb)
        pt = (pa[0] + d0[0] * TETTO_USCITA, pa[1] + d0[1] * TETTO_USCITA)
        pieni.append(extrude_xz(slab(pt, pb, 0.0, H_FUORI, 0.0, eb), 0, D_TOT))
        # punta arrotondata del tetto sopra la capsula 1
        u0 = leg_frame(pa, pb)[2]
        punta = (pt[0] + u0[0] * (RC + T / 2), pt[1] + u0[1] * (RC + T / 2))
        pieni.append(extrude_xz(disco(punta, T / 2, 15), 0, D_TOT))
    else:
        pieni.append(extrude_xz(slab(pa, pb, H_FUORI, H_FUORI, ea, eb), 0, D_TOT))
for c, side in turns:
    pieni.append(extrude_xz(half_ring(c, side, 0, RT + H_FUORI), 0, D_TOT))
for i in range(len(legs) - 1):
    l1, l2 = legs[i], legs[i + 1]
    x0 = max(min(l1[0][0], l1[1][0]), min(l2[0][0], l2[1][0]))
    x1 = min(max(l1[0][0], l1[1][0]), max(l2[0][0], l2[1][0]))
    pieni.append(extrude_xz([(x0, z_on(l1, x0)), (x1, z_on(l1, x1)), (x1, z_on(l2, x1)), (x0, z_on(l2, x0))], 0, D_TOT))
# fondo piatto sotto il ramo basso (appoggio sul tronco) con il fermo all'uscita
z_fermo = ze - EA_USCITA * math.sin(math.radians(PEND))
X_FERMO_SX, Z_FERMO_SU, R_FERMO = X_FERMO - FERMO[0], Z_PAV_E + FERMO[1], 3.0   # fianco sinistro, cima, raccordi
raccordo = lambda cx, cz, a0, a1: [(cx + R_FERMO * math.cos(math.radians(a)), cz + R_FERMO * math.sin(math.radians(a)))
                                   for a in np.linspace(a0, a1, 7)]
fondo = [(xr - 28, Z_PIANO), (xr, zr - H_FUORI / COSA), (xr, zr), (xe, ze),
         (X_FERMO + 1.5, z_fermo), (X_FERMO + 1.5, Z_FERMO_SU)] + \
        raccordo(X_FERMO_SX + R_FERMO, Z_FERMO_SU - R_FERMO - 0.6, 90, 180) + \
        raccordo(X_FERMO_SX + R_FERMO, Z_PIANO + R_FERMO, 180, 270)
# (la faccia del fermo la fa la fine del canale: il pieno la supera di 1,5 mm per non avere facce quasi coincidenti)
pieni.append(extrude_xz(fondo, 0, D_TOT))
# cresta sotto la stella, sul tetto del ramo più alto
STELLA_X = (X_CURVE[-1] + X_INGRESSO) / 2 + 4
top = legs[-1]
z_tetto = lambda x: z_on(top, x) + H_FUORI / COSA
CRESTA_H, SLOT_H = 6.0, 8.0
cresta = [(STELLA_X - 16, z_tetto(STELLA_X - 16) - 1), (STELLA_X + 16, z_tetto(STELLA_X + 16) - 1),
          (STELLA_X + 7, z_tetto(STELLA_X) + CRESTA_H), (STELLA_X - 7, z_tetto(STELLA_X) + CRESTA_H)]
Z_CRESTA = z_tetto(STELLA_X) + CRESTA_H
pieni.append(extrude_xz(cresta, D_TOT / 2 - 12, D_TOT / 2 + 12))
# attacchi delle palline: fianco destro della curva alta, fianco sinistro della curva di mezzo, sotto il ramo basso
R_EST = RT + H_FUORI
ch_a, ch_b = (xr - 28, Z_PIANO), (xr, zr - H_FUORI / COSA)          # smusso sotto il ramo basso
L_ch = math.dist(ch_a, ch_b)
t_ch = ((ch_b[0] - ch_a[0]) / L_ch, (ch_b[1] - ch_a[1]) / L_ch)
attacchi = []                                     # (bocca del foro, direzione verso l'interno del nastro), in 3D
# una pallina sul fianco esterno di ogni curva, a quote alternate sopra e sotto il centro (sulle curve tagliate
# il foro e il rinforzo stanno tutti in un pezzo: |dz| >= 14)
FIANCHI = [(0, -20.0), (1, 16.0), (2, 15.0), (3, -12.0), (4, -22.0), (5, 6.0)]   # (curva, quota rispetto al centro)
for k, dz in FIANCHI:
    (cx_t, cz_t), side = turns[k]
    assert k not in TAGLI or abs(dz) >= 14.0, f"attacco della curva {k} sul taglio"
    n = (float(side), 0.0)
    p = (cx_t + n[0] * math.sqrt(R_EST ** 2 - dz ** 2), cz_t + dz)
    # fianchi delle curve: rinforzo sul profilo (per tutta la profondità) e foro radiale orizzontale a metà profondità
    cr = (p[0] - n[0] * (RINFORZO[0] - RINFORZO[1]), p[1] - n[1] * (RINFORZO[0] - RINFORZO[1]))
    pieni.append(extrude_xz(disco(cr, RINFORZO[0]), 0, D_TOT))
    attacchi.append((Vector((p[0] + n[0] * RINFORZO[1], D_TOT / 2, p[1] + n[1] * RINFORZO[1])), Vector((-n[0], 0, -n[1]))))
# davanti: foro lungo Y nel muro fra il ramo che arriva a una curva di destra e quello che riparte (lì i telai non
# sono tagliati: foro e bottone stanno tutti nel telaio davanti),
# a metà del muro, dove è spesso almeno 10 (il foro filettato è Ø7 con i denti)
DAVANTI = [(0, 110.0), (2, 76.0)]                 # (curva, distanza dal centro della curva verso sinistra)
BOTTONE = 6.0                                     # sporgenza del bottone davanti attorno al foro
for k, dd in DAVANTI:
    (cx_t, cz_t), side = turns[k]
    x = cx_t - side * dd
    z_lo, z_hi = z_on(legs[k], x) + RC / COSA, z_on(legs[k + 1], x) - RC / COSA
    assert z_hi - z_lo >= 10.0, f"muro troppo sottile per il gancio davanti alla curva {k}"
    zm = (z_lo + z_hi) / 2                        # bottone sporgente: la pallina pende staccata dal nastro
    pieni.append(extrude_xz(disco((x, zm), 7.0), -BOTTONE, 0.5))
    attacchi.append((Vector((x, -BOTTONE, zm)), Vector((0, 1, 0))))
# fianco sinistro del fermo d'uscita: il fermo è già spesso FERMO[0], il foro entra nel pieno (nessun rinforzo)
attacchi.append((Vector((X_FERMO_SX, D_TOT / 2, (Z_PIANO + Z_FERMO_SU) / 2)), Vector((1, 0, 0))))
# sotto il ramo basso: aletta sotto lo smusso, foro che entra dal davanti (lungo Y)
ALETTA = (8.0, 1.0)                               # raggio, spostamento del centro oltre il fondo
for pm, n_ch in ((((ch_a[0] + ch_b[0]) / 2, (ch_a[1] + ch_b[1]) / 2), (t_ch[1], -t_ch[0])),):  # sotto lo smusso a destra
    pieni.append(extrude_xz(disco((pm[0] + n_ch[0] * ALETTA[1], pm[1] + n_ch[1] * ALETTA[1]), ALETTA[0]), 0, D_TOT))
    pf = (pm[0] + n_ch[0] * 3.5, pm[1] + n_ch[1] * 3.5)
    pieni.append(extrude_xz(disco(pf, 6.5), -BOTTONE, 0.5))     # bottone: il foro resta tutto nel telaio davanti
    attacchi.append((Vector((pf[0], -BOTTONE, pf[1])), Vector((0, 1, 0))))

nastro = pieni.pop(0)
nastro.name = "P01_Nastro"
nastro.users_collection[0].objects.unlink(nastro); C_STAMPA.objects.link(nastro)
boolean(nastro, merge(pieni, "pieni", C_TMP), 'UNION', self_int=True)

# --- canale passante (da togliere), con i bordini a 3 gradini davanti e dietro ---
GR = Y_LIP / 3
PROFONDITA = [(-1.0, RC - LIP), (GR, RC - LIP), (GR, RC - 2 * LIP / 3), (2 * GR, RC - 2 * LIP / 3),
              (2 * GR, RC - LIP / 3), (Y_LIP, RC - LIP / 3), (Y_LIP, RC), (Y_LIP_DIETRO, RC),
              (Y_LIP_DIETRO, RC - LIP / 3), (D_TOT - 2 * GR, RC - LIP / 3), (D_TOT - 2 * GR, RC - 2 * LIP / 3),
              (D_TOT - GR, RC - 2 * LIP / 3), (D_TOT - GR, RC - LIP), (D_TOT + 1.0, RC - LIP)]
IMBOCCO = 40.0                                    # ingresso: lunghezza della rampa che sostituisce i gradini
RAMPA_TETTO = 24.0                                # uscita: rampa dei gradini sotto la punta del tetto del ramo basso


def canale_intero():
    """Tutto il canale come un solo solido spazzato lungo il percorso (rami e curve): niente sovrapposizioni.
    Ogni stazione: (punto, normale a sinistra del verso di percorrenza, sinistra aperta, destra aperta).
    Aperto = senza bordino; fra una stazione a gradini e una aperta i gradini diventano rampe morbide."""
    st = []
    for i, (pa, pb) in enumerate(legs):
        L, d, u = leg_frame(pa, pb)
        nl = (-d[1], d[0])                                     # sinistra del verso di percorrenza
        at = lambda s: (pa[0] + d[0] * s, pa[1] + d[1] * s)
        if i == 0:                                             # uscita: a sinistra (= tetto) niente bordino fino alla punta
            st += [(at(-EA_USCITA), nl, True, False), (at(TETTO_USCITA), nl, True, False),
                   (at(TETTO_USCITA + RAMPA_TETTO), nl, False, False), (at(L), nl, False, False)]
        elif i == len(legs) - 1:                               # ingresso: rampa e bocca aperta
            st += [(at(L - IMBOCCO), nl, False, False), (at(L), nl, True, True), (at(L + 30.0), nl, True, True)]
        else:
            st += [(at(L), nl, False, False)]
        if i < len(turns):
            c, side = turns[i]
            for k in range(1, 60):                             # la stazione d'inizio e di fine sono quelle dei rami
                a = -math.pi / 2 + side * math.pi * k / 60
                rad = (math.cos(a), math.sin(a))
                st.append(((c[0] + RT * rad[0], c[1] + RT * rad[1]), (-side * rad[0], -side * rad[1]), False, False))
    aperto = [RC + (h - (RC - LIP)) * 0.02 for y, h in PROFONDITA]
    bm = bmesh.new()
    rings = []
    for p, nl, sx, dx in st:
        hs = [aperto[k] if sx else h for k, (y, h) in enumerate(PROFONDITA)]
        hd = [aperto[k] if dx else h for k, (y, h) in enumerate(PROFONDITA)]
        pts = [(y, hs[k]) for k, (y, h) in enumerate(PROFONDITA)] + \
              [(y, -hd[k]) for k, (y, h) in reversed(list(enumerate(PROFONDITA)))]
        rings.append([bm.verts.new((p[0] + nl[0] * n, y, p[1] + nl[1] * n)) for y, n in pts])
    bm.faces.new(rings[0]); bm.faces.new(rings[-1][::-1])
    for a, b in zip(rings, rings[1:]):
        for i in range(len(a)):
            j = (i + 1) % len(a)
            bm.faces.new((a[i], a[j], b[j], b[i]))
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm(bm, "canale", C_TMP)


tagli = [canale_intero()]
# finestra davanti alla capsula 1 (niente bordino: si sfila in avanti)
xw0, xw1 = X_FERMO + 0.3, xe + CAP_D / 2 + 0.5
zf = lambda x: Z_PAV_E + (x - xe) * TA + 0.2
tagli.append(extrude_xz([(xw0, zf(xw0)), (xw1, zf(xw1)), (xw1, ze + RC + 3), (xw0, ze + RC + 3)], -1, Y_LIP + 0.9))   # oltre il piano del telaio: niente lamelle
# scanalatura per il tenone del tronco (aperta sul retro)
tagli.append(box(TR_X - TEN_W / 2 - TEN_G, Y_LIP + 0.8, Z_PIANO - 1, TR_X + TEN_W / 2 + TEN_G, D_TOT + 1, Z_PIANO + TEN_H + TEN_G, "scan"))
# fori filettati dei ganci delle palline
def asse(bocca, dirz):
    """Matrice che porta l'asse +Z locale nel foro: origine sulla bocca, +Z verso l'interno del nastro.
    L'asse X locale resta orizzontale, così il gancio e la pallina appesa si orientano bene."""
    z = dirz.normalized()
    x = Vector((0, 0, 1)).cross(z)
    x = x.normalized() if x.length > 1e-6 else Vector((1, 0, 0))
    y = z.cross(x)
    m = Matrix((x, y, z)).transposed().to_4x4()
    return Matrix.Translation(bocca) @ m


for i, (bocca, dirz) in enumerate(attacchi):
    rf = PAL_R + PAL_GIOCO
    foro = merge([cyl(rf, -1, PAL_FORO, "f", seg=48),
                  filetto(rf - 0.2, PAL_H + 0.2, 0.0, PAL_FORO, rf - 1.0, PAL_PASSO, seg=48)], f"foro{i}", C_TMP)
    foro.data.transform(asse(bocca, dirz))
    tagli.append(foro)
# fessura della stella
tagli.append(box(STELLA_X - 3.3, D_TOT / 2 - 1.7, Z_CRESTA - SLOT_H, STELLA_X + 3.3, D_TOT / 2 + 1.7, Z_CRESTA + 1, "fessura"))
# colonnine davanti e dietro: il canale è passante, senza di loro ogni ramo starebbe attaccato solo all'uscita.
# Stanno nello spessore dei bordini (fuori dal bussolotto) e uniscono il bordino di sopra con quello di sotto.
# Si tolgono dal solido del canale (niente facce coincidenti con il davanti e il retro del nastro).
colonne, COL_POS = [], []
for i, (pa, pb) in enumerate(legs):
    L, d, u = leg_frame(pa, pb)
    m0 = TETTO_USCITA + RAMPA_TETTO + 5 if i == 0 else COL_MARGINE
    m1 = IMBOCCO + 8 if i == len(legs) - 1 else COL_MARGINE
    if L - m0 - m1 < 0:                                   # ramo troppo corto (in cima): niente colonnine
        continue
    n = max(1, round((L - m0 - m1) / COL_PASSO) + 1)
    for s in (np.linspace(m0, L - m1, n) if n > 1 else [(m0 + L - m1) / 2]):
        c = (pa[0] + d[0] * s, pa[1] + d[1] * s)
        a = (c[0] - d[0] * COL_W / 2, c[1] - d[1] * COL_W / 2)
        b = (c[0] + d[0] * COL_W / 2, c[1] + d[1] * COL_W / 2)
        prof = slab(a, b, RC + 0.8, RC + 0.8)
        colonne.append(extrude_xz(prof, -2.0, Y_LIP - COL_GIOCO))
        colonne.append(extrude_xz(prof, D_TOT - Y_LIP + COL_GIOCO, D_TOT + 2.0))
        COL_POS.append((i, round(s, 1)))
boolean(tagli[0], merge(colonne, "colonne", C_TMP), 'DIFFERENCE', True)
boolean(nastro, merge(tagli, "tagli", C_TMP), 'DIFFERENCE', True, self_int=True)
paint(nastro, M_VERDE)


def baricentro_x(o):
    """x del baricentro (tetraedri dall'origine)."""
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    V = acc = 0.0
    for f in bm.faces:
        a, b, c = (v.co for v in f.verts)
        v6 = a.dot(b.cross(c))
        V += v6; acc += v6 * (a.x + b.x + c.x) / 4
    bm.free()
    return acc / V


BARI_X = baricentro_x(nastro)

# --- nastro in pezzi --------------------------------------------------------
# In profondità tre strati: telaio davanti (bordini, colonnine, bottoni), corpo (pareti del canale), telaio dietro.
# Si stampano tutti stesi, senza gradini a sbalzo. In altezza i corpi si tagliano a metà delle curve TAGLI (destra),
# i telai a metà delle curve TAGLI_TELAI (sinistra): ogni telaio scavalca un taglio dei corpi e tiene insieme due
# livelli. Perni stampati nel pezzo (niente perni staccati): davanti sul corpo (entrano nel telaio, che si stampa
# con la faccia interna sul piatto), dietro sul telaio (entrano nel corpo).
TAGLI_TELAI = [1, 3]                             # il telaio in cima tiene intera la curva alta (la striscia sotto l'ultimo ramo non ha colonnine)
Y_TF, Y_TD = Y_LIP + 0.3, Y_LIP_DIETRO - 0.3      # piani fra telai e corpo (0,3 oltre le facce dei gradini)
PT_D, PT_H, PT_FORO, PT_PROF = 2.6, 3.0, 3.0, 3.4  # perni dei telai: diametro, altezza; fori: diametro, profondità
PT_PASSO, PT_MARGINE, PT_MARGINE_TELAIO = 30.0, 1.1, 1.6   # distanza fra perni; materiale attorno nel corpo / nel telaio
SMUSSO_TAGLIO = 0.8                               # smusso del canale sul corpo sotto: il bussolotto scende senza urti
z_taglio = lambda k: turns[k][0][1] + 0.13        # un filo sopra la mediana: niente vertici del canale sul taglio
Z_TAGLI = [z_taglio(k) for k in TAGLI]
Z_TAGLI_T = [z_taglio(k) for k in TAGLI_TELAI]
LO, HI = -1000.0, 2000.0


def fetta(src, name, tagli_via):
    """Copia di src senza le scatole in tagli_via (disgiunte fra loro: un solo booleano pulito)."""
    o = bpy.data.objects.new(name, src.data.copy())
    C_STAMPA.objects.link(o)
    if tagli_via:
        boolean(o, merge([box(*b, "via") for b in tagli_via], "fuori", C_TMP), 'DIFFERENCE', self_int=True)
    return o


def strato(name, y0, y1):
    via = ([(-400, -100, -1000, 400, y0, 2000)] if y0 > LO else []) + ([(-400, y1, -1000, 400, D_TOT + 100, 2000)] if y1 < HI else [])
    return fetta(nastro, name, via)


def livelli(src, prefisso, bordi):
    out = []
    for i in range(len(bordi) - 1):
        via = ([(-400, -100, bordi[i] - 2000, 400, D_TOT + 100, bordi[i])] if bordi[i] > LO else []) +               ([(-400, -100, bordi[i + 1], 400, D_TOT + 100, bordi[i + 1] + 2000)] if bordi[i + 1] < HI else [])
        out.append(fetta(src, f"{prefisso}_{i + 1}", via))
    bpy.data.objects.remove(src)
    return out


bc = [LO] + Z_TAGLI + [HI]
bt = [LO] + Z_TAGLI_T + [HI]
corpi = livelli(strato("corpo", Y_TF, Y_TD), "P01_Nastro", bc)
tel_d = livelli(strato("tel_d", LO, Y_TF), "P23_Telaio_davanti", bt)
tel_r = livelli(strato("tel_r", Y_TD, HI), "P24_Telaio_dietro", bt)
bpy.data.objects.remove(nastro)
# smusso sul bordo alto del canale dei corpi (pareti esterna e interna della curva tagliata)
for i, o in enumerate(corpi[:-1]):
    (xc, zc), s = turns[TAGLI[i]]
    zp, e = bc[i + 1], SMUSSO_TAGLIO
    xo, xi = xc + s * (RT + RC), xc + s * (RT - RC)
    boolean(o, merge([extrude_xz([(xb - v * 0.2, zp - e - 0.2), (xb + v * (e + 1), zp + 1), (xb - v * 0.2, zp + 1)],
                                 Y_TF - 1, Y_TD + 1) for xb, v in ((xo, s), (xi, -s))], "smussi", C_TMP), 'DIFFERENCE', True)

# posizioni dei perni: dove c'è materiale attorno sia nel corpo sia nel telaio, ben distanziati
from mathutils.bvhtree import BVHTree


def bvh(o):
    bm = bmesh.new(); bm.from_mesh(o.data)
    t = BVHTree.FromBMesh(bm); bm.free()
    return t


def dentro(t, p, margine):
    """Punto dentro il solido e lontano almeno margine dalla superficie. Dentro/fuori: tre raggi obliqui (lontani
    dalle pendenze del nastro), attraversamenti dispari, a maggioranza; i colpi doppi sullo stesso punto non contano."""
    hit = t.find_nearest(p)
    if hit[0] is None or hit[3] < margine:
        return False
    voti = 0
    for d in (Vector((1, 0.31, 0.47)), Vector((-0.6, 0.2, 1)), Vector((0.2, -0.4, -1))):
        d = d.normalized()
        n, q, prec = 0, p.copy(), None
        for _ in range(200):
            h = t.ray_cast(q, d)
            if h[0] is None:
                break
            if prec is None or (h[0] - prec).length > 1e-3:
                n += 1
            prec = h[0]
            q = h[0] + d * 1e-3
        voti += n % 2
    return voti >= 2


def quale(bordi, z):
    return next(i for i in range(len(bordi) - 1) if bordi[i] < z < bordi[i + 1])


B_C, B_TD, B_TR = [bvh(o) for o in corpi], [bvh(o) for o in tel_d], [bvh(o) for o in tel_r]
PERNI_T = []                                      # (lato, x, z): lato -1 davanti, +1 dietro
xs_c = [v.co.x for o in corpi for v in o.data.vertices]
zs_c = [v.co.z for o in corpi for v in o.data.vertices]
for lato, yf, B_T in ((-1, Y_TF, B_TD), (1, Y_TD, B_TR)):
    cand = []
    for x in np.arange(min(xs_c), max(xs_c), 1.0):
        for z in np.arange(min(zs_c), max(zs_c), 1.0):
            if min(abs(z - zt) for zt in Z_TAGLI + Z_TAGLI_T) < PT_D:
                continue
            ic, it = quale(bc, z), quale(bt, z)
            pc = Vector((x, yf - lato * 6.0, z))                   # nel corpo, oltre il fondo del foro
            pt = Vector((x, yf + lato * (Y_TF / 2), z))             # a metà del telaio
            if dentro(B_C[ic], pc, PT_MARGINE + PT_D / 2) and dentro(B_T[it], pt, PT_MARGINE_TELAIO):
                cand.append((B_C[ic].find_nearest(pc)[3], x, z))
    cand.sort(reverse=True)
    scelti = []
    for c, x, z in cand:
        if all(math.dist((x, z), q) >= PT_PASSO for q in scelti):
            scelti.append((x, z))
    PERNI_T += [(lato, x, z) for x, z in scelti]


def perno_t(lato, x, z):
    """Perno con lo smusso in punta: parte dalla faccia di contatto e sporge verso -Y (davanti sul corpo, dietro sul telaio)."""
    r = PT_D / 2
    o = lathe([(0, -0.3), (r, -0.3), (r, PT_H - 0.4), (r - 0.4, PT_H), (0, PT_H)], "pt", C_TMP, seg=24)
    yf = Y_TF if lato < 0 else Y_TD
    o.data.transform(Matrix.Translation((x, yf, z)) @ Matrix.Rotation(math.pi / 2, 4, 'X'))   # +Z -> -Y
    return o


def foro_t(lato, x, z):
    """Foro cieco dalla faccia di contatto verso -Y (davanti nel telaio, dietro nel corpo)."""
    yf = Y_TF if lato < 0 else Y_TD
    o = cyl(PT_FORO / 2, -1.0, PT_PROF, "ft", seg=24)
    o.data.transform(Matrix.Translation((x, yf, z)) @ Matrix.Rotation(math.pi / 2, 4, 'X'))   # +Z -> -Y
    return o


for i, o in enumerate(corpi):
    davanti = [(x, z) for l, x, z in PERNI_T if l < 0 and quale(bc, z) == i]
    dietro = [(x, z) for l, x, z in PERNI_T if l > 0 and quale(bc, z) == i]
    if davanti:
        boolean(o, merge([perno_t(-1, x, z) for x, z in davanti], "perni", C_TMP), 'UNION', self_int=True)
    if dietro:
        boolean(o, merge([foro_t(1, x, z) for x, z in dietro], "fori", C_TMP), 'DIFFERENCE', self_int=True)
for i, o in enumerate(tel_d):
    fd = [(x, z) for l, x, z in PERNI_T if l < 0 and quale(bt, z) == i]
    if fd:
        boolean(o, merge([foro_t(-1, x, z) for x, z in fd], "fori", C_TMP), 'DIFFERENCE', self_int=True)
for i, o in enumerate(tel_r):
    pd = [(x, z) for l, x, z in PERNI_T if l > 0 and quale(bt, z) == i]
    if pd:
        boolean(o, merge([perno_t(1, x, z) for x, z in pd], "perni", C_TMP), 'UNION', self_int=True)
pezzi_n = corpi + tel_d + tel_r
for o in pezzi_n:
    paint(o, M_VERDE)
    pieces[o.name] = (o, Matrix.Rotation(-math.pi / 2, 4, 'X'))   # faccia con il Y più grande sul piatto, perni in alto
    montato(o, M_VERDE, o.name.split("_", 1)[1])


# --- tracciato campionato e posizioni delle capsule ---
def campioni(step=0.2):
    out = []                                      # (s, x, z, nx, nz): n verso il pavimento / la parete esterna
    s = 0.0
    for i, (pa, pb) in enumerate(legs):
        L, d, u = leg_frame(pa, pb)
        for k in range(int(L / step)):
            t = k * step
            out.append((s + t, pa[0] + d[0] * t, pa[1] + d[1] * t, -u[0], -u[1]))
        s += L
        if i < len(turns):
            c, side = turns[i]
            arc = math.pi * RT
            for k in range(int(arc / step)):
                a = -math.pi / 2 + side * k * step / RT
                out.append((s + k * step, c[0] + RT * math.cos(a), c[1] + RT * math.sin(a), math.cos(a), math.sin(a)))
            s += arc
    return out, s


camp, S_TOT = campioni()
diam = [CAP_D] * 24 + [CAP25_D]
capsule = []                                      # (numero, x, z, diametro, s)
for s, x, z, nx, nz in camp:
    if len(capsule) == len(diam):
        break
    r = diam[len(capsule)] / 2
    cx, cz = x + nx * (RC - r), z + nz * (RC - r)
    if not capsule or math.dist((cx, cz), capsule[-1][1:3]) >= capsule[-1][3] / 2 + r + 0.3:
        capsule.append((len(capsule) + 1, cx, cz, 2 * r, s))
# quante capsule Ø20 ci starebbero in tutto (capienza)
cap_max, last = 0, None
for s, x, z, nx, nz in camp:
    cx, cz = x + nx * (RC - CAP_D / 2), z + nz * (RC - CAP_D / 2)
    if last is None or math.dist((cx, cz), last) >= CAP_D + 0.3:
        cap_max += 1; last = (cx, cz)

# ===========================================================================
# Capsule: corpo con collo + tappo numerato
# ===========================================================================
RI_COLLO = R_COLLO - PARETE_COLLO                 # foro del collo (bocca della capsula)


def corpo(dia, name):
    r = dia / 2; ri = RI_COLLO
    prof = [(0, 0), (r, 0), (r, CORPO_L), (R_COLLO, CORPO_L), (R_COLLO, CORPO_L + COLLO_L),
            (ri, CORPO_L + COLLO_L), (ri, CORPO_L - 2), (r - PARETE, CORPO_L - 2 - (r - PARETE - ri)),
            (r - PARETE, PARETE), (0, PARETE)]                  # interno largo, raccordo a 45° verso la bocca
    o = lathe(prof, name, C_STAMPA)
    # filetto maschio sul collo (il fondo entra 0,2 nel collo, si ferma 0,3 prima della bocca)
    boolean(o, filetto(R_COLLO - 0.2, FIL_H + 0.2, CORPO_L + 0.6, CORPO_L + COLLO_L - 0.3, ri + 0.4, FIL_PASSO), 'UNION')
    return o


H_TAPPO = COLLO_L + TAPPO_CIELO


def tappo_base(dia):
    """Tappo senza numero, già nella posa di stampa: cielo in alto, bocca filettata sul piatto."""
    r = dia / 2; rf = R_COLLO + GIOCO_TAPPO                      # cresta del filetto femmina
    prof = [(0, 0), (r - 0.6, 0), (r, 0.6), (r, H_TAPPO), (rf, H_TAPPO), (rf, TAPPO_CIELO), (0, TAPPO_CIELO)]
    o = lathe(prof, "tappo_base", C_TMP)
    boolean(o, filetto(rf - 0.2, FIL_H + 0.2, TAPPO_CIELO + 0.4, H_TAPPO + 1.0, rf - 1.0, FIL_PASSO), 'DIFFERENCE')
    # cielo in alto ruotando di 180° attorno a X (una rotazione non cambia il verso del filetto)
    o.data.transform(Matrix.Translation((0, 0, H_TAPPO)) @ Matrix.Rotation(math.pi, 4, 'X'))
    return o


def num_size(dia, numero):
    return dia * (0.5 if numero < 10 else 0.42)


def tappo(base, dia, numero, name):
    o = bpy.data.objects.new(name, base.data.copy())
    C_STAMPA.objects.link(o)
    t = testo(str(numero), num_size(dia, numero), NUM_H + 1.0, "num")
    t.data.transform(Matrix.Translation((0, 0, H_TAPPO - NUM_H)))
    boolean(o, t, 'DIFFERENCE')                    # numero inciso: tappo di un colore solo
    return o, H_TAPPO


corpo_p = corpo(CAP_D, "P02_Corpo_capsula")
corpo_25 = corpo(CAP25_D, "P04_Corpo_capsula_25")
paint(corpo_p, M_VERDE_CH); paint(corpo_25, M_ROSSO)
pieces[corpo_p.name] = (corpo_p, Matrix())
pieces[corpo_25.name] = (corpo_25, Matrix())
tb = tappo_base(CAP_D)
# --- viste per la guida (solo il viewer: gli STL di stampa non cambiano) ---
# Solo le superfici che si vedono, a risoluzione regolare, con il font meno fitto. I tappi sono un corpo comune
# (fianco e smusso, file unico) più il cielo con il numero inciso, l'unica parte diversa da tappo a tappo.
V_SEG, V_RES = 48, 5
viste, comuni = {}, {}


def vista_tappo_corpo(dia):
    r = dia / 2
    o = lathe([(0, H_TAPPO), (r - 0.6, H_TAPPO), (r, H_TAPPO - 0.6), (r, 0), (0, 0)], "vista_tappo_corpo", C_TMP, seg=V_SEG)
    bm = bmesh.new(); bm.from_mesh(o.data)       # via il cielo: lo porta ogni tappo con il suo numero
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if all(v.co.z > H_TAPPO - 1e-3 for v in f.verts)], context='FACES')
    bm.to_mesh(o.data); bm.free()
    return o


def vista_tappo_cielo(dia, numero):
    r = dia / 2 - 0.6
    z0 = H_TAPPO - NUM_H - 0.3
    o = lathe([(0, z0), (r, z0), (r, H_TAPPO), (0, H_TAPPO)], f"vista_cielo_{numero}", C_TMP, seg=V_SEG)
    t = testo(str(numero), num_size(dia, numero), NUM_H + 1.0, "num", res=V_RES)
    t.data.transform(Matrix.Translation((0, 0, H_TAPPO - NUM_H)))
    boolean(o, t, 'DIFFERENCE')
    bm = bmesh.new(); bm.from_mesh(o.data)       # restano la faccia del cielo e il solco
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if any(v.co.z < z0 + 0.15 for v in f.verts)], context='FACES')
    bm.to_mesh(o.data); bm.free()
    return o


def vista_corpo(dia):
    r = dia / 2                                  # il collo sta dentro il tappo: basta il cilindro
    return lathe([(0, 0), (r, 0), (r, CORPO_L), (R_COLLO, CORPO_L), (R_COLLO, CORPO_L + COLLO_L - 0.5),
                  (0, CORPO_L + COLLO_L - 0.5)], "vista_corpo", C_TMP, seg=V_SEG)


viste[corpo_p.name] = vista_corpo(CAP_D)
viste[corpo_25.name] = vista_corpo(CAP25_D)
for n, x, zc, d, _ in capsule:
    nm = f"P03_Tappo_{n:02d}" if n < 25 else "P05_Tappo_25"
    o, H = tappo(tb, d, n, nm)
    rosso = n % 5 == 0                             # multipli di 5 (e la 25): tappo rosso
    o.data.materials.clear()
    o.data.materials.append(M_ROSSO if rosso else M_BIANCO)
    pieces[o.name] = (o, Matrix())
    # numero da inserire nel solco (facoltativo, altro colore): a filo del cielo, stampato steso
    ni = numero_inserto(str(n), num_size(d, n), NUM_H, NUM_GIOCO, f"P16_Numero_{n:02d}")
    ni.data.transform(Matrix.Translation((0, 0, H - NUM_H)))
    ni.data.materials.append(M_ORO if n == 25 else (M_BIANCO if rosso else M_ROSSO))
    pieces[ni.name] = (ni, Matrix.Rotation(math.pi, 4, 'X'))   # capovolto: la faccia a vista sul piatto
    viste[o.name] = vista_tappo_cielo(d, n)
    comuni.setdefault("tappo_corpo", (vista_tappo_corpo(d), o.name))
    vn = numero_inserto(str(n), num_size(d, n), NUM_H, NUM_GIOCO, f"vista_num_{n}", C_TMP, res=V_RES)
    vn.data.transform(Matrix.Translation((0, 0, H - NUM_H)))
    viste[ni.name] = vn
    # montaggio: asse lungo Y, tappo davanti (verso -Y)
    rot = Matrix.Rotation(math.pi / 2, 4, 'X')     # +Z -> -Y
    montato(o, None, f"Tappo_{n:02d}", Matrix.Translation((x, Y_CAP + H, zc)) @ rot)
    montato(ni, None, f"Numero_{n:02d}", Matrix.Translation((x, Y_CAP + H, zc)) @ rot @ Matrix.Translation((0, 0, 0.05)))  # 0,05 fuori: niente facce coincidenti nella vista
    cb = corpo_25 if n == 25 else corpo_p
    y_fondo = Y_CAP + TAPPO_CIELO + COLLO_L + CORPO_L
    montato(cb, None, f"Corpo_{n:02d}", Matrix.Translation((x, y_fondo, zc)) @ rot)

# ===========================================================================
# Tronco con tenone e cassetto, base, stella, chiave, palline, decorazioni
# ===========================================================================
TR_Y0 = 0.0
tronco = box(TR_X - TR_W / 2, TR_Y0, BASE[2], TR_X + TR_W / 2, TR_Y0 + TR_D, Z_PIANO, "P06_Tronco", C_STAMPA)
cav = box(TR_X - TR_W / 2 + TR_PARETE, TR_Y0 - 1, BASE[2] + TR_FONDO, TR_X + TR_W / 2 - TR_PARETE, TR_Y0 + TR_D - TR_PARETE,
          Z_PIANO - TR_CIELO, "cav")
ven = []                                           # venature della corteccia sui fianchi e sul retro
for k, x in enumerate(np.linspace(-TR_W / 2 + 7, TR_W / 2 - 7, 5)):
    ven.append(box(TR_X + x - 0.8, TR_Y0 + TR_D - 0.8, BASE[2] + 8 + 3 * (k % 2), TR_X + x + 0.8, TR_Y0 + TR_D + 1,
                   Z_PIANO - 6 - 4 * (k % 2), "v"))
for side in (-1, 1):
    for k, y in enumerate(np.linspace(TR_Y0 + 8, TR_Y0 + TR_D - 8, 5)):
        x0 = TR_X + side * TR_W / 2
        ven.append(box(x0 - 0.8, y - 0.8, BASE[2] + 7 + 4 * (k % 2), x0 + 0.8, y + 0.8, Z_PIANO - 7 - 3 * (k % 2), "v"))
for x in (-12.0, 12.0):                            # fori dei perni della base
    f = cyl(DIAM_FORO / 2, BASE[2] - 1, BASE[2] + 3, "fb"); f.data.transform(Matrix.Translation((TR_X + x, TR_Y0 + TR_D / 2, 0)))
    ven.append(f)
boolean(tronco, merge([cav] + ven, "t", C_TMP), 'DIFFERENCE', True)
# tenone: entra dal retro nella scanalatura sotto il nastro, si ferma contro il bordino
boolean(tronco, box(TR_X - TEN_W / 2, Y_LIP + 1.1, Z_PIANO - 0.5, TR_X + TEN_W / 2, TR_D, Z_PIANO + TEN_H, "ten"), 'UNION')
paint(tronco, M_LEGNO)
pieces[tronco.name] = (tronco, Matrix.Rotation(-math.pi / 2, 4, 'X'))  # retro sul piatto, apertura in alto
montato(tronco, None, "Tronco")

# cassetto
cw = TR_W - 2 * TR_PARETE - 2 * CASS_GIOCO
ch = TR_H - TR_FONDO - TR_CIELO - 2 * CASS_GIOCO
cd = TR_D - TR_PARETE - 1.0
cz0 = BASE[2] + TR_FONDO + CASS_GIOCO
cass = box(TR_X - cw / 2, TR_Y0, cz0, TR_X + cw / 2, TR_Y0 + cd, cz0 + ch, "P07_Cassetto", C_STAMPA)
interno = box(TR_X - cw / 2 + 1.6, TR_Y0 + 1.6, cz0 + 1.6, TR_X + cw / 2 - 1.6, TR_Y0 + cd - 1.6, cz0 + ch + 1, "ci")
boolean(cass, interno, 'DIFFERENCE')
fr = box(TR_X - TR_W / 2, TR_Y0 - PANN, BASE[2] + 0.4, TR_X + TR_W / 2, TR_Y0 + 1.6, Z_PIANO - 0.4, "fr")
boolean(cass, fr, 'UNION')
FESS_Z = BASE[2] + TR_H * 0.62
fe = box(TR_X - FESSURA[0] / 2, TR_Y0 - PANN - 1, FESS_Z - FESSURA[1] / 2, TR_X + FESSURA[0] / 2, TR_Y0 + 2.6, FESS_Z + FESSURA[1] / 2, "fess")
boolean(cass, fe, 'DIFFERENCE')
paint(cass, M_ROSSO)
pieces[cass.name] = (cass, Matrix.Rotation(math.pi / 2, 4, 'X'))   # frontale sul piatto
montato(cass, None, "Cassetto")

# chiave piatta: anello + gambo + mappa a T (spessore CH_S)
GAMBO_L = PANN + 4.5
chiave = cyl(CH_R, 0, CH_S, "P08_Chiave", C_STAMPA, seg=48)
boolean(chiave, cyl(CH_R - 3.0, -1, CH_S + 1, "buco", seg=48), 'DIFFERENCE')
boolean(chiave, box(CH_R - 1.0, -CH_S / 2, 0, CH_R + GAMBO_L + 0.3, CH_S / 2, CH_S, "gambo"), 'UNION')
boolean(chiave, box(CH_R + GAMBO_L, -CH_MAPPA / 2, 0, CH_R + GAMBO_L + CH_S, CH_MAPPA / 2, CH_S, "mappa"), 'UNION')
paint(chiave, M_ORO)
pieces[chiave.name] = (chiave, Matrix())
montato(chiave, None, "Chiave", Matrix.Translation((TR_X - 30, BASE_Y0 - 22, 0)) @ Matrix.Rotation(math.radians(20), 4, 'Z'))

# stella: base piatta + piramide sfaccettata + linguetta che entra nella fessura sulla cresta
RS, RI, ST_B, ST_P = 36.0, 14.5, 3.0, 8.0         # ST_B = spessore della linguetta: entra nella fessura da 3,4
star = [(RS * math.cos(math.radians(90 + 36 * k)) if k % 2 == 0 else RI * math.cos(math.radians(90 + 36 * k)),
         RS * math.sin(math.radians(90 + 36 * k)) if k % 2 == 0 else RI * math.sin(math.radians(90 + 36 * k))) for k in range(10)]
bm = bmesh.new()
b0 = [bm.verts.new((x, y, 0)) for x, y in star]
b1 = [bm.verts.new((x, y, ST_B)) for x, y in star]
apex = bm.verts.new((0, 0, ST_B + ST_P))
bm.faces.new(b0[::-1])
for i in range(10):
    j = (i + 1) % 10
    bm.faces.new((b0[i], b0[j], b1[j], b1[i]))
    bm.faces.new((b1[i], b1[j], apex))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
stella = obj_from_bm(bm, "P09_Stella", C_STAMPA)
LING = SLOT_H + RS * math.sin(math.radians(54)) + 1.0     # le punte basse restano 1 mm sopra la cresta
ling = box(-3.0, -LING, 0, 3.0, -RI * 0.6, ST_B, "ling")
boolean(stella, ling, 'UNION')
paint(stella, M_ORO)
pieces[stella.name] = (stella, Matrix())
M_st = Matrix.Translation((STELLA_X, D_TOT / 2 + ST_B / 2, Z_CRESTA - SLOT_H + LING)) @ Matrix.Rotation(math.pi / 2, 4, 'X')
montato(stella, None, "Stella", M_st)

# --- palline: due semisfere avvitate (come le palline per i gatti), occhiello in cima ---
# metà sotto («vite»): collare filettato su un cono a 45°; metà sopra («madrevite»): svasatura a 45° e filetto interno.
# Si stampano senza supporti: la sopra sul piano del giunto (occhiello in alto), la sotto capovolta sul collare.
PALLA_R, PB_W = 12.0, 1.6                         # pallina Ø24, guscio vuoto spesso 1,6 (come le palline del gatto)
PB_RI = PALLA_R - PB_W
PB_S = -3.0                                       # giunto sotto l'equatore: il filetto largo sta dove la sfera è ampia
PB_LIP, PB_CONO_G = 0.8, 0.3                      # bordo piano al giunto, gioco fra cono e svasatura
PB_TM, PB_H, PB_PASSO, PB_L, PB_G = 9.0, 0.7, 1.5, 3.0, 0.3   # filetto: cresta maschio, dente, passo, lunghezza, gioco
PB_RC = PB_TM - PB_H                              # nocciolo del collare
PB_RF = PB_RC + PB_G                              # cresta del filetto femmina (foro della metà sopra)
PB_RL = math.sqrt(PALLA_R ** 2 - PB_S ** 2) - PB_LIP   # dove il bordo piano diventa svasatura a 45°
PB_Z0 = PB_S + PB_RL - PB_RF                      # inizio del filetto (fine della svasatura)
PB_ZC = PB_Z0 + PB_L                              # cima del collare
PB_ZR = PB_ZC + 0.4                               # cima dell'anello filettato della metà sopra
PB_BORE = PB_RC - PB_W                            # foro del collare: le due metà fanno un solo vuoto
OCCH = (3.8, 2.2, 3.0, PALLA_R + 2.6)             # occhiello: raggio esterno, foro, spessore, quota del centro


def arco_rz(r, a0, a1, step=3.0):
    return [(r * math.cos(math.radians(a)), r * math.sin(math.radians(a))) for a in np.linspace(a0, a1, int(abs(a1 - a0) / step) + 1)]


def incontro_45(c):
    """z (sotto il giunto) dove la retta a 45° r = c - z incontra la sfera interna."""
    return (c - math.sqrt(2 * PB_RI ** 2 - c ** 2)) / 2


a_s = math.degrees(math.asin(PB_S / PALLA_R))
# metà sotto («vite»): calotta dal polo al giunto, bordo, cono a 45°, collare filettato forato; dentro cono parallelo
c_in = (PB_RL - PB_CONO_G + PB_S) - PB_W * math.sqrt(2)          # cono interno a PB_W dal cono esterno
z_m = incontro_45(c_in)
a_m = math.degrees(math.asin(z_m / PB_RI))
a_r = math.degrees(math.asin(PB_ZR / PB_RI))


def occhiello(seg):
    oc = cyl(OCCH[0], -OCCH[2] / 2, OCCH[2] / 2, "occh", seg=seg)
    boolean(oc, cyl(OCCH[1], -OCCH[2] / 2 - 1, OCCH[2] / 2 + 1, "occh_f", seg=seg), 'DIFFERENCE')
    oc.data.transform(Matrix.Translation((0, 0, OCCH[3])) @ Matrix.Rotation(math.pi / 2, 4, 'Y'))   # foro lungo X
    return oc


def pallina_meta(sopra, name, c, seg, step, seg_occh):
    """Metà della pallina, come si stampa."""
    if sopra:   # «madrevite»: bordo piano sul giunto, svasatura a 45°, anello filettato, poi la cupola vuota
        o = lathe([(PB_RL, PB_S)] + arco_rz(PALLA_R, a_s, 88, step) + [(0, PALLA_R), (0, PB_RI)] +
                  arco_rz(PB_RI, 88, a_r, step)[1:] + [(PB_RF, PB_ZR), (PB_RF, PB_Z0)], name, c, seg=seg)
        boolean(o, filetto(PB_RF - 0.2, PB_H + 0.2, PB_Z0 - 0.3, PB_ZR - 0.2, PB_RF - 1.0, PB_PASSO, seg=seg), 'DIFFERENCE')
        boolean(o, occhiello(seg_occh), 'UNION')
    else:       # «vite»: calotta dal polo al giunto, bordo, cono a 45°, collare filettato forato; dentro cono parallelo
        o = lathe([(0, -PALLA_R)] + arco_rz(PALLA_R, -88, a_s, step)[1:] +
                  [(PB_RL - PB_CONO_G, PB_S), (PB_RC, PB_Z0), (PB_RC, PB_ZC), (PB_BORE, PB_ZC), (PB_BORE, c_in - PB_BORE),
                   (c_in - z_m, z_m)] + arco_rz(PB_RI, a_m, -88, step)[1:] + [(0, -PB_RI)], name, c, seg=seg)
        boolean(o, filetto(PB_RC - 0.2, PB_H + 0.2, PB_Z0 + 0.3, PB_ZC - 0.5, PB_BORE + 0.6, PB_PASSO, seg=seg), 'UNION')
    paint(o, M_ROSSO)
    return o


pal_sotto = pallina_meta(False, "P14_Pallina_sotto", C_STAMPA, 96, 3.0, 48)
pal_sopra = pallina_meta(True, "P10_Pallina_sopra", C_STAMPA, 96, 3.0, 48)
# viste: da fuori la pallina è una sfera; ogni metà è una calotta chiusa dal disco del giunto (più l'occhiello)
r_g = math.sqrt(PALLA_R ** 2 - PB_S ** 2)
viste[pal_sotto.name] = lathe([(0, -PALLA_R)] + arco_rz(PALLA_R, -88, a_s, 7.5)[1:] + [(r_g, PB_S), (0, PB_S)],
                              "vista_sotto", C_TMP, seg=32)
viste[pal_sopra.name] = lathe([(0, PB_S), (r_g, PB_S)] + arco_rz(PALLA_R, a_s, 88, 7.5)[1:] + [(0, PALLA_R)],
                              "vista_sopra", C_TMP, seg=32)
boolean(viste[pal_sopra.name], occhiello(16), 'UNION')
SC_PAL = 1.5                                      # palline in scala (filetti e occhiello compresi): Ø36
S_PAL = Matrix.Scale(SC_PAL, 4)
for o in (pal_sotto, pal_sopra, viste[pal_sotto.name], viste[pal_sopra.name]):
    o.data.transform(S_PAL)
pieces[pal_sopra.name] = (pal_sopra, Matrix())                                       # giunto sul piatto
pieces[pal_sotto.name] = (pal_sotto, Matrix.Rotation(math.pi, 4, 'X'))               # capovolta, collare sul piatto

# gancio a vite: perno filettato (nel nastro), collarino, piolo con gola dove si appoggia l'occhiello
G_GOLA = (2.0, 2.5, -16.0, -21.3)                  # raggio della gola, raggio del piolo, inizio e fine della gola
G_PUNTA = -24.0                                    # piolo lungo: la pallina Ø36 pende lontano dal nastro
G_PROF = [(0, G_PUNTA), (G_GOLA[1] - 0.6, G_PUNTA), (G_GOLA[1], G_PUNTA + 0.6), (G_GOLA[1], G_GOLA[3] - 0.5), (G_GOLA[0], G_GOLA[3]),
          (G_GOLA[0], G_GOLA[2]), (G_GOLA[1], G_GOLA[2] + 0.5), (4.5, -1.0), (4.5, 0.0), (PAL_R, 0.0),
          (PAL_R, PAL_PERNO), (0, PAL_PERNO)]
gancio = lathe(G_PROF, "P15_Gancio", C_STAMPA, seg=48)
viste[gancio.name] = lathe(G_PROF, "vista_gancio", C_TMP, seg=24)     # il perno filettato sta dentro il nastro
boolean(gancio, filetto(PAL_R - 0.2, PAL_H + 0.2, 0.4, PAL_PERNO - 0.3, 1.0, PAL_PASSO, seg=48), 'UNION')
paint(gancio, M_ORO)
pieces[gancio.name] = (gancio, Matrix())                                             # punta del piolo sul piatto

# montaggio: nel riferimento del foro (+Z dentro il nastro, +Y in alto) la pallina pende dalla gola
R_PALLA = Matrix(((0, 1, 0), (0, 0, 1), (1, 0, 0))).to_4x4()   # X pallina -> asse del piolo, Z pallina -> in alto
z_gola = (G_GOLA[2] + G_GOLA[3]) / 2
for i, (bocca, dirz) in enumerate(attacchi):
    A = asse(bocca, dirz)
    montato(gancio, None, f"Gancio_{i}", A)
    M_p = A @ Matrix.Translation((0, -(OCCH[1] * SC_PAL - G_GOLA[0]) - OCCH[3] * SC_PAL, z_gola)) @ R_PALLA
    montato(pal_sopra, None, f"Pallina_sopra_{i}", M_p)
    montato(pal_sotto, None, f"Pallina_sotto_{i}", M_p)

# base con bordo arrotondato e perni
bx, by, bz = BASE
rr = 15.0
bpoly = []
for cx, cy, a0 in ((bx / 2 - rr, by - rr, 0), (-bx / 2 + rr, by - rr, 90), (-bx / 2 + rr, rr, 180), (bx / 2 - rr, rr, 270)):
    for a in np.linspace(a0, a0 + 90, 12):
        bpoly.append((TR_X + cx + rr * math.cos(math.radians(a)), BASE_Y0 + cy + rr * math.sin(math.radians(a))))
base = prism(bpoly, 0, bz, "P11_Base", C_STAMPA)
for x in (-12.0, 12.0):
    p = cyl(PERNO_D / 2, bz - 0.5, bz + PERNO_H, "pb", seg=32)
    p.data.transform(Matrix.Translation((TR_X + x, TR_Y0 + TR_D / 2, 0)))
    boolean(base, p, 'UNION')
paint(base, M_NEVE)
pieces[base.name] = (base, Matrix())


# regalo: cubo con un solco a croce (fianchi e cielo) in cui si infila dall'alto il nastro, stampato a parte
NA_W, NA_P, NA_S, NA_G = 3.0, 0.8, 0.6, 0.15     # nastro: larghezza, profondità del solco, sporgenza, gioco laterale


def croce(L, w, fuori, dentro, z_core, z0, name):
    """Due fasce larghe w che avvolgono il cubo L fino a `fuori` dal fianco, svuotate fino a `dentro` dal fianco."""
    a = box(-L / 2 - fuori, -w / 2, z0, L / 2 + fuori, w / 2, L + fuori, "c1")
    b = box(-w / 2, -L / 2 - fuori, z0, w / 2, L / 2 + fuori, L + fuori, "c2")
    boolean(a, b, 'UNION')
    boolean(a, box(-L / 2 + dentro, -L / 2 + dentro, -2, L / 2 - dentro, L / 2 - dentro, z_core, "core"), 'DIFFERENCE')
    a.name = name
    return a


def regalo(L, name, c=None):
    o = box(-L / 2, -L / 2, 0, L / 2, L / 2, L, name, c or C_TMP)
    boolean(o, croce(L, NA_W + 2 * NA_G, 1.0, NA_P, L - NA_P, -1, "solco"), 'DIFFERENCE')
    return o


def nastro_regalo(L, name):
    n = croce(L, NA_W, NA_S, NA_P - 0.05, L - NA_P + 0.05, 0, name)    # 0,05 d'aria sul fondo del solco
    C_TMP.objects.unlink(n); C_STAMPA.objects.link(n)
    return n


# pupazzo di neve: testa piatta in cima con un perno per il cappello (a parte, nero), foro per il naso (a parte, giallo)
SC_PUP = 1.6                                       # scala del pupazzo rispetto al primo albero piccolo
PUP_TESTA = 25.5                                   # quota del taglio piatto della testa
CAP_PERNO, CAP_FORO = (3.0, 2.0), (3.2, 2.2)       # perno sulla testa e foro nel cappello: diametro, altezza
# naso e occhi si avvitano nella testa: filetto Ø3 passo 1 (dente 0,4, gioco radiale 0,2), il più piccolo che viene
# con l'ugello 0,4. Testa: centro a 20,5, raggio 6,5. Le direzioni tengono le madreviti separate e gli occhi sotto la tesa.
PF_D, PF_P, PF_H, PF_G = 3.0, 1.0, 0.4, 0.2        # cresta del maschio, passo, dente, gioco radiale
TESTA_C, TESTA_R = 20.5, 6.5
NASO = (2.2, 2.4, 1.8, 4.5)                        # codolo, foro, raggio della base della carota, lunghezza della carota
NASO_Z = 21.0                                      # quota del naso (dritto in avanti)
OCCHI = (2.0, 2.2, 1.2, 36, 30)                    # codolo, profondità del foro, raggio del bottone, angolo di lato, in alto
OCCHI_D = 1.7                                      # occhi a incastro a forza: codolo e foro uguali (i fori piccoli escono stretti)
r_t = math.sqrt(6.5 ** 2 - (PUP_TESTA - 20.5) ** 2)
pup_prof = [(0, 0), (7.2, 0)] + [(9 * math.cos(math.radians(a)), 7.5 + 9 * math.sin(math.radians(a))) for a in np.linspace(-53, 50, 40)] + \
           [(6.5 * math.cos(math.radians(a)), 20.5 + 6.5 * math.sin(math.radians(a))) for a in np.linspace(-45, 50, 32)][1:-1] + \
           [(r_t, PUP_TESTA), (CAP_PERNO[0] / 2, PUP_TESTA), (CAP_PERNO[0] / 2, PUP_TESTA + CAP_PERNO[1]), (0, PUP_TESTA + CAP_PERNO[1])]
pup = lathe(pup_prof, "pupazzo", C_TMP, seg=96)


def asse_testa(d, prof):
    """Riferimento con +Z verso fuori lungo d e origine a `prof` sotto la superficie della testa."""
    d = Vector(d).normalized()
    c = Vector((0, 0, TESTA_C))
    if abs(d.y + 1) < 1e-9:                         # naso: dritto in avanti, il punto è a NASO_Z
        p = Vector((0, -math.sqrt(TESTA_R ** 2 - (NASO_Z - TESTA_C) ** 2), NASO_Z))
    else:
        p = c + d * TESTA_R
    return Matrix.Translation(p - d * prof) @ Vector((0, 0, 1)).rotation_difference(d).to_matrix().to_4x4()


def madrevite(prof, M):
    """Foro filettato profondo prof (dalla superficie verso dentro), per il maschio PF_*."""
    rf = PF_D / 2 - PF_H + PF_G                     # cresta della femmina = nocciolo del maschio + gioco
    f = cyl(rf, 0, prof + 1.5, "fb", seg=32)
    boolean(f, filetto(rf - 0.2, PF_H + 0.2, 0, prof + 1.5, 0.3, PF_P, seg=32), 'UNION')
    f.data.transform(M)
    return f


def vite_codolo(lung, testa_prof, name):
    """Codolo filettato da z = 0 (punta) a z = lung, poi la testa (profilo lathe sopra lung)."""
    r0 = PF_D / 2 - PF_H                            # nocciolo del maschio
    o = lathe([(0, 0), (r0, 0)] + [(r, lung + z) for r, z in testa_prof] + [(0, lung + testa_prof[-1][1])], name, C_STAMPA, seg=32)
    boolean(o, filetto(r0 - 0.2, PF_H + 0.2, 0.3, lung - 0.2, max(0.3, r0 - 0.8), PF_P, seg=32), 'UNION')
    return o


d_naso = (0, -1, 0)
a_o, e_o = math.radians(OCCHI[3]), math.radians(OCCHI[4])
d_occhi = [(sx * math.cos(e_o) * math.sin(a_o), -math.cos(e_o) * math.cos(a_o), math.sin(e_o)) for sx in (-1, 1)]
# ogni foro arriva alla profondità indicata e sbuca 1,5 fuori dalla testa
fori_occhi = []
for d in d_occhi:
    f = cyl(OCCHI_D / 2, 0, OCCHI[1] + 1.5, "fo", seg=24)
    f.data.transform(asse_testa(d, OCCHI[1]))
    fori_occhi.append(f)
for f in [madrevite(NASO[1], asse_testa(d_naso, NASO[1]))] + fori_occhi:
    boolean(pup, f, 'DIFFERENCE')
cappello = lathe([(CAP_FORO[0] / 2, 0), (4.5, 0), (4.5, 1.0), (3.2, 1.0), (3.2, 6.5), (0, 6.5), (0, CAP_FORO[1]),
                  (CAP_FORO[0] / 2, CAP_FORO[1])], "P18_Cappello", C_STAMPA, seg=48)
paint(cappello, mat("Nero", (0.02, 0.02, 0.02)))
pieces[cappello.name] = (cappello, Matrix())                         # tesa sul piatto, foro in basso
r0_v = PF_D / 2 - PF_H
naso = vite_codolo(NASO[0], [(r0_v, 0), (NASO[2], 0), (0.3, NASO[3])], "P19_Naso")
paint(naso, M_ORO)
pieces[naso.name] = (naso, Matrix())                                 # in piedi sul codolo (brim consigliato)
cupola = [(OCCHI[2] * math.cos(math.radians(a)), 0.3 + 0.5 * math.sin(math.radians(a))) for a in range(0, 90, 15)]
occhio = lathe([(0, 0), (OCCHI_D / 2 - 0.15, 0), (OCCHI_D / 2, 0.15)] + [(r, OCCHI[0] + z) for r, z in [(OCCHI_D / 2, 0), (OCCHI[2], 0)] + cupola] +
               [(0, OCCHI[0] + 0.3 + 0.5)], "P21_Occhio", C_STAMPA, seg=24)   # punta smussata per entrare
paint(occhio, mat("Nero", (0.02, 0.02, 0.02)))
pieces[occhio.name] = (occhio, Matrix())                             # in piedi sul codolo, cupola in alto

# regali a parte (si stampano nel loro colore: davanti a destra verde, gli altri due rossi), ognuno fermato da
# due perni in diagonale in fori ciechi del regalo e della base: si centra e non ruota
REG_L = 22.0
REG_POS = ((-62, -38, 15), (62, -34, -20), (88, 45, 5))       # x (dal tronco), y, rotazione; il secondo è il verde (REG_VERDE)
REG_VERDE = 1                                                 # davanti a destra
REG_PERNI = ((-5.5, -5.5), (5.5, 5.5))                      # posizione dei perni nel riferimento del regalo
REG_FORO = (DIAM_FORO, 3.0)                                  # fori nel regalo e nella base: diametro, profondità
REG_PERNO = (PERNO_D, 2 * REG_FORO[1] - 0.4)                 # perno: 0,2 d'aria in fondo a ciascun foro
def foro_regalo(z0, z1, M):
    f = cyl(REG_FORO[0] / 2, z0, z1, "f", seg=32)
    f.data.transform(M)
    return f


reg = regalo(REG_L, "P12_Regalo", C_STAMPA)
boolean(reg, merge([foro_regalo(-1, REG_FORO[1], Matrix.Translation((px, py, 0))) for px, py in REG_PERNI],
                   "fori_regalo", C_TMP), 'DIFFERENCE')
paint(reg, M_ROSSO)
pieces[reg.name] = (reg, Matrix())                                   # fondo forato sul piatto
M_reg = [Matrix.Translation((TR_X + x, y, BASE[2])) @ Matrix.Rotation(math.radians(rz), 4, 'Z') for x, y, rz in REG_POS]
boolean(base, merge([foro_regalo(-REG_FORO[1], 1, M @ Matrix.Translation((px, py, 0))) for M in M_reg for px, py in REG_PERNI],
                    "fori_base", C_TMP), 'DIFFERENCE')
r_p, l_p = REG_PERNO[0] / 2, REG_PERNO[1]
perno_reg = lathe([(0, 0), (r_p - 0.3, 0), (r_p, 0.3), (r_p, l_p - 0.3), (r_p - 0.3, l_p), (0, l_p)],
                  "P17_Perno_regalo", C_STAMPA, seg=32)
paint(perno_reg, M_NEVE)
pieces[perno_reg.name] = (perno_reg, Matrix())
nastro_r = nastro_regalo(REG_L, "P20_Nastro_regalo")
paint(nastro_r, M_VERDE_CH)
pieces[nastro_r.name] = (nastro_r, Matrix.Rotation(math.pi, 4, 'X'))   # capovolto: la croce sul piatto, gambe in alto
for i, M in enumerate(M_reg):
    d = montato(reg, None, f"Regalo_{i}", M)
    if i == REG_VERDE:                             # stesso STL, ma questo si stampa verde
        d.material_slots[0].link = 'OBJECT'
        d.material_slots[0].material = M_VERDE_CH
    d = montato(nastro_r, None, f"Nastro_regalo_{i}", M)
    if i == REG_VERDE:                             # sul regalo verde il nastro è rosso, sugli altri verde
        d.material_slots[0].link = 'OBJECT'
        d.material_slots[0].material = M_ROSSO
    for k, (px, py) in enumerate(REG_PERNI):
        montato(perno_reg, None, f"Perno_regalo_{i}_{k}", M @ Matrix.Translation((px, py, -REG_FORO[1] + 0.2)))

# il pupazzo resta unito alla base: affonda 0,2 mm, lo slicer lo unisce (bianco come la base)
AFFONDO = 0.2
S_PUP = Matrix.Scale(SC_PUP, 4)                    # pupazzo, cappello, naso e occhi in scala (filetti compresi)
for o in (pup, cappello, naso, occhio):
    o.data.transform(S_PUP)
pup.matrix_world = Matrix.Translation((TR_X - 65, 62, BASE[2] - AFFONDO))
join_into(base, [pup], 0)
montato(base, None, "Base")
M_pup = Matrix.Translation((TR_X - 65, 62, BASE[2] - AFFONDO))
montato(cappello, None, "Cappello", M_pup @ S_PUP @ Matrix.Translation((0, 0, PUP_TESTA)) @ S_PUP.inverted())
montato(naso, None, "Naso", M_pup @ S_PUP @ asse_testa(d_naso, NASO[0]) @ S_PUP.inverted())
for k, d in enumerate(d_occhi):
    montato(occhio, None, f"Occhio_{k}", M_pup @ S_PUP @ asse_testa(d, OCCHI[0]) @ S_PUP.inverted())

# ===========================================================================
# Controlli
# ===========================================================================
cz = geo["controlli"]
cz["canale_altezza_mm"] = round(2 * RC, 2)
cz["gioco_capsula25_mm"] = round(2 * RC - CAP25_D, 2)
cz["gioco_capsula20_mm"] = round(2 * RC - CAP_D, 2)
cz["due_capsule_non_si_sovrappongono"] = 2 * RC < 2 * CAP_D - 6
cz["pendenza_rami_gradi"] = PEND
cz["raggio_mediana_curve_mm"] = RT
cz["spessore_min_nastro_mm"] = T
cz["lunghezza_percorso_mm"] = round(S_TOT, 1)
cz["capsule_posizionate"] = len(capsule)
cz["capienza_capsule_20"] = cap_max
cz["spazio_libero_ingresso_mm"] = round(S_TOT - capsule[-1][4] - capsule[-1][3] / 2, 1) if len(capsule) == 25 else None
cz["bordino_mm"] = [LIP, Y_LIP]
cz["aria_capsula_fra_i_bordini_mm"] = round(Y_LIP_DIETRO - Y_LIP - CAP_LEN, 2)
cz["profondita_nastro_mm"] = round(D_TOT, 2)
cz["baricentro_nastro_x_mm"] = round(BARI_X, 1)
cz["tronco_x_mm"] = [TR_X - TR_W / 2, TR_X + TR_W / 2]
cz["tenone_scanalatura_mm"] = [TEN_W, TEN_W + 2 * TEN_G, TEN_H, TEN_H + TEN_G]
cz["gioco_radiale_tappo_mm"] = GIOCO_TAPPO
cz["bocca_capsula_d_mm"] = round(2 * RI_COLLO, 2)
cz["filetto_mm"] = {"passo": FIL_PASSO, "dente": FIL_H, "gioco_radiale": GIOCO_TAPPO, "parete_tappo": round(CAP_D / 2 - R_COLLO - GIOCO_TAPPO - FIL_H, 2)}
cz["interno_capsula_l_mm"] = round(CORPO_L + COLLO_L - PARETE, 1)
cz["colonnine_per_lato"] = len(COL_POS)
cz["colonnine_posizioni_ramo_mm"] = COL_POS
cz["colonnine_aria_bussolotto_mm"] = [round(Y_CAP - (Y_LIP - COL_GIOCO), 2),
                                      round((D_TOT - Y_LIP + COL_GIOCO) - (Y_CAP + CAP_LEN), 2)]
cz["numero_inciso_mm"] = NUM_H
cz["numero_da_inserire_gioco_mm"] = NUM_GIOCO
cz["cielo_sotto_numero_mm"] = round(TAPPO_CIELO - NUM_H, 2)
cz["pallina_mm"] = {"scala_rispetto_alle_misure": SC_PAL, "diametro_stampato": 2 * PALLA_R * SC_PAL,
                    "occhiello_spessore_vs_gola": [round(OCCH[2] * SC_PAL, 2), round(G_GOLA[2] - G_GOLA[3], 2)], "diametro": 2 * PALLA_R, "guscio": PB_W, "filetto_cresta_d": 2 * PB_TM,
                    "parete_anello_sopra": round(math.sqrt(PALLA_R ** 2 - PB_ZR ** 2) - (PB_RF + PB_H), 2),
                    "margine_vuoto_sopra": round(math.sqrt(PB_RI ** 2 - PB_ZR ** 2) - (PB_RF + PB_H), 2),
                    "gioco_collare_cima": round(PB_ZR - PB_ZC, 2)}
cz["chiave_lunghezza_mm"] = round(2 * CH_R + GAMBO_L + CH_S, 1)
cz["chiave_entra_capsula25"] = (2 * CH_R + GAMBO_L + CH_S) < cz["interno_capsula_l_mm"] and 2 * CH_R + 0.5 < cz["bocca_capsula_d_mm"]
cz["mappa_chiave_vs_fessura_mm"] = [CH_MAPPA, FESSURA[1], CH_S, FESSURA[0]]
cz["mappa_trattenuta_ruotata"] = CH_MAPPA > FESSURA[0] + 2
cz["gioco_cassetto_mm"] = CASS_GIOCO
cz["perni_fori_mm"] = [PERNO_D, DIAM_FORO]
cz["regali_mm"] = {"foro": list(REG_FORO), "perno": [PERNO_D, round(REG_PERNO[1], 2)], "fondo_sotto_foro_base": round(BASE[2] - REG_FORO[1], 2),
                   "aria_in_fondo_ai_fori": round((2 * REG_FORO[1] - REG_PERNO[1]) / 2, 2)}
cz["nastro_regalo_mm"] = {"larghezza": NA_W, "solco": [NA_W + 2 * NA_G, NA_P], "sporgenza": NA_S, "spessore": round(NA_P - 0.05 + NA_S, 2)}
cz["pupazzo_mm"] = {"scala_rispetto_alle_misure": SC_PUP, "perno_cappello": list(CAP_PERNO), "foro_cappello": list(CAP_FORO),
                    "filetto_viso": {"diametro": PF_D, "passo": PF_P, "dente": PF_H, "gioco_radiale": PF_G},
                    "naso": {"codolo": NASO[0], "foro": NASO[1], "base_d": 2 * NASO[2], "carota": NASO[3]},
                    "occhi": {"codolo": [OCCHI_D, OCCHI[0]], "foro": [OCCHI_D, OCCHI[1]], "bottone_d": 2 * OCCHI[2], "angoli": [OCCHI[3], OCCHI[4]]}}

# --- pose di stampa, controlli per pezzo, STL ---------------------------------
for n, (o, mp) in pieces.items():
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-3)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-3, edges=bm.edges)
    # i tagli del nastro lasciano buchini di pochi decimi sul davanti e sul retro, attorno alle curve: si chiudono
    bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=16)
    bm.to_mesh(o.data); bm.free()
    co = [mp @ v.co for v in o.data.vertices]
    zmin = min(c.z for c in co)
    mp = Matrix.Translation((0, 0, -zmin)) @ mp
    pieces[n] = (o, mp)
    saved = o.matrix_world.copy()
    o.matrix_world = mp
    bpy.context.view_layer.update()
    geo["pezzi"][n] = info(o)
    geo.setdefault("pose", {})[n] = [[[round(v, 4) for v in row] for row in (d.matrix_world @ mp.inverted())]
                                     for d in C_MONT.objects if d.data == o.data]
    if SCRIVI:
        os.makedirs(STL, exist_ok=True)
        write_stl(o, mp, os.path.join(STL, n + ".stl"))
        os.makedirs(os.path.join(ROOT, "dati", "vista"), exist_ok=True)
        if n in viste:   # mesh solo per la vista della guida, nella stessa posa del file di stampa
            write_stl(viste[n], mp, os.path.join(ROOT, "dati", "vista", n + ".stl"))
        for cn, (ov, pn) in comuni.items():     # mesh comuni a più pezzi, nella posa del primo che la usa
            if pn == n:
                write_stl(ov, mp, os.path.join(ROOT, "dati", "vista", cn + ".stl"))
    o.matrix_world = saved
cz["nastro_pezzi_mm"] = {o.name: geo["pezzi"][o.name]["size"] for o in pezzi_n}
cz["nastro_pezzi_stanno_in_235"] = all(max(geo["pezzi"][o.name]["size"]) <= 235 for o in pezzi_n)
cz["nastro_perni_telai"] = {"davanti": sum(1 for p in PERNI_T if p[0] < 0), "dietro": sum(1 for p in PERNI_T if p[0] > 0),
                            "perno": [PT_D, PT_H], "foro": [PT_FORO, PT_PROF],
                            "posizioni": [[l, round(x, 1), round(z, 1)] for l, x, z in PERNI_T]}

allco = []
for d in C_MONT.objects:
    allco += [d.matrix_world @ v.co for v in d.data.vertices]
geo["montaggio"] = {"min": [round(min(c[i] for c in allco), 1) for i in range(3)],
                    "max": [round(max(c[i] for c in allco), 1) for i in range(3)]}
geo["capsule"] = [{"n": n, "x": round(x, 2), "z": round(z, 2), "d": d} for n, x, z, d, _ in capsule]

bpy.data.collections.remove(C_TMP)
print("CONTROLLI", json.dumps(cz))
print("NASTRO", json.dumps({o.name: geo["pezzi"][o.name] for o in pezzi_n}))
if SCRIVI:
    os.makedirs(os.path.join(ROOT, "dati"), exist_ok=True)
    with open(os.path.join(ROOT, "dati", "geometria.json"), "w", encoding="utf-8") as f:
        json.dump(geo, f, indent=1, ensure_ascii=False)
    path = os.path.join(ROOT, "blender", "costruisci.py")
    txt = bpy.data.texts.get("costruisci.py") or bpy.data.texts.new("costruisci.py")
    txt.from_string(open(path, encoding="utf-8").read())
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "blender", "Calendario_Avvento.blend"))
