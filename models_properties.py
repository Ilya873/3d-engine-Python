from OpenGL.GL import *
import pygame
import json
from pywavefront import Wavefront

models_data = []

# Функция для загрузки текстур и присвоения ID каждой текстуре
def load_textures():
    for model_data in models_data:
        texture_file = model_data['texture_file']
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        texture_surface = pygame.image.load(texture_file)
        texture_data = pygame.image.tostring(texture_surface, "RGBA", True)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, texture_surface.get_width(), texture_surface.get_height(),
                     0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)

        model_data['texture_id'] = texture_id

# Импорт моделей
def import_obj_model(model_file, texture_file, model_name):
    vertices = []
    faces = []
    tex_coords = []

    with open(model_file, 'r') as file:
        for line in file:
            parts = line.split()
            if not parts:
                continue
            if parts[0] == 'v':
                vertex = [float(val) for val in parts[1:]]
                vertices.append(vertex)
            elif parts[0] == 'vt':
                tex_coord = [float(val) for val in parts[1:]]
                tex_coords.append(tex_coord)
            elif parts[0] == 'f':
                face = []
                for vertex_str in parts[1:]:
                    vertex_parts = vertex_str.split('/')
                    vertex_index = int(vertex_parts[0]) - 1
                    tex_coord_index = int(vertex_parts[1]) - 1 if vertex_parts[1] else 0  # Учтем отсутствие текстурных координат
                    face.append((vertex_index, tex_coord_index))
                faces.append(face)

    model_data = {
        'name': model_name,
        'vertices': vertices,
        'faces': faces,
        'texture_file': texture_file,
        'tex_coords': tex_coords
    }

    models_data.append(model_data)

def import_obj_models_from_json(json_file):
    with open(json_file, 'r') as file:
        objects_data = json.load(file)

    for object_data in objects_data:
        model_file = object_data['model_file']
        texture_file = object_data['texture_file']
        object_name = object_data['object_name']

        import_obj_model(model_file, texture_file, object_name)

# Вызов функции для импорта моделей из objects.json
import_obj_models_from_json('objects.json')

# ручной импорт моделей
# import_obj_model('aircraft.obj', 'aircraft.png', 'tree')
import_obj_model('untitled.obj', 'texture.png', 'new_model')

# Вызываем функцию загрузки текстур при импорте модуля
load_textures()

