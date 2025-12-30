"""Tests for ImageScanner module."""
import os
import tempfile
import pytest
from PIL import Image
from hypothesis import given, strategies as st, settings

from src.core.scanner import ImageScanner, PathNotFoundError, AccessDeniedError
from src.core.models import ScanResult


class TestImageScanner:
    """Unit tests for ImageScanner class."""
    
    def test_scan_empty_directory(self, tmp_path):
        """Test scanning an empty directory returns empty result."""
        scanner = ImageScanner()
        result = scanner.scan(str(tmp_path))
        
        assert isinstance(result, ScanResult)
        assert result.total_count == 0
        assert len(result.image_paths) == 0
        assert result.skipped_count == 0
    
    def test_scan_nonexistent_path(self):
        """Test scanning a non-existent path raises PathNotFoundError."""
        scanner = ImageScanner()
        
        with pytest.raises(PathNotFoundError) as exc_info:
            scanner.scan("/nonexistent/path/that/does/not/exist")
        
        assert "nonexistent" in str(exc_info.value.path)
    
    def test_scan_finds_supported_formats(self, tmp_path):
        """Test scanner finds all supported image formats."""
        scanner = ImageScanner()
        
        # Create test images for each supported format
        for ext in ['.jpg', '.png', '.bmp', '.gif']:
            img = Image.new('RGB', (10, 10), color='red')
            img_path = tmp_path / f"test_image{ext}"
            img.save(str(img_path))
        
        result = scanner.scan(str(tmp_path))
        
        assert result.total_count == 4
        assert len(result.image_paths) == 4
    
    def test_scan_ignores_non_image_files(self, tmp_path):
        """Test scanner ignores non-image files."""
        scanner = ImageScanner()
        
        # Create a valid image
        img = Image.new('RGB', (10, 10), color='blue')
        img.save(str(tmp_path / "valid.png"))
        
        # Create non-image files
        (tmp_path / "text.txt").write_text("hello")
        (tmp_path / "data.json").write_text("{}")
        
        result = scanner.scan(str(tmp_path))
        
        assert result.total_count == 1
        assert len(result.image_paths) == 1
    
    def test_scan_recursive(self, tmp_path):
        """Test scanner recursively scans subdirectories."""
        scanner = ImageScanner()
        
        # Create nested directory structure
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        
        # Create images in both directories
        img = Image.new('RGB', (10, 10), color='green')
        img.save(str(tmp_path / "root.png"))
        img.save(str(subdir / "nested.png"))
        
        result = scanner.scan(str(tmp_path))
        
        assert result.total_count == 2
        assert len(result.image_paths) == 2
    
    def test_scan_handles_corrupted_images(self, tmp_path):
        """Test scanner handles corrupted image files gracefully."""
        scanner = ImageScanner()
        
        # Create a valid image
        img = Image.new('RGB', (10, 10), color='yellow')
        img.save(str(tmp_path / "valid.png"))
        
        # Create a corrupted "image" file
        corrupted = tmp_path / "corrupted.png"
        corrupted.write_bytes(b"not a valid image content")
        
        result = scanner.scan(str(tmp_path))
        
        assert result.total_count == 1
        assert result.skipped_count == 1
        assert len(result.error_files) == 1
        assert "corrupted.png" in result.error_files[0]
    
    def test_is_valid_image_returns_true_for_valid(self, tmp_path):
        """Test is_valid_image returns True for valid images."""
        scanner = ImageScanner()
        
        img = Image.new('RGB', (10, 10), color='purple')
        img_path = tmp_path / "valid.png"
        img.save(str(img_path))
        
        assert scanner.is_valid_image(str(img_path)) is True
    
    def test_is_valid_image_returns_false_for_invalid(self, tmp_path):
        """Test is_valid_image returns False for invalid files."""
        scanner = ImageScanner()
        
        # Non-existent file
        assert scanner.is_valid_image("/nonexistent/file.png") is False
        
        # Non-image file with image extension
        fake_img = tmp_path / "fake.png"
        fake_img.write_text("not an image")
        assert scanner.is_valid_image(str(fake_img)) is False
    
    def test_is_valid_image_returns_false_for_unsupported_format(self, tmp_path):
        """Test is_valid_image returns False for unsupported formats."""
        scanner = ImageScanner()
        
        # Create a text file with unsupported extension
        txt_file = tmp_path / "file.txt"
        txt_file.write_text("hello")
        
        assert scanner.is_valid_image(str(txt_file)) is False
    
    def test_supported_formats_constant(self):
        """Test SUPPORTED_FORMATS contains expected formats."""
        scanner = ImageScanner()
        
        expected = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
        assert set(scanner.SUPPORTED_FORMATS) == expected


# =============================================================================
# Property-Based Tests
# =============================================================================

# Feature: image-color-classifier, Property 1: 扫描结果完整性
# Validates: Requirements 1.1, 1.2

# Strategy to generate valid file extensions (supported and unsupported)
SUPPORTED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']
UNSUPPORTED_EXTENSIONS = ['.txt', '.pdf', '.doc', '.mp3', '.mp4', '.zip', '.py', '.html']

@st.composite
def file_structure_strategy(draw):
    """
    Generate a random file structure with a mix of supported and unsupported files.
    Returns a dict with:
    - supported_files: list of (filename, extension) tuples for image files
    - unsupported_files: list of (filename, extension) tuples for non-image files
    """
    # Generate random number of supported image files (0-10)
    num_supported = draw(st.integers(min_value=0, max_value=10))
    supported_files = []
    for i in range(num_supported):
        ext = draw(st.sampled_from(SUPPORTED_EXTENSIONS))
        filename = f"image_{i}{ext}"
        supported_files.append((filename, ext))
    
    # Generate random number of unsupported files (0-5)
    num_unsupported = draw(st.integers(min_value=0, max_value=5))
    unsupported_files = []
    for i in range(num_unsupported):
        ext = draw(st.sampled_from(UNSUPPORTED_EXTENSIONS))
        filename = f"other_{i}{ext}"
        unsupported_files.append((filename, ext))
    
    return {
        'supported_files': supported_files,
        'unsupported_files': unsupported_files
    }


class TestImageScannerProperties:
    """Property-based tests for ImageScanner class."""
    
    @given(file_structure=file_structure_strategy())
    @settings(max_examples=100, deadline=None)
    def test_scan_returns_only_supported_formats(self, file_structure, tmp_path_factory):
        """
        Property 1: 扫描结果完整性
        
        For any directory structure containing image files, the scanner should:
        1. Only return files with supported formats (jpg, jpeg, png, bmp, gif, webp)
        2. Include all valid image files in the directory (no omissions)
        
        Validates: Requirements 1.1, 1.2
        """
        # Create a unique temp directory for this test run
        tmp_path = tmp_path_factory.mktemp("scan_test")
        scanner = ImageScanner()
        
        created_supported_paths = []
        
        # Create supported image files (actual valid images)
        for filename, ext in file_structure['supported_files']:
            file_path = tmp_path / filename
            # Create a minimal valid image
            img = Image.new('RGB', (10, 10), color='red')
            img.save(str(file_path))
            created_supported_paths.append(str(file_path))
        
        # Create unsupported files
        for filename, ext in file_structure['unsupported_files']:
            file_path = tmp_path / filename
            file_path.write_text("non-image content")
        
        # Perform scan
        result = scanner.scan(str(tmp_path))
        
        # Property 1a: All returned paths should have supported extensions
        for path in result.image_paths:
            ext = os.path.splitext(path)[1].lower()
            assert ext in SUPPORTED_EXTENSIONS, \
                f"Returned path {path} has unsupported extension {ext}"
        
        # Property 1b: All created supported files should be in the result (completeness)
        # Note: We compare sets of normalized paths
        returned_paths_set = set(os.path.normpath(p) for p in result.image_paths)
        expected_paths_set = set(os.path.normpath(p) for p in created_supported_paths)
        
        assert returned_paths_set == expected_paths_set, \
            f"Missing files: {expected_paths_set - returned_paths_set}, " \
            f"Extra files: {returned_paths_set - expected_paths_set}"
        
        # Property 1c: Count should match
        assert result.total_count == len(file_structure['supported_files']), \
            f"Expected {len(file_structure['supported_files'])} files, got {result.total_count}"
