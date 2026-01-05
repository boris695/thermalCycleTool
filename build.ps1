# ============================
# ThermalCycleTool build script
# ============================

# bypass execution policy for this script
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force



# Nettoyage anciens builds
Remove-Item -Recurse -Force venv -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item .\dist\* -Force -ErrorAction SilentlyContinue


# Activer le venv
if (!(Test-Path "venv")) {
    Write-Host "Virtualenv not found. Creating..."
    python -m venv venv
}

& .\venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

# Nettoyage ancien build
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue

$config = Get-Content .\config.json | ConvertFrom-Json
$AppName = $config.app_name
$version_number = $config.version
$ExeName = "$AppName-$version_number"

Write-Host "Building $ExeName..."

# Build
pyinstaller `
  --onefile `
  --name $ExeName `
  --icon icon.ico `
  --add-data "templates;templates" `
  --add-data "static;static" `
  --add-data "config.json;." `
  --hidden-import matplotlib.backends.backend_pdf `
  app.py

Write-Host "Build finished -> dist\$ExeName.exe"
