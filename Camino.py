import bpy
import math
import bmesh

def crear_material(nombre, color_rgb):
    if nombre in bpy.data.materials:
        return bpy.data.materials[nombre]
    mat = bpy.data.materials.new(name=nombre)
    mat.diffuse_color = (*color_rgb, 1.0)
    return mat

def crear_anillo_curvo(nombre, r_in, r_out, angulo, resolucion, inicio_y, altura, material, extruir=False):
    mesh = bpy.data.meshes.new(nombre)
    obj = bpy.data.objects.new(nombre, mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()

    verts_in = []
    verts_out = []

    # Crear vértices base
    for i in range(resolucion + 1):
        t = i / resolucion
        ang = t * angulo

        x_in = radio_centro - math.cos(ang) * r_in
        y_in = inicio_y + math.sin(ang) * r_in
        x_out = radio_centro - math.cos(ang) * r_out
        y_out = inicio_y + math.sin(ang) * r_out

        v_in = bm.verts.new((x_in, y_in, 0))
        v_out = bm.verts.new((x_out, y_out, 0))

        verts_in.append(v_in)
        verts_out.append(v_out)

    bm.verts.ensure_lookup_table()

    # Crear caras base
    for i in range(resolucion):
        bm.faces.new((
            verts_in[i],
            verts_out[i],
            verts_out[i+1],
            verts_in[i+1]
        ))

    # Si es muro, extruir correctamente sin dejar tapa interna
    if extruir:
        geom = bm.faces[:]
        extrude = bmesh.ops.extrude_face_region(bm, geom=geom)
        verts_extruidos = [ele for ele in extrude["geom"] if isinstance(ele, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=verts_extruidos, vec=(0, 0, altura))

        # Eliminar caras superiores (tapas)
        for face in bm.faces:
            if face.normal.z > 0.9:
                bm.faces.remove(face)

    bm.to_mesh(mesh)
    bm.free()

    obj.data.materials.append(material)
    return obj


def generar_camino_suave_total():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    global radio_centro
    ancho = 4
    radio_centro = 10
    largo_recto = 12
    segmentos_curva = 100
    grosor_muro = 0.3
    altura_muro = 2

    mat_pared = crear_material("Pared", (0.1, 0.1, 0.1))
    mat_suelo = crear_material("Suelo", (0.02, 0.02, 0.02))

    # ---------- RECTO INICIAL ----------
    bpy.ops.mesh.primitive_plane_add(location=(0, (largo_recto/2) - 0.5, 0))
    s1 = bpy.context.active_object
    s1.scale = (ancho, largo_recto/2 + 0.5, 1)
    s1.data.materials.append(mat_suelo)

    # Muros rectos inicio
    for i in range(largo_recto + 1):
        for lado in [-1, 1]:
            bpy.ops.mesh.primitive_cube_add(location=(lado * ancho, i, 1))
            m = bpy.context.active_object
            m.scale = (grosor_muro, 0.51, 1)
            m.data.materials.append(mat_pared)

    # ---------- CURVA ----------
    inicio_y = largo_recto - 1
    r_in = radio_centro - ancho
    r_out = radio_centro + ancho

    # Piso curvo sólido
    crear_anillo_curvo(
        "Curva_Suelo",
        r_in,
        r_out,
        math.pi/2,
        segmentos_curva,
        inicio_y,
        0,
        mat_suelo,
        extruir=False
    )

    # Muro interno curvo
    crear_anillo_curvo(
        "Muro_Interno",
        r_in - grosor_muro,
        r_in,
        math.pi/2,
        segmentos_curva,
        inicio_y,
        altura_muro,
        mat_pared,
        extruir=True
    )

    # Muro externo curvo
    crear_anillo_curvo(
        "Muro_Externo",
        r_out,
        r_out + grosor_muro,
        math.pi/2,
        segmentos_curva,
        inicio_y,
        altura_muro,
        mat_pared,
        extruir=True
    )

    # ---------- RECTO FINAL ----------
    offset_x = radio_centro
    offset_y = inicio_y + radio_centro

    bpy.ops.mesh.primitive_plane_add(location=(offset_x + (largo_recto/2), offset_y, 0))
    s2 = bpy.context.active_object
    s2.scale = (largo_recto/2 + 0.5, ancho, 1)
    s2.data.materials.append(mat_suelo)

    # Muros rectos final
    for i in range(largo_recto + 1):
        for lado in [-1, 1]:
            bpy.ops.mesh.primitive_cube_add(
                location=(offset_x + i, offset_y + (lado * ancho), 1)
            )
            m = bpy.context.active_object
            m.scale = (0.51, grosor_muro, 1)
            m.data.materials.append(mat_pared)


generar_camino_suave_total()

import bpy

# Crear cámara
bpy.ops.object.camera_add(location=(0, -5, 3))
cam = bpy.context.active_object

# Hacerla cámara activa
bpy.context.scene.camera = cam

# Rotarla ligeramente hacia abajo
cam.rotation_euler = (1.2, 0, 0)
import bpy
import math

# Crear curva
curve_data = bpy.data.curves.new(name="RutaCamara", type='CURVE')
curve_data.dimensions = '3D'

spline = curve_data.splines.new(type='BEZIER')
spline.bezier_points.add(2)

ancho = 4
radio_centro = 10
largo_recto = 12
inicio_y = largo_recto - 1
offset_x = radio_centro
offset_y = inicio_y + radio_centro

# Punto 1 (inicio recto)
spline.bezier_points[0].co = (0, 0, 1)

# Punto 2 (inicio curva)
spline.bezier_points[1].co = (0, largo_recto, 1)

# Punto 3 (final)
spline.bezier_points[2].co = (offset_x + largo_recto, offset_y, 1)

# Suavizar handles
for point in spline.bezier_points:
    point.handle_left_type = 'AUTO'
    point.handle_right_type = 'AUTO'

curve_obj = bpy.data.objects.new("RutaCamara", curve_data)
bpy.context.collection.objects.link(curve_obj)
import bpy

cam = bpy.context.scene.camera
ruta = bpy.data.objects["RutaCamara"]

# Agregar constraint Follow Path
constraint = cam.constraints.new(type='FOLLOW_PATH')
constraint.target = ruta
constraint.use_curve_follow = True

# Ajustar duración de la animación
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 120

ruta.data.path_duration = 120

# Animar el movimiento
constraint.offset = 0
cam.keyframe_insert(data_path='constraints["Follow Path"].offset', frame=1)

constraint.offset = 100
cam.keyframe_insert(data_path='constraints["Follow Path"].offset', frame=120)
