import uuid
from pathlib import Path

MAX_FILE_SIZE = 5_000_000
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
JPEG_SOI = b"\xff\xd8"
JPEG_EOI = b"\xff\xd9"


def sniff_image_type(data: bytes) -> str:
    """Определяем тип файла по magic bytes"""
    if data.startswith(PNG_SIGNATURE):
        return "image/png"
    if data.startswith(JPEG_SOI) and data.endswith(JPEG_EOI):
        return "image/jpeg"
    raise ValueError("Unsupported file type")


def secure_file_save(base_dir: str, data: bytes) -> str:
    """Безопасное сохранение файла с валидацией"""
    # Проверка размера
    if len(data) > MAX_FILE_SIZE:
        raise ValueError("File too large")

    # Проверка типа
    file_type = sniff_image_type(data)

    # Безопасный путь
    root = Path(base_dir).resolve(strict=True)
    ext = ".png" if file_type == "image/png" else ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    file_path = (root / filename).resolve()

    # Защита от path traversal
    if not str(file_path).startswith(str(root)):
        raise ValueError("Path traversal detected")

    # Защита от симлинков
    if any(part.is_symlink() for part in file_path.parents):
        raise ValueError("Symlink in path")

    # Сохранение
    file_path.write_bytes(data)
    return str(file_path)
