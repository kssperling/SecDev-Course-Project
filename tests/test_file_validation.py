from pathlib import Path

import pytest

from app.file_validation import secure_file_save, sniff_image_type


class TestFileValidation:
    def test_sniff_png_type(self):
        """Проверка определения PNG по magic bytes"""
        png_data = b"\x89PNG\r\n\x1a\n" + b"fake_png_data"
        assert sniff_image_type(png_data) == "image/png"

    def test_sniff_jpeg_type(self):
        """Проверка определения JPEG"""
        jpeg_data = b"\xff\xd8" + b"fake_jpeg_data" + b"\xff\xd9"
        assert sniff_image_type(jpeg_data) == "image/jpeg"

    def test_reject_unsupported_type(self):
        """Негативный тест: неподдерживаемый тип"""
        with pytest.raises(ValueError, match="Unsupported file type"):
            sniff_image_type(b"invalid_file_data")

    def test_reject_large_file(self, tmp_path):
        """Негативный тест: файл слишком большой"""
        large_data = b"\x89PNG\r\n\x1a\n" + b"x" * 5_000_001
        with pytest.raises(ValueError, match="File too large"):
            secure_file_save(str(tmp_path), large_data)

    def test_safe_filename_generation(self, tmp_path):
        """Проверка безопасного генерации имени файла"""
        png_data = b"\x89PNG\r\n\x1a\n" + b"test_data"
        saved_path = secure_file_save(str(tmp_path), png_data)

        # Проверяем что имя файла - UUID
        filename = Path(saved_path).name
        assert filename.endswith(".png")
        assert len(filename) == 36 + 4  # UUID + .png
