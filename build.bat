@echo off
REM Activar entorno virtual (si usas uno)
REM call venv\Scripts\activate

echo =============================
echo  RECONSTRUYENDO EL EXE...
echo =============================

REM Limpiar builds anteriores (opcional)
rmdir /s /q build
rmdir /s /q dist


REM Instalar dependencias si fuera necesario
REM pip install -r requirements.txt

REM Ejecutar PyInstaller con el archivo .spec existente
pyinstaller build.spec

echo =============================
echo  BUILD COMPLETADO!
echo  EXE generado en /dist/
echo =============================
pause