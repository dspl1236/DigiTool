"""
Build script for DigifantTool desktop exe.
Run: python build.py
Produces: dist/DigifantTool.exe (Windows) or dist/DigifantTool (Linux/Mac)
"""
import subprocess
import sys
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.join(ROOT, 'app')
DESKTOP_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(ROOT, 'dist')

def run(cmd):
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        print(f"ERROR: command failed with code {result.returncode}")
        sys.exit(result.returncode)

def main():
    print("=== DigifantTool Build ===")
    
    # Install deps
    run([sys.executable, '-m', 'pip', 'install', 'pywebview', 'pyinstaller', '--quiet'])

    is_windows = sys.platform == 'win32'
    sep = ';' if is_windows else ':'

    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--windowed' if is_windows else '--onefile',
        '--name', 'DigifantTool',
        '--distpath', DIST_DIR,
        '--workpath', os.path.join(DESKTOP_DIR, 'build_tmp'),
        '--specpath', DESKTOP_DIR,
        # Bundle the HTML app folder
        f'--add-data={APP_DIR}{sep}app',
        # Hidden imports for pywebview backends
        '--hidden-import', 'webview.platforms.winforms' if is_windows else 'webview.platforms.gtk',
        '--hidden-import', 'clr',
        # Main script
        os.path.join(DESKTOP_DIR, 'main.py'),
    ]

    if is_windows:
        cmd += ['--hidden-import', 'pythonnet']

    run(cmd)

    exe = os.path.join(DIST_DIR, 'DigifantTool.exe' if is_windows else 'DigifantTool')
    if os.path.exists(exe):
        size_mb = os.path.getsize(exe) / 1_000_000
        print(f"\n✓ Build complete: {exe} ({size_mb:.1f} MB)")
    else:
        print("\nBuild may have succeeded — check dist/ folder")

if __name__ == '__main__':
    main()
