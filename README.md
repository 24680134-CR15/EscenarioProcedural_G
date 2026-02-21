# Escenario Procedural

Este proyecto consiste en la creación de un camino generado mediante código en Blender. Se diseñó una curva personalizada para definir la trayectoria y posteriormente se configuró una cámara para que recorriera el interior del camino, simulando un desplazamiento dinámico. 

El objetivo fue aplicar programación para automatizar tanto la generación del escenario como la animación, creando un entorno procedural de forma eficiente.
## Desarrollo del Proyecto

### Paso 1: Código base

Primero tomamos un código base proporcionado en la clase de Graficación. Este código nos sirvió como punto de partida para comenzar a trabajar en la generación del escenario dentro de Blender mediante programación.
<img width="901" height="837" alt="image" src="https://github.com/user-attachments/assets/52084bcb-7383-444a-888b-b728016e4914" />

```python
import bpy
import random

def crear_material(nombre, color_rgb):
    # Crea un material básico con un color específico
    mat = bpy.data.materials.new(name=nombre)
    mat.diffuse_color = (*color_rgb, 1.0)  # RGBA
    return mat

def generar_escenario():
    # 1. Limpiar la escena previa
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # 2. Definir materiales (Basado en modelos de color RGB)
    mat_pared_a = crear_material("ParedOscura", (0.1, 0.1, 0.1))
    mat_pared_b = crear_material("ParedDetalle", (0.8, 0.2, 0.0))  # Naranja rojizo

    # 3. Parámetros del escenario
    largo_pasillo = 10
    ancho_pasillo = 4

    # 4. Ciclo para construir paredes (Transformación: Traslación)
    for i in range(largo_pasillo):
        # Pared Izquierda
        bpy.ops.mesh.primitive_cube_add(location=(-ancho_pasillo, i * 2, 1))
        pared_izq = bpy.context.active_object

        # Aplicar material de forma alternada
        if i % 2 == 0:
            pared_izq.data.materials.append(mat_pared_a)
        else:
            pared_izq.data.materials.append(mat_pared_b)

        # Escalamiento
        pared_izq.scale.z = 1.5

        # Pared Derecha
        bpy.ops.mesh.primitive_cube_add(location=(ancho_pasillo, i * 2, 1))
        pared_der = bpy.context.active_object
        pared_der.data.materials.append(mat_pared_a)

    # 5. Agregar un suelo (Escalamiento y Posicionamiento)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, (largo_pasillo - 1), 0))
    suelo = bpy.context.active_object
    suelo.scale.x = ancho_pasillo + 1
    suelo.scale.y = largo_pasillo + 1

generar_escenario()
```
<img width="1568" height="888" alt="image" src="https://github.com/user-attachments/assets/27274d49-e7b0-43c6-b17e-a3015f20bc2c" />

### Paso 2: Aplicación de la curva y ajustes visuales

En este paso aplicamos una curva al escenario para darle una trayectoria más dinámica. En lugar de mantener el camino completamente recto, utilizamos una curva para modificar su dirección y generar un recorrido más natural.

Además, se realizaron ajustes en la apariencia de los muros, modificando sus materiales y detalles visuales para darles mayor personalidad. También se agregó el suelo completo del escenario, permitiendo que el camino tuviera una base continua y más realista.

Con estos cambios, el entorno dejó de ser una estructura básica y comenzó a verse como un escenario más completo y definido.

```Python
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
```
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/675f15d9-b0ab-466e-a7da-d8a599614f4c" />

### Paso 3: Integración de la cámara y guía de recorrido

En este paso se agregó una cámara al escenario y se creó una guía (path) para que pudiera seguir una trayectoria definida. Esto permitió que el recorrido dentro del camino se viera más suave y fluido.

Al hacer que la cámara siguiera esta guía, se logró una animación más controlada y natural, mejorando la experiencia visual del desplazamiento a través del escenario.
```Python
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
```
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/2257c8de-0552-4c2c-8be2-9be401289481" />

### Paso 4: Ajustes finales y solución de problemas

En la etapa final surgieron algunas dificultades para lograr que la cámara recorriera correctamente el camino, principalmente por la poca familiaridad con el entorno de Blender y sus herramientas de animación.

Para solucionarlo, se utilizaron frames clave marcados al inicio y al final de la guía de la cámara (la línea negra que define la trayectoria). Esto permitió controlar el movimiento a lo largo del tiempo y asegurar que la cámara recorriera todo el camino de manera completa y fluida.


https://github.com/user-attachments/assets/9433561a-8bcf-4873-bb82-7fad7d8b2255

## Conclusión

Este proyecto permitió aplicar programación dentro de Blender para crear un escenario procedural desde cero y animarlo de forma dinámica. A pesar de algunas dificultades durante el proceso, se logró generar un camino curvo y un recorrido fluido de cámara, fortaleciendo tanto el entendimiento del entorno como el uso de animaciones mediante código.

https://github.com/user-attachments/assets/c1bb97a2-2392-4fd4-865d-75774593337c
