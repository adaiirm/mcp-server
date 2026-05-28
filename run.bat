@echo off
REM Script para ejecutar el MCP Server EXE con configuración

echo ========================================
echo MCP Server - Configuración de Variables
echo ========================================
echo.

REM Pedir configuración al usuario
set /p DB_HOST="Host (default: localhost): "
if "%DB_HOST%"=="" set DB_HOST=localhost

set /p DB_USER="Usuario DB (default: root): "
if "%DB_USER%"=="" set DB_USER=root

set /p DB_PASSWORD="Contraseña DB: "

set /p DB_NAME="Nombre de la BD: "
if "%DBgit _NAME%"=="" (
    echo ERROR: Nombre de BD requerido
    pause
    exit /b 1
)

set /p DB_PORT="Puerto (default: 3306): "
if "%DB_PORT%"=="" set DB_PORT=3306

set /p ALLOWED_DATABASES="BDs permitidas separadas por coma (dejar en blanco = todas): "

REM Mostrar resumen
echo.
echo ========================================
echo Configuración:
echo   Host: %DB_HOST%
echo   Usuario: %DB_USER%
echo   Base de datos: %DB_NAME%
echo   Puerto: %DB_PORT%
if not "%ALLOWED_DATABASES%"=="" echo   BDs permitidas: %ALLOWED_DATABASES%
echo ========================================
echo.

REM Exportar variables y ejecutar
setlocal enabledelayedexpansion
set DB_HOST=%DB_HOST%
set DB_USER=%DB_USER%
set DB_PASSWORD=%DB_PASSWORD%
set DB_NAME=%DB_NAME%
set DB_PORT=%DB_PORT%
if not "%ALLOWED_DATABASES%"=="" set ALLOWED_DATABASES=%ALLOWED_DATABASES%

echo Iniciando MCP Server...
echo.

dist\mcp-server.exe

endlocal
