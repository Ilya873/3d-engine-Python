import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys
import math
from math import sqrt
import time
import json

# Инициализация Pygame
pygame.init()

# Измененные размеры окна для полноэкранного и оконного режимов
width, height = 1280, 800

# Установка атрибутов OpenGL
pygame.display.gl_set_attribute(GL_ACCUM_GREEN_SIZE, 8)  # Установим GL_ACCUM_GREEN_SIZE на 8
pygame.display.gl_set_attribute(GL_MULTISAMPLEBUFFERS, 1)
pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES, 4)

# Создание окна
pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL | HWSURFACE | RESIZABLE)
pygame.display.set_caption("Игра")

fullscreen = False  # По умолчанию начинаем не в полноэкранном режиме
cursor_visible = False

# Начальные параметры камеры
camera_pos = [0, -2, 0]  # Начальная позиция камеры
camera_speed = 0.1  # Скорость перемещения камеры
rotation_speed = 0.3  # Скорость вращения камеры

# Углы вращения камеры
yaw = 0
pitch = 0

# Импорт свойств моделей из models_properties.py
import models_properties
# Генерация позиций моделей с использованием функции из world_generator.py
import world_generator

models_positions = world_generator.generate_models()

# Включение теста глубины и сглаживания
glEnable(GL_DEPTH_TEST)
glEnable(GL_MULTISAMPLE)  # Включение сглаживания

# Load object scripts from JSON
with open('object_scripts.json', 'r') as f:
    object_scripts = json.load(f)

# Рендер текста
def render_text(text, x, y):
    font = pygame.font.Font(None, 36)
    text_surface = font.render(text, True, (255, 255, 255), (0, 0, 0, 0))  # Установка фонового цвета как (0, 0, 0, 0)
    text_data = pygame.image.tostring(text_surface, "RGBA", True)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, width, 0, height)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glRasterPos2f(x, y)
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    glPopMatrix()

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()

    glDisable(GL_BLEND)

# Измерение FPS
def fps_check():
    global last_time
    # Измерение и отображение FPS
    if 'last_time' not in globals():
        last_time = time.time()
    frame_time = time.time() - last_time
    last_time = time.time()

    # Проверка на ноль
    if frame_time > 0:
        fps = 1.0 / frame_time
    else:
        fps = float('inf')  # Если frame_time равен нулю, считаем FPS как бесконечность

    # Отобразить FPS или сообщение "N/A"
    if fps != float('inf'):
        fps_text = f"FPS: {int(fps)}"
    else:
        fps_text = "FPS: N/A"

    render_text(fps_text, 10, height - 40)

# Функция для проверки столкновений между камерой и кубами
def check_collisions(camera_pos, model_positions):
    camera_x, camera_y, camera_z = camera_pos
    camera_radius = 0.2  # Радиус столкновения камеры

    for model_position_data in model_positions:
        position = model_position_data['position']
        model_name = model_position_data['model_name']

        # Найдите модель по имени
        for model_data in models_properties.models_data:
            if model_data['name'] == model_name:
                model_vertices = model_data['vertices']

                # Определите ограничивающий объем модели
                min_x, min_y, min_z = model_vertices[0]
                max_x, max_y, max_z = model_vertices[0]

                for vertex in model_vertices:
                    vertex_x, vertex_y, vertex_z = vertex
                    min_x = min(min_x, vertex_x)
                    min_y = min(min_y, vertex_y)
                    min_z = min(min_z, vertex_z)
                    max_x = max(max_x, vertex_x)
                    max_y = max(max_y, vertex_y)
                    max_z = max(max_z, vertex_z)

                # Проверяем столкновение камеры с ограничивающим объемом модели
                if (camera_x + camera_radius >= min_x + position[0] and
                    camera_x - camera_radius <= max_x + position[0] and
                    camera_y + camera_radius >= min_y + position[1] and
                    camera_y - camera_radius <= max_y + position[1] and
                    camera_z + camera_radius >= min_z + position[2] and
                    camera_z - camera_radius <= max_z + position[2]):
                    return True  # Столкновение обнаружено

    return False  # Столкновений не обнаружено

# Открываем файл "game_options.json" для чтения
with open('game_options.json', 'r') as json_file:
    game_options = json.load(json_file)

# Доступ к переменным из JSON файла:
view_distance = game_options["view_distance"] # Максимальное расстояние видимости
fog_start_distance = game_options["fog_start_distance"] # Расстояние, на котором начинается туман
fog_depth = game_options["fog_depth"] # Глубина тумана

# Включение режима тумана
glEnable(GL_FOG)
glFogi(GL_FOG_MODE, GL_LINEAR)  # Линейный туман
glFogf(GL_FOG_START, fog_start_distance)  # Расстояние, на котором начинается туман
glFogf(GL_FOG_END, fog_start_distance+fog_depth)  # Расстояние, на котором туман полностью затеняет объекты
glFogfv(GL_FOG_COLOR, (0.7, 0.7, 1.0, 1.0))  # Цвет тумана
glClearColor(0.6, 0.7, 1.0, 1.0)

def create_display_list(model_data):
    display_list = glGenLists(1)
    glNewList(display_list, GL_COMPILE)
    glBindTexture(GL_TEXTURE_2D, model_data['texture_id'])

    for face in model_data['faces']:
        glBegin(GL_POLYGON)
        for vertex_index, tex_coord_index in face:
            vertex = model_data['vertices'][vertex_index]
            tex_coord = model_data['tex_coords'][tex_coord_index]
            glTexCoord2fv(tex_coord)
            glVertex3fv(vertex)
        glEnd()

    glEndList()
    return display_list

def get_model_by_name(model_name):
    for model_data in models_properties.models_data:
        if model_data['name'] == model_name:
            return model_data
    return None  # Возвращаем None, если модель не найдена


def draw_models(models_positions, camera_pos):
    glEnable(GL_TEXTURE_2D)
    for model_position_data in models_positions:
        position = model_position_data['position']
        model_name = model_position_data['model_name']
        distance = sqrt((camera_pos[0] - position[0]) ** 2 + (camera_pos[1] - position[1]) ** 2 + (camera_pos[2] - position[2]) ** 2)

        if distance <= view_distance:
            if distance <= fog_start_distance:
                glFogf(GL_FOG_START, fog_start_distance)
                glFogf(GL_FOG_END, fog_start_distance+fog_depth)
            else:
                glFogf(GL_FOG_START, fog_start_distance)
                glFogf(GL_FOG_END, fog_start_distance+fog_depth)

            model_data = get_model_by_name(model_name)
            if model_data:
                if 'display_list' not in model_data:
                    model_data['display_list'] = create_display_list(model_data)

                glPushMatrix()
                glTranslatef(-position[0], -position[1], -position[2])
                glCallList(model_data['display_list'])
                glPopMatrix()

    glDisable(GL_TEXTURE_2D)

# Основной цикл программы
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == K_F10:
                fullscreen = not fullscreen
                if fullscreen:
                    width, height = pygame.display.list_modes()[0]
                    pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL | HWSURFACE | FULLSCREEN | RESIZABLE)
                else:
                    width, height = 1280, 800
                    pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL | HWSURFACE | RESIZABLE)
                # Обновляем glViewport с новым разрешением
                glViewport(0, 0, width, height)
            elif event.type == KEYDOWN:
                if event.key == K_F9:
                    cursor_visible = not cursor_visible  # Инвертируем состояние курсора
                    pygame.mouse.set_pos(width // 2, height // 2)

        pygame.mouse.set_visible(cursor_visible)  # Устанавливаем видимость курсора в зависимости от состояния

    # Обработка управления камерой
    keys = pygame.key.get_pressed()

    # Вычисление вектора направления движения относительно ориентации камеры
    forward = [
        -math.sin(math.radians(yaw)),
        math.sin(math.radians(pitch)),
        -math.cos(math.radians(yaw))
    ]

    # Нормализация вектора направления
    length = math.sqrt(forward[0] ** 2 + forward[1] ** 2 + forward[2] ** 2)
    forward = [x / length for x in forward]

    # Сохраняем текущую позицию камеры в случае столкновения
    old_camera_pos = camera_pos.copy()

    if keys[pygame.K_w]:
        camera_pos[0] -= forward[0] * camera_speed
        camera_pos[1] -= forward[1] * camera_speed
        camera_pos[2] -= forward[2] * camera_speed
    if keys[pygame.K_s]:
        camera_pos[0] += forward[0] * camera_speed
        camera_pos[1] += forward[1] * camera_speed
        camera_pos[2] += forward[2] * camera_speed
    if keys[pygame.K_a]:
        strafe = math.degrees(math.atan2(forward[2], forward[0])) + 90
        strafe_rad = math.radians(strafe)
        camera_pos[0] += math.cos(strafe_rad) * camera_speed
        camera_pos[2] += math.sin(strafe_rad) * camera_speed
    if keys[pygame.K_d]:
        strafe = math.degrees(math.atan2(forward[2], forward[0])) + 90
        strafe_rad = math.radians(strafe)
        camera_pos[0] -= math.cos(strafe_rad) * camera_speed
        camera_pos[2] -= math.sin(strafe_rad) * camera_speed

    # Проверяем столкновения и возвращаем камеру на предыдущую позицию при столкновении
    if check_collisions(camera_pos, models_positions):
        camera_pos = old_camera_pos

    # Обработка вращения камеры с помощью мыши
    dx, dy = pygame.mouse.get_rel()
    yaw += -dx * rotation_speed
    pitch += -dy * rotation_speed

    # Установка позиции курсора в центр окна
    if cursor_visible == False:
        # Обновление позиции курсора
        cursor_x, cursor_y = pygame.mouse.get_pos()

        # Проверка расстояния между текущей позицией курсора и центром экрана
        distance_to_center = pygame.math.Vector2(cursor_x - width // 2, cursor_y - height // 2).length()

        # Если расстояние больше ширины экрана - 100, установите курсор в центр экрана
        if distance_to_center > width - 100 - width / 2:
            pygame.mouse.set_pos(width // 2, height // 2)

    # Очистка экрана и буфера глубины
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    fps_check()

    # Установка матрицы проекции
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # Пересчет aspect_ratio в зависимости от текущего режима
    aspect_ratio = width / height
    gluPerspective(60, aspect_ratio, 0.1, 100.0)  # Используем gluPerspective для установки перспективы

    # Установка матрицы модели и вида с учетом положения и ориентации камеры
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glRotatef(-pitch, 1, 0, 0)  # Вращение камеры по оси X
    glRotatef(-yaw, 0, 1, 0)  # Вращение камеры по оси Y
    glTranslatef(*camera_pos)  # Перемещение камеры

    # Включение отсечения невидимых граней
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    # Отрисовка моделей
    draw_models(models_positions, camera_pos)
    # Выключение отсечения невидимых граней
    glDisable(GL_CULL_FACE)

    # Execute scripts (simplified example, integrate this into your game loop or appropriate location)
    for obj, script in object_scripts.items():
        exec(script, None, {'models_positions': models_positions})

    # Обновление экрана
    pygame.display.flip()
    pygame.time.wait(10)
