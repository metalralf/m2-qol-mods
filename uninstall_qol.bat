@echo off
rem ============================================================
rem  Madocsa2 QoL modok - ELTAVOLITO
rem  Visszaallitja az eredeti pack-ot (a telepito altal mentett
rem  biztonsagi mentesbol). A jatek mappajaban kell futtatni.
rem ============================================================
cd /d "%~dp0"

tasklist /fi "imagename eq Madocsa2.exe" 2>nul | find /i "Madocsa2.exe" >nul
if not errorlevel 1 (
  echo.
  echo HIBA: a jatek most fut. Zard be teljesen, majd futtasd ujra!
  echo.
  pause
  exit /b 1
)

if not exist "pack\root.epk.qolbak" (
  echo.
  echo Nincs biztonsagi mentes (pack\root.epk.qolbak).
  echo Az install_qol.bat meg nem futott le, vagy mar visszaallitottal.
  echo.
  pause
  exit /b 1
)

echo Eredeti pack visszaallitasa...
copy /y "pack\root.epk.qolbak" "pack\root.epk" >nul
copy /y "pack\root.eix.qolbak" "pack\root.eix" >nul
del "pack\root.epk.qolbak" >nul 2>nul
del "pack\root.eix.qolbak" >nul 2>nul

echo.
echo KESZ. Az eredeti allapot visszaallitva.
echo.
pause
