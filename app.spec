# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('sql_fn_query.sql', '.'),
        ('sql_obj_query.sql', '.'),
        ('sql_tables_query.sql', '.'),
        ('sql_table_records.sql', '.'),
        ('sql_table_records_filtered.sql', '.'),
        ('assets/icon.ico', 'assets'),
        ('src/config/config.json', '.'),
    ],
    hiddenimports=[
        'flet',
        'flet.core',
        'flet.desktop',
        'pyodbc',
        'cryptography',
        'cryptography.fernet',
    ],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SQL Object Generator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin ventana de consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    manifest='app.manifest',
    icon='assets/icon.ico',
    version='version_info.txt'
)