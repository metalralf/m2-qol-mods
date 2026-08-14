@echo off
rem ============================================================
rem  Madocsa2 QoL modok - TELEPITO
rem  Ezt a fajlt a jatek mappajaba kell masolni (oda, ahol a
rem  Madocsa2.exe van), majd duplan ra kattintani.
rem  A script magatol biztositasi mentest keszit, barmikor
rem  visszavonhato az uninstall_qol.bat-tal.
rem ============================================================
cd /d "%~dp0"

if not exist "Madocsa2.exe" (
  echo.
  echo HIBA: a Madocsa2.exe nem talalhato ebben a mappaban.
  echo Helyezd ezt a fajlt a jatek mappajaba (a Madocsa2.exe melle)!
  echo.
  pause
  exit /b 1
)

tasklist /fi "imagename eq Madocsa2.exe" 2>nul | find /i "Madocsa2.exe" >nul
if not errorlevel 1 (
  echo.
  echo HIBA: a jatek most fut. Zard be teljesen, majd futtasd ujra!
  echo.
  pause
  exit /b 1
)

if not exist "root.epk" (
  echo.
  echo HIBA: a root.epk nincs a jatek mappajaban.
  echo A zip OSSZES fajlat be kell masolni a Madocsa2.exe melle!
  echo.
  pause
  exit /b 1
)

if not exist "pack\root.epk" (
  echo.
  echo HIBA: nincs pack\root.epk a jatek mappajaban.
  echo Biztos a jo mappaban vagy? (Madocsa2.exe mellett kell lennie.)
  echo.
  pause
  exit /b 1
)

echo.
echo Biztonsagi mentes keszitese (csak egyszer)...
if not exist "pack\root.epk.qolbak" copy /y "pack\root.epk" "pack\root.epk.qolbak" >nul
if not exist "pack\root.eix.qolbak" copy /y "pack\root.eix" "pack\root.eix.qolbak" >nul

echo Modok masolasa a pack mappaba...
copy /y "root.epk" "pack\root.epk" >nul
copy /y "root.eix" "pack\root.eix" >nul

echo.
echo KESZ! A QoL modok aktivak. Indithatod a jatekot.
echo Visszavonas: kattints az uninstall_qol.bat-ra.
echo.
pause
