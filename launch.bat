@echo off
echo ===============================================================
echo                 🚀 SoccerSafe - Lancement Rapide
echo               Projet M1 IPSSI - Base de Donnees NoSQL
echo ===============================================================
echo.

echo 💡 Que voulez-vous faire ?
echo.
echo [1] Configuration complete (premiere fois)
echo [2] Lancer l'application simple
echo [3] Lancer l'application complete 
echo [4] Tester le systeme ML
echo [5] Installer les dependances
echo [Q] Quitter
echo.

set /p choice="Votre choix (1-5 ou Q): "

if "%choice%"=="1" (
    echo.
    echo 🔧 Configuration complete du projet...
    python start.py --setup
    goto end
)

if "%choice%"=="2" (
    echo.
    echo 🚀 Lancement de l'application simple...
    python start.py --start simple
    goto end
)

if "%choice%"=="3" (
    echo.
    echo 🚀 Lancement de l'application complete...
    python start.py --start full
    goto end
)

if "%choice%"=="4" (
    echo.
    echo 🧪 Test du systeme ML...
    python start.py --test
    goto end
)

if "%choice%"=="5" (
    echo.
    echo 📦 Installation des dependances...
    python start.py --install
    goto end
)

if /i "%choice%"=="Q" (
    echo Au revoir ! 👋
    goto end
)

echo Choix invalide. Veuillez entrer 1, 2, 3, 4, 5 ou Q.
pause
goto menu

:end
echo.
echo ===============================================================
echo                    Operation terminee
echo ===============================================================
pause