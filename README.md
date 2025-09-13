# 🎥 DICOM to Video Converter

> **Конвертируй серии DICOM-файлов (например, КТ или МРТ) в видеофайл одним запуском скрипта.**

Автоматически обрабатывает монохромные (`MONOCHROME2`) и цветные (`YBR_FULL`, `RGB`, `PALETTE COLOR`) DICOM-изображения.  
Приводит всё к единому формату → **никаких ошибок, никаких пропущенных кадров**.  
Видео сохраняется с именем, содержащим дату и время — удобно для архива.  
**Самоустанавливающийся скрипт — просто запусти, всё остальное он сделает за тебя.**

---

## 🖼️ Пример результата

Видео из 408 срезов КТ, конвертированных в MP4:

📹 [Скачать пример видео (placeholder)](https://example.com/ct_scan_2025-04-05_14-30-22.mp4)  


## 🚀 Как использовать

### 1. Клонируй репозиторий

```bash
git clone https://github.com/KrivchenkoEgor/DICOM-to-Video-Converter.git
cd DICOM-to-Video-Converter

📦 Требования
Скрипт сам установит всё необходимое, но вот что используется под капотом:

Python 3.7+
pydicom — для чтения DICOM
opencv-python — для создания видео
numpy — для работы с массивами
pylibjpeg, pylibjpeg-libjpeg, pylibjpeg-openjpeg — для декодирования сжатых DICOM
pillow — дополнительная поддержка форматов

Сделано с ❤️ для радиологов, исследователей и инженеров медицинской визуализации.

# 🎥 DICOM to Video Converter

> **Convert a series of DICOM files (for example, CT or MRI) into a video file with one run of the script.**

Automatically processes monochrome (`MONOCHROME2') and color (`YBR_FULL`, `RGB`, `PALETTE COLOR`) DICOM images.  
Brings everything to a single format → **no errors, no missed frames**.  
The video is saved with a name containing the date and time, which is convenient for archiving.  
**Self—installing script - just run it, it will do the rest for you.**

---

## 🖼️ Result example

Video of 408 CT slices converted to MP4:

[Download sample video (placeholder)](https://example.com/ct_scan_2025-04-05_14-30-22.mp4 )  


## 🚀 How to use

### 1. Clone the repository

```bash
git clone https://github.com/KrivchenkoEgor/DICOM-to-Video-Converter.git
cd DICOM-to-Video-Converter

📦 Requirements
The script will install everything you need by itself, but here's what's used under the hood:

Python 3.7+
pydicom — for DICOM reading
opencv-python — for video creation
numpy — for working with arrays
pylibjpeg, pylibjpeg-libjpeg, pylibjpeg-openjpeg — for decoding compressed DICOM
pillow — additional format support

Made with ❤️ for radiologists, researchers and medical imaging engineers.

