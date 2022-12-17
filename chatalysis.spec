# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

data_files = [
    ("resources/images", "resources/images"),
    ("resources/templates", "resources/templates")
]

a = Analysis(
    ['chatalysis/__main__.py'],
    pathex=['chatalysis'],
    binaries=[],
    datas=data_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name="chatalysis",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="resources/images/icon.ico"
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Chatalysis',
)
app = BUNDLE(
    coll,
    name='Chatalysis.app',
    icon="resources/images/icon.icns",
    bundle_identifier=None,
    info_plist={
        'LSEnvironment': {
            'LC_NUMERIC': 'cs_CZ.UTF-8'
        }
    }
)
