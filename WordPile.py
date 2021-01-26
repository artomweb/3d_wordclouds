import bpy
import numpy as np
import random
import time
import os 
import sys
import re
import json
import ast

def srgb_to_linearrgb(c):
   if   c < 0:       return 0
   elif c < 0.04045: return c/12.92
   else:             return ((c+0.055)/1.055)**2.4

def hex_to_rgb(h,alpha=1):
   r = (h & 0xff0000) >> 16
   g = (h & 0x00ff00) >> 8
   b = (h & 0x0000ff)
   return tuple([srgb_to_linearrgb(c/0xff) for c in (r,g,b)] + [alpha])


def create_scene(bpyscene):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


    bpy.ops.object.light_add(type='AREA', radius=3, align='WORLD', location=(-3, -3, 1.5))
    bpy.ops.transform.rotate(value=-1.09453, orient_axis='Y', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    bpy.ops.transform.rotate(value=0.802275, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    bpy.context.object.data.energy = 240

    bpy.ops.object.light_add(type='AREA', radius=3, align='WORLD', location=(7, -0.4, 1.5))
    bpy.ops.transform.rotate(value=-1.09453, orient_axis='Y', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    bpy.ops.transform.rotate(value=-3.306, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    bpy.context.object.data.energy = 200

    bpy.ops.object.light_add(type='AREA', radius=3, align='WORLD', location=(1.55, 2.99, 2.3))
    bpy.ops.transform.rotate(value=-0.9, orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    bpy.context.object.data.energy = 200

    bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(0, 0, 0), rotation=(0.111701, 1.00995e-10, 0.0628319))
    bpy.ops.object.rotation_clear(clear_delta=False)
    bpy.ops.transform.translate(value=(1.245, -5.68, 11.49))
    bpy.ops.transform.rotate(value=0.449807, orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    bpyscene.camera = bpy.context.object

    bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(0, 0, -0.5))
    bpy.ops.transform.resize(value=(15, 10, 1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"use_normal_flip":False, "mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, -0.492551), "orient_type":'NORMAL', "orient_matrix":((0, -1, 0), (1, 0, -0), (0, 0, 1)), "orient_matrix_type":'NORMAL', "constraint_axis":(False, False, True)})
    bpy.ops.object.editmode_toggle()

    bpy.ops.rigidbody.object_add(type='PASSIVE')

def sort_words(words_freq, add_exclude, num_words):
    top_list = []

    if num_words > len(words_freq):
        num_words = len(words_freq)

    for w in sorted(words_freq, key=words_freq.get, reverse=True)[:num_words]:
        if w not in add_exclude:
            top_list.append([w, words_freq[w]])


    top_list.sort(key = lambda x: x[1])

    max_val = top_list[-1][1]
    min_val = top_list[0][1]

    for i in range(len(top_list)):
       top_list[i][1] = round(((top_list[i][1] - min_val) / (max_val - min_val)), 4)
    
    return top_list

def conv_rgb(color_pal):
    col_pal_rgb = []

    for c in color_pal:
       col_pal_rgb.append(hex_to_rgb(int(c, 16)))
    
    return col_pal_rgb


def create_material(color_pal, random_color):
    material = bpy.data.materials.new(name="Random Colour")
    material.use_nodes = True

    bsdf = material.node_tree.nodes.get('Principled BSDF')

    material_output = material.node_tree.nodes.get('Material Output')

    material.node_tree.links.new(material_output.inputs[0], bsdf.outputs[0])

    if not random_color:
        col_pal_rgb = conv_rgb(color_pal)

        col_ramp = material.node_tree.nodes.new('ShaderNodeValToRGB')
        col_ramp.color_ramp.interpolation = 'CONSTANT'
        material.node_tree.links.new(bsdf.inputs[0], col_ramp.outputs[0])
        col_ramp.color_ramp.elements.remove(col_ramp.color_ramp.elements[0])
        spacing = 1/len(col_pal_rgb)

        pos = 0

        for i in range(len(col_pal_rgb)):
            col_ramp.color_ramp.elements.new(pos)
            col_ramp.color_ramp.elements[i].color = col_pal_rgb[i]
            pos += spacing

    else:
        hue_sat = material.node_tree.nodes.new('ShaderNodeHueSaturation')
        hue_sat.inputs[4].default_value = (0.8, .11, 0.134, 1)
        hue_sat.inputs[1].default_value = 0.9

        material.node_tree.links.new(bsdf.inputs[0], hue_sat.outputs[0])

        math = material.node_tree.nodes.new('ShaderNodeMath')

        material.node_tree.links.new(hue_sat.inputs[0], math.outputs[0])

        col_ramp = material.node_tree.nodes.new('ShaderNodeMath')
        col_ramp.operation = 'MULTIPLY'
        col_ramp.inputs[1].default_value = random.uniform(0.3, 10)

        material.node_tree.links.new(math.inputs[0], col_ramp.outputs[0])


    obj_info = material.node_tree.nodes.new('ShaderNodeObjectInfo')
    material.node_tree.links.new(col_ramp.inputs[0], obj_info.outputs[4])

    return material


def generate_objects(top_list, material, current_height, vertical_offset, mi_max, li_max, s_f, extrusion):
    for word in top_list:
        bpy.ops.object.text_add(enter_editmode=False, align='WORLD', location=(0,0, current_height))
        bpy.context.active_object.name = word[0]
        bpy.context.active_object.data.body = word[0]
        bpy.context.object.data.extrude = extrusion
        bpy.context.object.data.bevel_depth = 0.015
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
        if word[1] > 0.5:
            bpy.ops.transform.translate(value=(random.uniform(-mi_max, mi_max), random.uniform(-mi_max, mi_max), 0), orient_type='GLOBAL')
        else:
            bpy.ops.transform.translate(value=(random.uniform(-li_max, li_max), random.uniform(-li_max, li_max), 0), orient_type='GLOBAL')

        bpy.ops.transform.resize(value=((0.5 + word[1])*s_f, (0.5 + word[1])*s_f, 1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)))
        bpy.ops.transform.rotate(value=random.uniform(-.1, .1), orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)

        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.rigidbody.object_add()
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.active_object.active_material = material
        current_height += vertical_offset


def setup_render(bpyscene, URI):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    override = {'scene': bpy.context.scene,
           'point_cache': bpy.context.scene.rigidbody_world.point_cache}

    #bpyscene.rigidbody_world.substeps_per_frame = 104

    bpyscene.rigidbody_world.point_cache.frame_end = 75

    bpyscene.frame_set(75)


    bpy.context.scene.frame_current = 70
    bpy.ops.ptcache.bake(override, bake=True)

    bpyscene.render.engine = 'BLENDER_EEVEE'
    bpyscene.cycles.device = "GPU"

    bpyscene.render.image_settings.file_format = 'PNG'
    bpyscene.render.filepath = dir_path + '/' + URI[-22:] + '.png'
    bpy.ops.render.render(write_still = 1)

    bpy.ops.wm.save_as_mainfile(filepath=dir_path + '/' + URI[-22:] + '.blend')

    bpy.ops.ptcache.free_bake_all(override)

def main_blender(URI, settingsDict):
    try:
        num_words = int(settingsDict['num_words'])

        mi_max = float(settingsDict['mi_max'])
        li_max = float(settingsDict['li_max'])

        current_height = float(settingsDict['current_height'])
        vertical_offset = float(settingsDict['vertical_offset'])
        extrusion = float(settingsDict['extrusion'])
        s_f = float(settingsDict['s_f'])

        color_pal = ast.literal_eval(settingsDict['color_pal']) 
        random_color = ast.literal_eval(settingsDict['random_color'])
        add_exclude = ast.literal_eval(settingsDict['add_exclude'])

    except KeyError:
        print("Invalid config file")
        exit()

    bpyscene = bpy.context.scene

    with open(URI[-22:] + '.txt', 'r') as f:
        words_freq = json.loads(f.read())
    
    create_scene(bpyscene)
    top_list = sort_words(words_freq, add_exclude, num_words)

    material = create_material(color_pal, random_color)

    generate_objects(top_list, material, current_height, vertical_offset, mi_max, li_max, s_f, extrusion)

    setup_render(bpyscene, URI)


def look_for_file(URI):
    try:
        open(URI[-22:] + '.txt')
        print("Found frequency file for song...")
        return
    except IOError:
        print("Generate a frequency file first")
        exit()

def look_for_config():
    try:
        with open('config.txt') as f:
            cont = f.read()
    except IOError:
        print("Could not find config file, make a new one")
        exit()
    
    print("\nSettings:")
    
    settingsDict = {}

    for c in cont.split("\n"):
        try:
            setting = c.split(" = ")
            settingsDict[setting[0]] = setting[1].strip()
            print(setting[0] + ':' + setting[1])
        except IndexError:
            pass
    
    print("\n")
    return settingsDict



def validate_uri(URI_maybe):
    URI = re.findall(r"spotify:playlist:[A-Za-z0-9]{22}", URI_maybe)
    if URI:
        return URI[0]
    else:
        print("\nNot a valid URI")
        exit()


def main():
    argv = sys.argv
    URI_maybe = argv[argv.index("--") + 1]
    URI = validate_uri(URI_maybe)
    print("\n")
    print(URI)
    look_for_file(URI)
    settingsDict =  look_for_config()
    main_blender(URI, settingsDict)

if __name__ == '__main__':
    main()