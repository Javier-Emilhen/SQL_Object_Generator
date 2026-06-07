import os
import subprocess
import sys

def build_app():
    print("Iniciando construcción de la aplicación...")
    
    # Limpiar builds anteriores
    if os.path.exists("build"):
        import shutil
        shutil.rmtree("build")
    if os.path.exists("dist"):
        import shutil
        shutil.rmtree("dist")
    
    # Ejecutar PyInstaller del entorno activo
    result = subprocess.run([
        sys.executable, "-m", "PyInstaller", "--noconfirm", "app.spec"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Aplicación construida exitosamente!")
        print("📁 Ejecutable disponible en: dist/SQL Object Generator.exe")
    else:
        print("❌ Error en la construcción:")
        print(result.stderr)

if __name__ == "__main__":
    build_app()