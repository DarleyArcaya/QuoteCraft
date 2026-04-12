@echo off
setlocal
title Compilador QuoteCraft v1.0
cd /d "%~dp0"

:: 1. Ruta al flet.exe
set "FLET_EXE=C:\Users\Darley\AppData\Local\Python\pythoncore-3.14-64\Scripts\flet.exe"

echo ====================================================
echo    LIMPIANDO...
echo ====================================================
if exist "dist" rd /s /q "dist"
if exist "build" rd /s /q "build"

echo.
echo ====================================================
echo    GENERANDO EJECUTABLE (VERSION ESTABLE)
echo ====================================================

:: Solo dejamos los argumentos que Flet acepta sin quejarse
"%FLET_EXE%" pack main.py ^
 --name "QuoteCraft" ^
 --icon "assets/favicon.ico" ^
 --add-data "assets;assets" ^
 --add-data "locales;locales" ^
 --add-data "database;database" ^
 --hidden-import "fpdf"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Algo fallo en la compilacion.
    pause
    exit /b %errorlevel%
)

echo.
echo ====================================================
echo    ¡PROCESO TERMINADO!
echo ====================================================
echo Revisa la carpeta 'dist'.
echo.
pause