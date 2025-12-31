# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# 只收集必要的 PyQt6 模块
pyqt6_hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'PyQt6.sip',
]

# sklearn 只收集必要的
sklearn_hiddenimports = [
    'sklearn.cluster', 
    'sklearn.cluster._kmeans', 
    'sklearn.cluster._k_means_common',
    'sklearn.utils._cython_blas',
    'sklearn.utils._typedefs',
]

a = Analysis(
    ['src/main.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('src/ui', 'ui'),
        ('src/core', 'core'),
    ],
    hiddenimports=pyqt6_hiddenimports + sklearn_hiddenimports + [
        'numpy', 
        'numpy.core._methods', 
        'numpy.lib.format',
        'PIL', 
        'PIL.Image', 
        'PIL._imaging',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['runtime_hook.py'],
    excludes=[
        'pytest', 'hypothesis', 'pytest_qt', '_pytest',
        'tkinter', 'matplotlib', 'IPython', 'jupyter', 'notebook',
        'torch', 'torchvision', 'tensorflow', 'keras',
        'pandas', 'sympy', 'sphinx', 'bokeh', 'plotly',
        'dask', 'distributed', 'numba', 'llvmlite',
        'PyQt5',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ImageColorClassifier',
    debug=False,
    strip=False,
    upx=False,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='ImageColorClassifier',
)
