#!/usr/bin/env python3
import os
import subprocess
import shutil
import zipfile
from pathlib import Path

def create_project_structure():
    dirs = ['src', 'bin', 'build', '.buildozer/android/platform/build-debug']
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    print("✓ Estrutura criada")

def install_dependencies():
    print("Instalando dependências...")
    packages = ['kivy', 'buildozer', 'opencv-python', 'numpy', 'ultralytics', 'cython', 'pillow']
    for pkg in packages:
        subprocess.run(['pip', 'install', pkg], capture_output=True)
    print("✓ Dependências instaladas")

def build_apk():
    print("Compilando APK...")
    result = subprocess.run(['buildozer', 'android', 'debug'], capture_output=False)
    return result.returncode == 0

def create_distribution_zip():
    print("Criando arquivo de distribuição...")
    files_to_include = ['main.py', 'buildozer.spec', 'requirements.txt', 'README.md', 'build_apk.sh', 'autoaim.kv']
    apk_files = list(Path('bin').glob('*.apk'))
    with zipfile.ZipFile('AutoAimDetector-Android.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in files_to_include:
            if Path(file).exists():
                zf.write(file, f'autoaim/{file}')
        for apk in apk_files:
            zf.write(str(apk), f'autoaim/bin/{apk.name}')
    print("✓ Arquivo ZIP criado: AutoAimDetector-Android.zip")

def main():
    print("╔════════════════════════════════════╗")
    print("║   Auto-Aim Detector APK Builder   ║")
    print("╚════════════════════════════════════╝\n")
    try:
        create_project_structure()
        install_dependencies()
        print("\nAgora execute: ./build_apk.sh")
        print("\nOu para compilar manualmente:")
        print("  buildozer android debug")
    except Exception as e:
        print(f"✗ Erro: {e}")
        return False
    return True

if __name__ == '__main__':
    main()