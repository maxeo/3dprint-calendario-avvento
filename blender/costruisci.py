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
CAP_D = 20.0              # diametro esterno capsule 1–24
CAP25_D = CAP_D           # capsula 25: stessa misura, rossa
CORPO_L = 40.0            # lunghezza del corpo (senza tappo)
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
X_USCITA = -72.0                                  # mediana: uscita, curve, ingresso (da basso in alto)
X_CURVE = [62.0, -58.0, 22.0]
X_INGRESSO = -32.0
TETTO_USCITA = 13.0                               # il tetto del ramo basso parte qui dopo l'uscita: capsula 1 libera sopra
COL_W, COL_PASSO, COL_MARGINE = 3.0, 40.0, 15.0   # colonnine fra i bordini: larghezza, passo, distanza dalle curve
COL_GIOCO = 0.4                                   # le colonnine finiscono così prima dello spazio dei bussolotti
LIP = 4.0                                         # bordini davanti e dietro: 3 gradini (sporgono verso l'interno del canale)
Y_LIP = 4.0                                       # spessore di ogni bordino
Y_CAP = Y_LIP + 0.8                               # faccia dei tappi
D_TOT = Y_CAP + CAP_LEN + 1.0 + Y_LIP             # profondità del nastro (canale passante, niente parete di fondo)
Y_LIP_DIETRO = D_TOT - Y_LIP                      # inizio del bordino dietro
FERMO = (9.0, 12.5)                               # fermo all'uscita (spessore: ci entra il gancio della pallina; altezza)
PAL_R, PAL_H, PAL_PASSO = 2.4, 0.6, 1.5           # perno filettato delle palline (fondo, dente, passo)
PAL_GIOCO = 0.3                                   # gioco radiale perno/foro
PAL_PERNO, PAL_FORO = 7.0, 8.0                    # lunghezza del perno, profondità del foro
RINFORZO = (8.0, 5.0)                             # rinforzo sul profilo attorno al foro (raggio, sporgenza)

# tronco, cassetto, base
TR_X = -1.0                                       # sotto il baricentro del nastro
TR_W, TR_D, TR_H = 52.0, D_TOT, 60.0
TR_PARETE, TR_FONDO, TR_CIELO = 2.5, 4.0, 4.0
TEN_W, TEN_H, TEN_G = 36.0, 4.0, 0.2              # tenone sul tronco, gioco nella scanalatura del nastro
CASS_GIOCO = 0.4
PANN = 3.0                # spessore del frontale del cassetto
FESSURA = (3.2, 9.0)      # serratura (larghezza, altezza)
BASE = (190.0, 115.0, 5.0)
BASE_Y0 = -42.0
DIAM_FORO = 3.6           # fori per i perni (perni 3,40)
PERNO_D, PERNO_H = 3.40, 2.6

# chiave
CH_S = 2.4                # sezione del gambo e della mappa
CH_MAPPA = 7.6            # lunghezza della mappa (entra nella fessura da 9)
CH_R = 6.0                # raggio esterno dell'anello (deve entrare nella capsula: bocca Ø12,8)

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


def testo(s, size, depth, name):
    """Testo pieno (mesh chiusa) centrato in XY, da z = 0 a z = depth."""
    cu = bpy.data.curves.new(name, 'FONT')
    cu.body = s
    try:
        cu.font = bpy.data.fonts.load(FONT, check_existing=True)
    except Exception:
        pass
    cu.size, cu.extrude = size, depth / 2
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


def numero_inserto(s, size, depth, gioco, name):
    """Numero da inserire nel solco: stesso testo del solco con il contorno rientrato di `gioco` (anche i buchi
    di 4, 6, 8, 9, 0 si allargano), spessore depth. Il rientro sulla faccia piana resta chiuso; l'offset della curva no."""
    cu = bpy.data.curves.new(name, 'FONT')
    cu.body = s
    try:
        cu.font = bpy.data.fonts.load(FONT, check_existing=True)
    except Exception:
        pass
    cu.size = size
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
    return obj_from_bm(bm, name, C_STAMPA)


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
for p, n in (((turns[2][0][0] + R_EST, turns[2][0][1]), (1.0, 0.0)),
             ((turns[1][0][0] - R_EST, turns[1][0][1]), (-1.0, 0.0))):
    # fianchi delle curve: rinforzo sul profilo (per tutta la profondità) e foro radiale orizzontale a metà profondità
    cr = (p[0] - n[0] * (RINFORZO[0] - RINFORZO[1]), p[1] - n[1] * (RINFORZO[0] - RINFORZO[1]))
    pieni.append(extrude_xz(disco(cr, RINFORZO[0]), 0, D_TOT))
    attacchi.append((Vector((p[0] + n[0] * RINFORZO[1], D_TOT / 2, p[1] + n[1] * RINFORZO[1])), Vector((-n[0], 0, -n[1]))))
# fianco sinistro del fermo d'uscita: il fermo è già spesso FERMO[0], il foro entra nel pieno (nessun rinforzo)
attacchi.append((Vector((X_FERMO_SX, D_TOT / 2, (Z_PIANO + Z_FERMO_SU) / 2)), Vector((1, 0, 0))))
# sotto il ramo basso: aletta sotto lo smusso, foro che entra dal davanti (lungo Y)
ALETTA = (8.0, 1.0)                               # raggio, spostamento del centro oltre il fondo
for pm, n_ch in ((((ch_a[0] + ch_b[0]) / 2, (ch_a[1] + ch_b[1]) / 2), (t_ch[1], -t_ch[0])),):  # sotto lo smusso a destra
    pieni.append(extrude_xz(disco((pm[0] + n_ch[0] * ALETTA[1], pm[1] + n_ch[1] * ALETTA[1]), ALETTA[0]), 0, D_TOT))
    attacchi.append((Vector((pm[0] + n_ch[0] * 3.5, 0.0, pm[1] + n_ch[1] * 3.5)), Vector((0, 1, 0))))

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
IMBOCCO = 20.0                                    # ingresso: lunghezza della rampa che sostituisce i gradini
RAMPA_TETTO = 12.0                                # uscita: rampa dei gradini sotto la punta del tetto del ramo basso


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
tagli.append(extrude_xz([(xw0, zf(xw0)), (xw1, zf(xw1)), (xw1, ze + RC + 3), (xw0, ze + RC + 3)], -1, Y_LIP + 0.1))
# scanalatura per il tenone del tronco (aperta sul retro)
tagli.append(box(TR_X - TEN_W / 2 - TEN_G, Y_LIP, Z_PIANO - 1, TR_X + TEN_W / 2 + TEN_G, D_TOT + 1, Z_PIANO + TEN_H + TEN_G, "scan"))
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
pieces[nastro.name] = (nastro, Matrix.Rotation(-math.pi / 2, 4, 'X'))   # retro sul piatto, bordino in alto
montato(nastro, M_VERDE, "Nastro")


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
boolean(tronco, box(TR_X - TEN_W / 2, Y_LIP + 0.3, Z_PIANO - 0.5, TR_X + TEN_W / 2, TR_D, Z_PIANO + TEN_H, "ten"), 'UNION')
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
RS, RI, ST_B, ST_P = 22.0, 9.0, 3.0, 5.0
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
PALLA_R = 12.0
PB_LIP, PB_CONO_G = 0.8, 0.3                      # bordo piano al giunto, gioco fra cono e svasatura
PB_TM, PB_H, PB_PASSO, PB_L, PB_G = 6.0, 0.7, 1.5, 3.0, 0.3   # filetto: cresta maschio, dente, passo, lunghezza, gioco
PB_RC = PB_TM - PB_H                              # nocciolo del collare
PB_ZC = (PALLA_R - PB_LIP - PB_CONO_G) - PB_RC    # quota dove il cono incontra il collare
PB_RF = PB_RC + PB_G                              # cresta del filetto femmina
PB_ZT = PB_ZC + PB_L + 0.4                        # cielo del foro nella metà sopra
OCCH = (3.8, 2.2, 3.0, PALLA_R + 2.6)             # occhiello: raggio esterno, foro, spessore, quota del centro


def arco_rz(r, a0, a1, step=3.0):
    return [(r * math.cos(math.radians(a)), r * math.sin(math.radians(a))) for a in np.linspace(a0, a1, int(abs(a1 - a0) / step) + 1)]


pal_sotto = lathe([(0, -PALLA_R)] + arco_rz(PALLA_R, -88, 0)[1:] +
                  [(PALLA_R - PB_LIP - PB_CONO_G, 0), (PB_RC, PB_ZC), (PB_RC, PB_ZC + PB_L), (0, PB_ZC + PB_L)],
                  "P14_Pallina_sotto", C_STAMPA, seg=64)
boolean(pal_sotto, filetto(PB_RC - 0.2, PB_H + 0.2, PB_ZC + 0.3, PB_ZC + PB_L - 0.5, PB_RC - 1.0, PB_PASSO, seg=64), 'UNION')
pal_sopra = lathe([(PALLA_R - PB_LIP, 0), (PALLA_R, 0)] + arco_rz(PALLA_R, 0, 88)[1:] +
                  [(0, PALLA_R), (0, PB_ZT), (PB_RF, PB_ZT), (PB_RF, (PALLA_R - PB_LIP) - PB_RF)],
                  "P10_Pallina_sopra", C_STAMPA, seg=64)
boolean(pal_sopra, filetto(PB_RF - 0.2, PB_H + 0.2, PB_ZC - 0.3, PB_ZT - 0.2, PB_RF - 1.0, PB_PASSO, seg=64), 'DIFFERENCE')
occh = cyl(OCCH[0], -OCCH[2] / 2, OCCH[2] / 2, "occh", seg=48)
boolean(occh, cyl(OCCH[1], -OCCH[2] / 2 - 1, OCCH[2] / 2 + 1, "occh_f", seg=48), 'DIFFERENCE')
occh.data.transform(Matrix.Translation((0, 0, OCCH[3])) @ Matrix.Rotation(math.pi / 2, 4, 'Y'))   # foro lungo X
boolean(pal_sopra, occh, 'UNION')
paint(pal_sotto, M_ROSSO); paint(pal_sopra, M_ROSSO)
pieces[pal_sopra.name] = (pal_sopra, Matrix())                                       # giunto sul piatto
pieces[pal_sotto.name] = (pal_sotto, Matrix.Rotation(math.pi, 4, 'X'))               # capovolta, collare sul piatto

# gancio a vite: perno filettato (nel nastro), collarino, piolo con gola dove si appoggia l'occhiello
G_GOLA = (1.5, 2.0, -4.0, -9.3)                    # raggio della gola, raggio del piolo, inizio e fine della gola
gancio = lathe([(0, -12.0), (1.4, -12.0), (2.0, -11.4), (2.0, G_GOLA[3] - 0.5), (G_GOLA[0], G_GOLA[3]),
                (G_GOLA[0], G_GOLA[2]), (2.0, G_GOLA[2] + 0.5), (4.5, -1.0), (4.5, 0.0), (PAL_R, 0.0),
                (PAL_R, PAL_PERNO), (0, PAL_PERNO)], "P15_Gancio", C_STAMPA, seg=48)
boolean(gancio, filetto(PAL_R - 0.2, PAL_H + 0.2, 0.4, PAL_PERNO - 0.3, 1.0, PAL_PASSO, seg=48), 'UNION')
paint(gancio, M_ORO)
pieces[gancio.name] = (gancio, Matrix())                                             # punta del piolo sul piatto

# montaggio: nel riferimento del foro (+Z dentro il nastro, +Y in alto) la pallina pende dalla gola
R_PALLA = Matrix(((0, 1, 0), (0, 0, 1), (1, 0, 0))).to_4x4()   # X pallina -> asse del piolo, Z pallina -> in alto
z_gola = (G_GOLA[2] + G_GOLA[3]) / 2
for i, (bocca, dirz) in enumerate(attacchi):
    A = asse(bocca, dirz)
    montato(gancio, None, f"Gancio_{i}", A)
    M_p = A @ Matrix.Translation((0, -(OCCH[1] - G_GOLA[0]) - OCCH[3], z_gola)) @ R_PALLA
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
montato(base, None, "Base")


# regalo: cubo con nastri in rilievo
def regalo(L, name):
    o = box(-L / 2, -L / 2, 0, L / 2, L / 2, L, name, C_TMP)
    n1 = box(-L / 2 - 0.6, -1.5, -0.0, L / 2 + 0.6, 1.5, L + 0.6, "n1")
    n2 = box(-1.5, -L / 2 - 0.6, 0.0, 1.5, L / 2 + 0.6, L + 0.6, "n2")
    boolean(o, n1, 'UNION'); boolean(o, n2, 'UNION')
    return o


# pupazzo di neve
pup_prof = [(0, 0), (7.2, 0)] + [(9 * math.cos(math.radians(a)), 7.5 + 9 * math.sin(math.radians(a))) for a in np.linspace(-53, 50, 25)] + \
           [(6.5 * math.cos(math.radians(a)), 20.5 + 6.5 * math.sin(math.radians(a))) for a in np.linspace(-45, 50, 20)][1:] + \
           [(4.5, 25.5), (4.5, 26.5), (3.2, 26.5), (3.2, 32.0), (0, 32.0)]     # cappello a cilindro nello stesso profilo
pup = lathe(pup_prof, "pupazzo", C_TMP, seg=64)
naso = cyl(0.9, 0, 6.5, "naso", seg=16); naso.data.transform(Matrix.Translation((0, -4.0, 21.0)) @ Matrix.Rotation(math.pi / 2, 4, 'X'))
boolean(pup, naso, 'UNION')

# la base è un pezzo unico con regali e pupazzo: affondano 0,2 mm nella base, lo slicer li unisce
AFFONDO = 0.2
decori = []
reg = regalo(14.0, "regalo")
for i, (x, y, rz) in enumerate(((-50, -26, 15), (48, -24, -20), (70, 30, 5))):
    o = bpy.data.objects.new("r", reg.data.copy()); C_TMP.objects.link(o)
    o.matrix_world = Matrix.Translation((TR_X + x, y, BASE[2] - AFFONDO)) @ Matrix.Rotation(math.radians(rz), 4, 'Z')
    decori.append(o)
bpy.data.objects.remove(reg)
pup.matrix_world = Matrix.Translation((TR_X - 50, 50, BASE[2] - AFFONDO))
join_into(base, decori, 1)                         # regali rossi
join_into(base, [pup], 0)                          # pupazzo bianco come la neve
base.data.materials.append(M_ROSSO)

# ===========================================================================
# Controlli
# ===========================================================================
bm = bmesh.new(); bm.from_mesh(nastro.data)
# baricentro del nastro (tetraedri dall'origine)
bm_t = bm.copy(); bmesh.ops.triangulate(bm_t, faces=bm_t.faces)
V, cx_acc = 0.0, 0.0
for f in bm_t.faces:
    a, b, c = (v.co for v in f.verts)
    v6 = a.dot(b.cross(c))
    V += v6; cx_acc += v6 * (a.x + b.x + c.x) / 4
bm_t.free(); bm.free()
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
cz["baricentro_nastro_x_mm"] = round(cx_acc / V, 1)
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
cz["chiave_lunghezza_mm"] = round(2 * CH_R + GAMBO_L + CH_S, 1)
cz["chiave_entra_capsula25"] = (2 * CH_R + GAMBO_L + CH_S) < cz["interno_capsula_l_mm"] and 2 * CH_R + 0.5 < cz["bocca_capsula_d_mm"]
cz["mappa_chiave_vs_fessura_mm"] = [CH_MAPPA, FESSURA[1], CH_S, FESSURA[0]]
cz["mappa_trattenuta_ruotata"] = CH_MAPPA > FESSURA[0] + 2
cz["gioco_cassetto_mm"] = CASS_GIOCO
cz["perni_fori_mm"] = [PERNO_D, DIAM_FORO]

# --- pose di stampa, controlli per pezzo, STL ---------------------------------
for n, (o, mp) in pieces.items():
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-3)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-3, edges=bm.edges)
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
    o.matrix_world = saved
p = geo["pezzi"]["P01_Nastro"]["size"]
cz["nastro_sta_sul_piatto_250"] = p[0] <= 250 and p[1] <= 250 and p[2] <= 250

allco = []
for d in C_MONT.objects:
    allco += [d.matrix_world @ v.co for v in d.data.vertices]
geo["montaggio"] = {"min": [round(min(c[i] for c in allco), 1) for i in range(3)],
                    "max": [round(max(c[i] for c in allco), 1) for i in range(3)]}
geo["capsule"] = [{"n": n, "x": round(x, 2), "z": round(z, 2), "d": d} for n, x, z, d, _ in capsule]

bpy.data.collections.remove(C_TMP)
print("CONTROLLI", json.dumps(cz))
print("NASTRO", json.dumps(geo["pezzi"]["P01_Nastro"]))
if SCRIVI:
    os.makedirs(os.path.join(ROOT, "dati"), exist_ok=True)
    with open(os.path.join(ROOT, "dati", "geometria.json"), "w", encoding="utf-8") as f:
        json.dump(geo, f, indent=1, ensure_ascii=False)
    path = os.path.join(ROOT, "blender", "costruisci.py")
    txt = bpy.data.texts.get("costruisci.py") or bpy.data.texts.new("costruisci.py")
    txt.from_string(open(path, encoding="utf-8").read())
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "blender", "Calendario_Avvento.blend"))
