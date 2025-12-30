"""Tests for ColorExtractor module."""
import os
import tempfile
import math
import pytest
from PIL import Image
from hypothesis import given, strategies as st, settings

from src.core.extractor import ColorExtractor
from src.core.models import ColorCategory, ColorExtractionResult, ColorInfo


# =============================================================================
# Property-Based Tests
# =============================================================================

# Feature: image-color-classifier, Property 2: 颜色提取一致性
# Validates: Requirements 2.1


def euclidean_distance(rgb1: tuple[int, int, int], rgb2: tuple[int, int, int]) -> float:
    """Calculate Euclidean distance between two RGB colors."""
    return math.sqrt(
        (rgb1[0] - rgb2[0]) ** 2 +
        (rgb1[1] - rgb2[1]) ** 2 +
        (rgb1[2] - rgb2[2]) ** 2
    )


@st.composite
def solid_color_strategy(draw):
    """
    Generate a random solid RGB color.
    Returns a tuple (r, g, b) with values 0-255.
    """
    r = draw(st.integers(min_value=0, max_value=255))
    g = draw(st.integers(min_value=0, max_value=255))
    b = draw(st.integers(min_value=0, max_value=255))
    return (r, g, b)


class TestColorExtractorProperties:
    """Property-based tests for ColorExtractor class."""
    
    @given(color=solid_color_strategy())
    @settings(max_examples=100, deadline=None)
    def test_color_extraction_consistency_for_solid_colors(self, color, tmp_path_factory):
        """
        Property 2: 颜色提取一致性
        
        For any pure color (solid color) image, the color extractor should return
        a dominant color that is within a Euclidean distance threshold (50) from
        the actual image color in RGB space.
        
        Validates: Requirements 2.1
        """
        # Create a unique temp directory for this test run
        tmp_path = tmp_path_factory.mktemp("extractor_test")
        
        # Create a solid color image
        img_path = tmp_path / "solid_color.png"
        img = Image.new('RGB', (100, 100), color=color)
        img.save(str(img_path))
        
        # Extract colors using ColorExtractor
        extractor = ColorExtractor(n_colors=3)
        result = extractor.extract_colors(str(img_path))
        
        # Get the dominant color (first color in sorted list, highest percentage)
        assert len(result.colors) > 0, "Should extract at least one color"
        dominant_color = result.colors[0]
        
        # Property: The extracted dominant color should be close to the actual color
        # For a solid color image, the distance should be very small (threshold: 50)
        distance = euclidean_distance(color, dominant_color.rgb)
        
        assert distance < 50, \
            f"Extracted color {dominant_color.rgb} is too far from actual color {color}. " \
            f"Distance: {distance:.2f}, threshold: 50"


# Feature: image-color-classifier, Property 3: 颜色占比完整性
# Validates: Requirements 2.2


@st.composite
def multi_color_image_strategy(draw):
    """
    Generate a random multi-color image configuration.
    Returns a list of (color, region_percentage) tuples that sum to 100%.
    """
    # Generate 2-5 colors for the image
    num_colors = draw(st.integers(min_value=2, max_value=5))
    
    colors = []
    for _ in range(num_colors):
        r = draw(st.integers(min_value=0, max_value=255))
        g = draw(st.integers(min_value=0, max_value=255))
        b = draw(st.integers(min_value=0, max_value=255))
        colors.append((r, g, b))
    
    return colors


class TestColorPercentageProperties:
    """Property-based tests for color percentage completeness."""
    
    @given(colors=multi_color_image_strategy())
    @settings(max_examples=100, deadline=None)
    def test_color_percentage_sum_equals_100(self, colors, tmp_path_factory):
        """
        Property 3: 颜色占比完整性
        
        For any image's color extraction result, the sum of all extracted color
        percentages should equal 100% (with a floating point tolerance of ±0.01).
        
        Validates: Requirements 2.2
        """
        # Create a unique temp directory for this test run
        tmp_path = tmp_path_factory.mktemp("percentage_test")
        
        # Create a multi-color image with horizontal stripes
        img_width, img_height = 100, 100
        img = Image.new('RGB', (img_width, img_height))
        pixels = img.load()
        
        # Divide image into horizontal stripes of different colors
        stripe_height = img_height // len(colors)
        for y in range(img_height):
            color_idx = min(y // stripe_height, len(colors) - 1)
            for x in range(img_width):
                pixels[x, y] = colors[color_idx]
        
        img_path = tmp_path / "multi_color.png"
        img.save(str(img_path))
        
        # Extract colors using ColorExtractor
        extractor = ColorExtractor(n_colors=3)
        result = extractor.extract_colors(str(img_path))
        
        # Property: Sum of all color percentages should equal 100%
        total_percentage = sum(color.percentage for color in result.colors)
        
        # Allow floating point tolerance of ±0.01 (as specified in design doc)
        assert abs(total_percentage - 100.0) <= 0.01, \
            f"Color percentages sum to {total_percentage:.4f}%, expected 100% (±0.01). " \
            f"Colors: {[(c.rgb, c.percentage) for c in result.colors]}"


# Feature: image-color-classifier, Property 4: 颜色分类确定性
# Validates: Requirements 2.3

# Get all valid color category values for validation
VALID_COLOR_CATEGORIES = {category.value for category in ColorCategory}


@st.composite
def rgb_color_strategy(draw):
    """
    Generate a random RGB color tuple.
    Returns a tuple (r, g, b) with values 0-255.
    """
    r = draw(st.integers(min_value=0, max_value=255))
    g = draw(st.integers(min_value=0, max_value=255))
    b = draw(st.integers(min_value=0, max_value=255))
    return (r, g, b)


class TestColorClassificationDeterminism:
    """Property-based tests for color classification determinism."""
    
    @given(rgb=rgb_color_strategy())
    @settings(max_examples=100, deadline=None)
    def test_classify_color_returns_valid_category(self, rgb):
        """
        Property 4: 颜色分类确定性 - Part 1
        
        For any RGB color value, the classify_color function should always
        return a valid color category from the predefined set.
        
        Validates: Requirements 2.3
        """
        extractor = ColorExtractor()
        category = extractor.classify_color(rgb)
        
        # Property: The returned category must be a valid color category
        assert category in VALID_COLOR_CATEGORIES, \
            f"classify_color({rgb}) returned '{category}' which is not a valid category. " \
            f"Valid categories: {VALID_COLOR_CATEGORIES}"
    
    @given(rgb=rgb_color_strategy())
    @settings(max_examples=100, deadline=None)
    def test_classify_color_is_idempotent(self, rgb):
        """
        Property 4: 颜色分类确定性 - Part 2
        
        For any RGB color value, calling classify_color multiple times with
        the same input should always return the same category (idempotence).
        
        Validates: Requirements 2.3
        """
        extractor = ColorExtractor()
        
        # Call classify_color multiple times with the same RGB value
        result1 = extractor.classify_color(rgb)
        result2 = extractor.classify_color(rgb)
        result3 = extractor.classify_color(rgb)
        
        # Property: All calls should return the same result (idempotence)
        assert result1 == result2 == result3, \
            f"classify_color({rgb}) is not idempotent. " \
            f"Results: {result1}, {result2}, {result3}"
