import sys
import os
import json
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QListWidget
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTextEdit, QPushButton

class ModelObjectEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Добавление объектов")
        self.setGeometry(100, 100, 400, 400)

        self.object_list = QListWidget(self)
        self.object_list.setGeometry(10, 10, 380, 200)

        self.add_button = QPushButton("Добавить объект", self)
        self.add_button.setGeometry(10, 220, 150, 30)
        self.add_button.clicked.connect(self.add_object)

        self.remove_button = QPushButton("Удалить объект", self)
        self.remove_button.setGeometry(170, 220, 150, 30)
        self.remove_button.clicked.connect(self.remove_object)

        self.model_file_label = QLabel("Файл модели:", self)
        self.model_file_label.setGeometry(10, 260, 150, 30)

        self.model_file_input = QLineEdit(self)
        self.model_file_input.setGeometry(170, 260, 220, 30)

        self.texture_file_label = QLabel("Файл текстуры:", self)
        self.texture_file_label.setGeometry(10, 300, 150, 30)

        self.texture_file_input = QLineEdit(self)
        self.texture_file_input.setGeometry(170, 300, 220, 30)

        self.object_name_label = QLabel("Имя объекта:", self)
        self.object_name_label.setGeometry(10, 340, 150, 30)

        self.object_name_input = QLineEdit(self)
        self.object_name_input.setGeometry(170, 340, 220, 30)
        # Создаем кнопку "Сохранить" и подключаем к ней метод сохранения
        self.save_button = QPushButton("Сохранить", self)
        self.save_button.setGeometry(10, 380, 150, 30)
        self.save_button.clicked.connect(self.save_edited_item)

        # Загрузка данных из objects.json
        self.load_objects_data()

        # Подключаем метод edit_item к событию выбора элемента в списке
        self.object_list.itemClicked.connect(self.edit_item)

    def add_object(self):
        model_file = self.model_file_input.text()
        texture_file = self.texture_file_input.text()
        object_name = self.object_name_input.text()

        if model_file and texture_file and object_name:
            item_text = f"Файл модели: {model_file}, Файл текстуры: {texture_file}, Имя объекта: {object_name}"
            self.object_list.addItem(item_text)

            # Сохранение данных в objects.json
            self.save_objects_data()

    def remove_object(self):
        selected_items = self.object_list.selectedItems()
        for item in selected_items:
            self.object_list.takeItem(self.object_list.row(item))

        # Сохранение данных в objects.json после удаления
        self.save_objects_data()

    def edit_item(self):
        selected_item = self.object_list.currentItem()  # Получаем выбранный элемент списка
        if selected_item is not None:
            item_text = selected_item.text()  # Получаем текст выбранного элемента
            parts = item_text.split(", ")
            model_file = parts[0].split(": ")[1]
            texture_file = parts[1].split(": ")[1]
            object_name = parts[2].split(": ")[1]

            # Заполняем поля данными выбранной строки
            self.model_file_input.setText(model_file)
            self.texture_file_input.setText(texture_file)
            self.object_name_input.setText(object_name)

            # Сохраняем выбранный элемент для последующего редактирования
            self.current_item = selected_item

    def save_edited_item(self):
        if hasattr(self, 'current_item') and self.current_item is not None:
            # Получаем индекс выбранного элемента
            index = self.object_list.indexFromItem(self.current_item).row()

            # Получаем новые значения из полей
            model_file = self.model_file_input.text()
            texture_file = self.texture_file_input.text()
            object_name = self.object_name_input.text()

            # Обновляем текст выбранного элемента
            new_item_text = f"Файл модели: {model_file}, Файл текстуры: {texture_file}, Имя объекта: {object_name}"
            self.current_item.setText(new_item_text)

            # Очищаем поля
            self.model_file_input.clear()
            self.texture_file_input.clear()
            self.object_name_input.clear()

            # Сохраняем измененные данные в файл
            self.save_objects_data()

    def save_objects_data(self):
        objects_data = []
        for index in range(self.object_list.count()):
            item_text = self.object_list.item(index).text()
            parts = item_text.split(", ")
            model_file = parts[0].split(": ")[1]
            texture_file = parts[1].split(": ")[1]
            object_name = parts[2].split(": ")[1]
            objects_data.append({'model_file': model_file, 'texture_file': texture_file, 'object_name': object_name})

        with open('objects.json', 'w') as json_file:
            json.dump(objects_data, json_file)

    def load_objects_data(self):
        try:
            with open('objects.json', 'r') as json_file:
                objects_data = json.load(json_file)

            self.object_list.clear()
            for obj_data in objects_data:
                model_file = obj_data['model_file']
                texture_file = obj_data['texture_file']
                object_name = obj_data['object_name']

                item_text = f"Файл модели: {model_file}, Файл текстуры: {texture_file}, Имя объекта: {object_name}"
                self.object_list.addItem(item_text)
        except FileNotFoundError:
            pass

class ModelPositionEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        # Dictionary to store object scripts
        self.object_scripts = {}

        # Загрузка сохраненных скриптов из JSON-файла
        try:
            with open('object_scripts.json', 'r') as f:
                self.object_scripts = json.load(f)
        except FileNotFoundError:
            self.object_scripts = {}  # Если файл не найден, инициализируем пустым словарем

    def initUI(self):
        self.setWindowTitle("Добавление позиций объектов")
        self.setGeometry(550, 100, 800, 450)

        self.position_list = QListWidget(self)
        self.position_list.setGeometry(10, 10, 380, 200)

        self.add_button = QPushButton("Добавить позицию", self)
        self.add_button.setGeometry(10, 220, 150, 30)
        self.add_button.clicked.connect(self.add_position)

        self.remove_button = QPushButton("Удалить позицию", self)
        self.remove_button.setGeometry(170, 220, 150, 30)
        self.remove_button.clicked.connect(self.remove_position)

        self.x_label = QLabel("X:", self)
        self.x_label.setGeometry(10, 260, 20, 30)

        self.x_input = QLineEdit(self)
        self.x_input.setGeometry(30, 260, 50, 30)

        self.y_label = QLabel("Y:", self)
        self.y_label.setGeometry(90, 260, 20, 30)

        self.y_input = QLineEdit(self)
        self.y_input.setGeometry(110, 260, 50, 30)

        self.z_label = QLabel("Z:", self)
        self.z_label.setGeometry(170, 260, 20, 30)

        self.z_input = QLineEdit(self)
        self.z_input.setGeometry(190, 260, 50, 30)

        self.rotation_x_label = QLabel("Угол по X:", self)
        self.rotation_x_label.setGeometry(10, 300, 150, 30)

        self.rotation_x_input = QLineEdit(self)
        self.rotation_x_input.setGeometry(170, 300, 50, 30)

        self.rotation_y_label = QLabel("Угол по Y:", self)
        self.rotation_y_label.setGeometry(10, 340, 150, 30)

        self.rotation_y_input = QLineEdit(self)
        self.rotation_y_input.setGeometry(170, 340, 50, 30)

        self.rotation_z_label = QLabel("Угол по Z:", self)
        self.rotation_z_label.setGeometry(10, 380, 150, 30)

        self.rotation_z_input = QLineEdit(self)
        self.rotation_z_input.setGeometry(170, 380, 50, 30)

        self.object_name_label = QLabel("Имя объекта:", self)
        self.object_name_label.setGeometry(10, 420, 150, 30)

        self.object_name_input = QLineEdit(self)
        self.object_name_input.setGeometry(170, 420, 220, 30)

        # Создаем кнопку "Сохранить" и подключаем к ней метод сохранения
        self.save_button = QPushButton("Сохранить", self)
        self.save_button.setGeometry(10, 460, 150, 30)
        self.save_button.clicked.connect(self.save_edited_item)

        # Загрузка данных из positions.json
        self.load_positions_data()

        # Подключаем метод edit_item к событию выбора элемента в списке
        self.position_list.itemClicked.connect(self.edit_item)

        # Add a text field for script input
        self.script_input = QTextEdit(self)
        self.script_input.setGeometry(400, 10, 380, 200)

        # Add a button to save the script
        self.save_script_button = QPushButton("Сохранить скрипт", self)
        self.save_script_button.setGeometry(400, 220, 150, 30)
        self.save_script_button.clicked.connect(self.save_script)

    def save_script(self):
        # Get the selected object from the list
        if hasattr(self, 'current_item') and self.current_item is not None:
            item_text = self.current_item.text()
            object_name = item_text.split(", ")[6].split(": ")[1]

            # Save the script for the selected object
            self.object_scripts[object_name] = self.script_input.toPlainText()

            # Save to a JSON file
            with open('object_scripts.json', 'w') as f:
                json.dump(self.object_scripts, f)

    def add_position(self):
        x = self.x_input.text()
        y = self.y_input.text()
        z = self.z_input.text()
        rotation_x = self.rotation_x_input.text()
        rotation_y = self.rotation_y_input.text()
        rotation_z = self.rotation_z_input.text()
        object_name = self.object_name_input.text()

        if x and y and z and rotation_x and rotation_y and rotation_z and object_name:
            item_text = f"X: {x}, Y: {y}, Z: {z}, Угол по X: {rotation_x}, Угол по Y: {rotation_y}, Угол по Z: {rotation_z}, Имя объекта: {object_name}"
            self.position_list.addItem(item_text)

            # Сохранение данных в positions.json
            self.save_positions_data()

    def remove_position(self):
        selected_items = self.position_list.selectedItems()
        for item in selected_items:
            self.position_list.takeItem(self.position_list.row(item))

        # Сохранение данных в positions.json после удаления
        self.save_positions_data()

    def edit_item(self):
        selected_item = self.position_list.currentItem()  # Получаем выбранный элемент списка
        if selected_item is not None:
            item_text = selected_item.text()  # Получаем текст выбранного элемента
            parts = item_text.split(", ")
            x = parts[0].split(": ")[1]
            y = parts[1].split(": ")[1]
            z = parts[2].split(": ")[1]
            rotation_x = parts[3].split(": ")[1]
            rotation_y = parts[4].split(": ")[1]
            rotation_z = parts[5].split(": ")[1]
            object_name = parts[6].split(": ")[1]

            # Заполняем поля данными выбранной строки
            self.x_input.setText(x)
            self.y_input.setText(y)
            self.z_input.setText(z)
            self.rotation_x_input.setText(rotation_x)
            self.rotation_y_input.setText(rotation_y)
            self.rotation_z_input.setText(rotation_z)
            self.object_name_input.setText(object_name)

            # Загрузка скрипта для выбранного объекта
            if object_name in self.object_scripts:
                self.script_input.setPlainText(self.object_scripts[object_name])
            else:
                self.script_input.clear()

            # Сохраняем выбранный элемент для последующего редактирования
            self.current_item = selected_item

    def save_edited_item(self):
        if hasattr(self, 'current_item') and self.current_item is not None:
            # Получаем индекс выбранного элемента
            index = self.position_list.indexFromItem(self.current_item).row()

            # Получаем новые значения из полей
            x = self.x_input.text()
            y = self.y_input.text()
            z = self.z_input.text()
            rotation_x = self.rotation_x_input.text()
            rotation_y = self.rotation_y_input.text()
            rotation_z = self.rotation_z_input.text()
            object_name = self.object_name_input.text()

            # Обновляем текст выбранного элемента
            new_item_text = f"X: {x}, Y: {y}, Z: {z}, Угол по X: {rotation_x}, Угол по Y: {rotation_y}, Угол по Z: {rotation_z}, Имя объекта: {object_name}"
            self.current_item.setText(new_item_text)

            # Очищаем поля
            self.x_input.clear()
            self.y_input.clear()
            self.z_input.clear()
            self.rotation_x_input.clear()
            self.rotation_y_input.clear()
            self.rotation_z_input.clear()
            self.object_name_input.clear()

            # Сохраняем измененные данные в файл
            self.save_positions_data()

    def save_positions_data(self):
        positions_data = []
        for index in range(self.position_list.count()):
            item_text = self.position_list.item(index).text()
            parts = item_text.split(", ")
            x = float(parts[0].split(": ")[1])
            y = float(parts[1].split(": ")[1])
            z = float(parts[2].split(": ")[1])
            rotation_x = float(parts[3].split(": ")[1])
            rotation_y = float(parts[4].split(": ")[1])
            rotation_z = float(parts[5].split(": ")[1])
            object_name = parts[6].split(": ")[1]
            positions_data.append({
                'x': x,
                'y': y,
                'z': z,
                'rotation_x': rotation_x,
                'rotation_y': rotation_y,
                'rotation_z': rotation_z,
                'object_name': object_name
            })

        with open('positions.json', 'w') as json_file:
            json.dump(positions_data, json_file)

    def load_positions_data(self):
        try:
            with open('positions.json', 'r') as json_file:
                positions_data = json.load(json_file)

            self.position_list.clear()
            for pos_data in positions_data:
                x = pos_data['x']
                y = pos_data['y']
                z = pos_data['z']
                rotation_x = pos_data['rotation_x']
                rotation_y = pos_data['rotation_y']
                rotation_z = pos_data['rotation_z']
                object_name = pos_data['object_name']

                item_text = f"X: {x}, Y: {y}, Z: {z}, Угол по X: {rotation_x}, Угол по Y: {rotation_y}, Угол по Z: {rotation_z}, Имя объекта: {object_name}"
                self.position_list.addItem(item_text)
        except FileNotFoundError:
            pass

class ObjectEditorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Редактор объектов")
        self.setGeometry(100, 100, 800, 400)

        self.add_object_button = QPushButton("Добавить объекты", self)
        self.add_object_button.setGeometry(10, 10, 150, 30)
        self.add_object_button.clicked.connect(self.open_object_editor)

        self.add_position_button = QPushButton("Добавить позиции", self)
        self.add_position_button.setGeometry(170, 10, 150, 30)
        self.add_position_button.clicked.connect(self.open_position_editor)

        # Добавление полей ввода для Максимального расстояния видимости
        # Загрузка данных из файла "game_options.json" (если он существует)
        try:
            with open('game_options.json', 'r') as json_file:
                game_options_data = json.load(json_file)
        except FileNotFoundError:
            # Если файл не найден, установите значения по умолчанию
            game_options_data = {
                "view_distance": 20,
                "fog_start_distance": 10,
                "fog_depth": 5
            }
        self.view_distance_label = QLabel("Максимальное расстояние видимости:", self)
        self.view_distance_label.setGeometry(10, 50, 250, 30)

        self.view_distance_input = QLineEdit(self)
        self.view_distance_input.setGeometry(270, 50, 150, 30)
        self.view_distance_input.setText(str(game_options_data["view_distance"]))

        # Добавление полей ввода для Расстояния, на котором начинается туман
        self.fog_start_distance_label = QLabel("Расстояние, на котором начинается туман:", self)
        self.fog_start_distance_label.setGeometry(10, 90, 250, 30)

        self.fog_start_distance_input = QLineEdit(self)
        self.fog_start_distance_input.setGeometry(270, 90, 150, 30)
        self.fog_start_distance_input.setText(str(game_options_data["fog_start_distance"]))

        # Добавление полей ввода для Глубины тумана
        self.fog_depth_label = QLabel("Глубина тумана:", self)
        self.fog_depth_label.setGeometry(10, 130, 150, 30)

        self.fog_depth_input = QLineEdit(self)
        self.fog_depth_input.setGeometry(270, 130, 150, 30)
        self.fog_depth_input.setText(str(game_options_data["fog_depth"]))

        self.run_game_button = QPushButton("Запуск игры", self)
        self.run_game_button.setGeometry(10, 340, 320, 40)
        self.run_game_button.clicked.connect(self.run_game)

    def open_object_editor(self):
        self.object_editor = ModelObjectEditor()
        self.object_editor.show()

    def open_position_editor(self):
        self.position_editor = ModelPositionEditor()
        self.position_editor.show()

    def run_game(self):
        # Считываем значения из полей ввода
        view_distance = float(self.view_distance_input.text())
        fog_start_distance = float(self.fog_start_distance_input.text())
        fog_depth = int(self.fog_depth_input.text())
        # Создаем словарь с данными
        game_options = {
            "view_distance": view_distance,
            "fog_start_distance": fog_start_distance,
            "fog_depth": fog_depth
        }

        # Сохраняем данные в файл "game_options.json"
        with open('game_options.json', 'w') as json_file:
            json.dump(game_options, json_file)
        os.system('python main.py')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = ObjectEditorApp()
    mainWindow.show()
    sys.exit(app.exec_())
