# Image Color Classifier

[English](README.md) | [中文](README_zh.md)

A desktop app that automatically classifies photos by color. Built with Python and PyQt6.

## Features

- **Simple Mode**: Classify by dominant color (red, blue, green, etc.)
- **Advanced Mode**: Multi-dimensional color analysis with automatic clustering
- Undo/rollback support
- Preview before moving files

## Tech Stack

- Python 3.12
- PyQt6 (GUI)
- NumPy (computation)
- PIL/Pillow (image processing)

## Architecture

```
src/
├── core/           # Core logic
│   ├── advanced_extractor.py   # Feature extraction
│   ├── similarity_calculator.py # Distance metrics
│   ├── adaptive_clusterer.py   # Hierarchical clustering
│   ├── category_namer.py       # Auto naming
│   └── advanced_engine.py      # Main engine
├── ui/             # PyQt6 interface
└── main.py         # Entry point
```

## Advanced Mode Algorithm

The advanced classification works in 5 steps:

### 1. Feature Extraction
For each image:
- Convert to HSV and LAB color spaces
- Compute histograms: Hue (180 bins), Lightness (256 bins), Saturation (256 bins)
- Extract dominant colors using K-Means in LAB space
- Classify tonal range (high-key / mid-key / low-key)

### 2. Similarity Calculation
Compare images using histogram distance metrics:
- **Bhattacharyya distance**: measures overlap between distributions
- Weighted combination: Hue (40%) + Lightness (35%) + Saturation (25%)
- Build N×N distance matrix

### 3. Hierarchical Clustering
- Use Ward linkage method
- Auto-select optimal cluster count using silhouette score
- Or manually specify number of categories

### 4. Category Naming
Generate descriptive names based on cluster characteristics:
- Tonal: 高调 (high-key) / 中调 (mid-key) / 低调 (low-key)
- Hue: 暖色 (warm) / 冷色 (cool) / 中性 (neutral)
- Saturation: 鲜艳 (vivid) / 适中 (moderate) / 柔和 (muted)

Example: "高调暖色鲜艳" = bright, warm, vivid images

### 5. File Organization
Move images into folders named by their category.

## Usage

1. Select a folder containing images
2. Choose mode (Simple / Advanced)
3. Adjust settings if needed (cluster count, feature weights)
4. Click "Start Classification"
5. Preview results and confirm

## Build

```bash
pip install -r requirements.txt
pyinstaller build.spec
```

Output: `dist/ImageColorClassifier/`

## License

MIT
