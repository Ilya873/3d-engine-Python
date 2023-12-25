import random
import json

def generate_models(grid_size_x=10, grid_size_y=1, grid_size_z=5):
    model_positions = []

    # Чтение данных из positions.json и преобразование их в model_positions
    def load_positions_data(json_file):
        try:
            with open(json_file, 'r') as json_file:
                positions_data = json.load(json_file)

            model_positions = []

            for pos_data in positions_data:
                x = pos_data['x']
                y = pos_data['y']
                z = pos_data['z']
                rotation_x = pos_data['rotation_x']
                rotation_y = pos_data['rotation_y']
                rotation_z = pos_data['rotation_z']
                model_name = pos_data['object_name']

                # Преобразуйте данные в нужный формат и добавьте в model_positions
                position = {'position': [x, y, z], 'rotation': [rotation_x, rotation_y, rotation_z], 'model_name': model_name}
                model_positions.append(position)

            return model_positions

        except FileNotFoundError:
            return []

    # Использование функции для загрузки данных из positions.json
    model_positions = load_positions_data('positions.json')

    # Создаем сетку блоков
    for x in range(grid_size_x):
        for y in range(grid_size_y):
            for z in range(grid_size_z):
                # Вычисляем координаты для блока в сетке
                position = (x * 2, y * 2, z * 2)  # Расстояние между блоками равно 2 (можете изменить по вашему усмотрению)
                # Выбираем случайную модель из model1, model2 и model3
                model_name = random.choice(['new_model', 'new_model', 'new_model'])
                model_positions.append({'position': position, 'model_name': model_name})

    return model_positions
