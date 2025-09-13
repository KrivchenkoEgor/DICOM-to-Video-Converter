#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DICOM to Video Converter
Автоматически конвертирует серию DICOM-файлов (например, КТ) в видеофайл.
Поддерживает монохромные и цветные форматы. Всё приводится к grayscale для стабильности.
Видео сохраняется с именем, содержащим дату и время.
Автоматически устанавливает недостающие зависимости.
"""

import os
import sys
import subprocess
import importlib.util
import datetime
import cv2
import numpy as np
import pydicom
from pydicom.pixel_data_handlers.util import apply_voi_lut, apply_color_lut

# ========================
# ⚙️ ГЛОБАЛЬНЫЕ НАСТРОЙКИ
# ========================
DICOM_DIR = "CT_Series"        # Папка с DCM-файлами
FPS = 10                       # Кадров в секунду
USE_COLOR = False              # True — применить псевдоцвет (COLORMAP_JET), False — оставить grayscale

# ========================
# 🧰 ФУНКЦИЯ: проверка и установка зависимостей
# ========================
def install_package(package):
    """Установить пакет через pip, если он не установлен."""
    try:
        spec = importlib.util.find_spec(package.split('==')[0].split('>=')[0])
        if spec is None:
            print(f"📦 Устанавливаю отсутствующий пакет: {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} успешно установлен.")
        else:
            print(f"✅ {package} уже установлен.")
    except Exception as e:
        print(f"❌ Ошибка при установке {package}: {e}")
        sys.exit(1)

# Список необходимых пакетов
REQUIRED_PACKAGES = [
    "pydicom",
    "opencv-python",
    "numpy",
    "pylibjpeg",
    "pylibjpeg-libjpeg",
    "pylibjpeg-openjpeg",
    "pillow"
]

print("🔍 Проверка зависимостей...")
for package in REQUIRED_PACKAGES:
    install_package(package)

# Перезагружаем pydicom, если он был установлен в ходе выполнения
if importlib.util.find_spec("pydicom") is not None:
    import pydicom
    from pydicom.pixel_data_handlers.util import apply_voi_lut, apply_color_lut
else:
    print("❌ Не удалось импортировать pydicom после установки.")
    sys.exit(1)

print("✅ Все зависимости установлены.")

# ========================
# 📂 ЗАГРУЗКА И СОРТИРОВКА DICOM-ФАЙЛОВ
# ========================
print("\n📂 Чтение DICOM-файлов...")

if not os.path.exists(DICOM_DIR):
    raise FileNotFoundError(f"Папка '{DICOM_DIR}' не найдена. Создайте её и поместите туда .dcm файлы.")

files = [f for f in os.listdir(DICOM_DIR) if f.lower().endswith('.dcm')]
if not files:
    raise FileNotFoundError(f"В папке '{DICOM_DIR}' не найдено .dcm файлов.")

datasets = []
for f in files:
    filepath = os.path.join(DICOM_DIR, f)
    try:
        ds = pydicom.dcmread(filepath)
        datasets.append(ds)
    except Exception as e:
        print(f"⚠️  Не удалось прочитать файл {f}: {e}")

print(f"✅ Загружено {len(datasets)} DICOM-файлов.")

# ========================
# 🔢 СОРТИРОВКА ПО InstanceNumber или SliceLocation
# ========================
def sort_dicom_datasets(datasets):
    try:
        sorted_datasets = sorted(datasets, key=lambda x: int(x.InstanceNumber))
        print("✅ Отсортировано по InstanceNumber")
        return sorted_datasets
    except:
        try:
            sorted_datasets = sorted(datasets, key=lambda x: float(x.SliceLocation))
            print("✅ Отсортировано по SliceLocation")
            return sorted_datasets
        except:
            print("⚠️  Не удалось отсортировать по метаданным — используем исходный порядок.")
            return datasets

datasets = sort_dicom_datasets(datasets)

# ========================
# 🎥 ИНИЦИАЛИЗАЦИЯ ВИДЕО
# ========================
# Генерируем имя файла с датой и временем
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
OUTPUT_VIDEO = f"ct_scan_{timestamp}.mp4"

# ========================
# 🖼️ ОБРАБОТКА КАЖДОГО СРЕЗА
# ========================
print(f"\n🎬 Начинаем создание видео: {OUTPUT_VIDEO} ({FPS} FPS)...")

out = None  # VideoWriter будет инициализирован после первого кадра

for i, ds in enumerate(datasets):
    try:
        # Получаем тип изображения
        photometric_interpretation = ds.get("PhotometricInterpretation", "UNKNOWN")
        print(f"🖼️  Файл {i+1}: PhotometricInterpretation = {photometric_interpretation}")

        # Читаем пиксели
        pixel_array = ds.pixel_array

        # Обработка в зависимости от типа
        if photometric_interpretation in ['MONOCHROME1', 'MONOCHROME2']:
            img = apply_voi_lut(pixel_array, ds)
        elif photometric_interpretation == 'PALETTE COLOR':
            img = apply_color_lut(pixel_array, ds)
        elif photometric_interpretation in ['RGB', 'YBR_FULL', 'YBR_FULL_422', 'YBR_PARTIAL_422']:
            img = pixel_array
            if photometric_interpretation == 'YBR_FULL':
                img = cv2.cvtColor(img, cv2.COLOR_YCrCb2RGB)
            elif photometric_interpretation in ['YBR_FULL_422', 'YBR_PARTIAL_422']:
                img = cv2.cvtColor(img, cv2.COLOR_YUV2RGB_Y422)
        else:
            print(f"⚠️  Неизвестный тип '{photometric_interpretation}' — использую как есть.")
            img = pixel_array

        # ========================
        # 🔄 ПРИВЕДЕНИЕ К ЕДИНОМУ ФОРМАТУ: ВСЕГДА GRAYSCALE (для стабильности видео)
        # ========================
        if len(img.shape) == 3:
            if img.shape[2] == 3:
                img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)  # Конвертируем в grayscale
            elif img.shape[2] == 4:
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)

        # Нормализация в диапазон 0-255 (если ещё не uint8)
        if img.dtype != np.uint8:
            img_min, img_max = img.min(), img.max()
            if img_max != img_min:
                img = (img - img_min) / (img_max - img_min) * 255.0
            else:
                img = np.zeros_like(img)
            img = img.astype(np.uint8)

        # Применяем псевдоцвет, если включено
        is_color_frame = False
        if USE_COLOR:
            img = cv2.applyColorMap(img, cv2.COLORMAP_JET)
            is_color_frame = True

        # ========================
        # 📹 ИНИЦИАЛИЗАЦИЯ VideoWriter (первый кадр)
        # ========================
        if out is None:
            frame_height, frame_width = img.shape[:2]
            frame_size = (frame_width, frame_height)
            out = cv2.VideoWriter(OUTPUT_VIDEO, cv2.VideoWriter_fourcc(*'mp4v'), FPS, frame_size, isColor=is_color_frame)
            if not out.isOpened():
                raise Exception("❌ Не удалось создать VideoWriter. Проверьте права на запись и наличие кодека.")
            print(f"✅ VideoWriter инициализирован: {frame_size[0]}x{frame_size[1]}, цветное: {is_color_frame}")

        # Записываем кадр
        out.write(img)

        if (i + 1) % 50 == 0:
            print(f"   ✅ Обработано {i + 1} / {len(datasets)} кадров")

    except Exception as e:
        print(f"❌ Ошибка при обработке файла {i+1}: {e}")
        continue  # Пропускаем проблемный файл

# ========================
# 🧹 ЗАВЕРШЕНИЕ
# ========================
if out is not None:
    out.release()
    print(f"\n🎉 Видео успешно сохранено: {os.path.abspath(OUTPUT_VIDEO)}")
else:
    print("❌ Ни один кадр не был записан. Проверьте входные данные.")

print("✅ Конвертация завершена.")