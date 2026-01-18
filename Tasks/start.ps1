# Function to check if Chocolatey is installed
function Is-ChocolateyInstalled {
    try {
        Get-Command choco -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Function to install Chocolatey
function Install-Chocolatey {
    Write-Host "Chocolatey not found. Installing Chocolatey..."
    Set-ExecutionPolicy Bypass -Scope Process -Force
    $chocoInstallScript = "https://chocolatey.org/install.ps1"
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString($chocoInstallScript))
}

# Function to check if a Chocolatey package is installed
function Choco-IsPackageInstalled {
    param(
        [string]$packageName,
        [string[]]$extraArgs = @()
    )
    $argsString = $extraArgs -join " "
    Write-Host "Check is choco package installed: $packageName $argsString"
    $list = choco list --exact $packageName @extraArgs
    if ($list -match "0 packages installed") {
        return $false
    }
    return $true
}

# Function to install a missing Chocolatey package
function Choco-InstallPackage {
    param(
        [string]$packageName,
        [string[]]$extraArgs = @()
    )
    $argsString = $extraArgs -join " "
    Write-Host "Launching elevated console to install $packageName $argsString..."
    $args = "-NoProfile -ExecutionPolicy Bypass -Command `"choco install -y --no-progress $packageName $argsString`""
    $proc = Start-Process -FilePath "powershell.exe" -ArgumentList $args -Verb RunAs -PassThru
    $proc.WaitForExit()
    if ($proc.ExitCode -ne 0) {
        Write-Error "Failed to install $packageName via Chocolatey in elevated console. Exiting."
        exit 1
    }
}

# Ensure Chocolatey is installed before checking packages
if (-not (Is-ChocolateyInstalled)) {
    Install-Chocolatey
    if (-not (Is-ChocolateyInstalled)) {
        Write-Error "Chocolatey installation failed. Please install it manually."
        exit 1
    }
} else {
    Write-Host "Chocolatey is installed."
}

# Required packages with optional extra arguments array
$requiredPackages = @(
    @{ Name = "python"; ExtraArgs = @("--version=3.9.12") }
)
foreach ($pkg in $requiredPackages) {
    if (-not (Choco-IsPackageInstalled $pkg.Name $pkg.ExtraArgs)) {
        Choco-InstallPackage $pkg.Name $pkg.ExtraArgs
    } else {
        Write-Host "$($pkg.Name) $($pkg.ExtraArgs -join ' ') is already installed."
    }
}

# Refresh environment variables for this session
Import-Module $env:ChocolateyInstall\helpers\chocolateyProfile.psm1

# Check if Python and pip are available
try {
    $pythonCmd = Get-Command python -ErrorAction Stop
} catch {
    Write-Error "Python is not available after installation. Please verify your Chocolatey and Python setup."
    exit 1
}

& python -m pip --version > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "pip not available. Installing pip..."
    python -m ensurepip
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install pip."
        exit 1
    }
}

# Check venv module, otherwise install virtualenv
& python -c "import venv" > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "venv module not available. Installing virtualenv..."
    & python -m pip install virtualenv
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install virtualenv."
        exit 1
    }
    $USE_VENV = $false
} else {
    $USE_VENV = $true
}

# Create virtual environment if not exists
if (!(Test-Path .venv)) {
    Write-Host "Creating virtual environment..."
    if ($USE_VENV) {
        & python -m venv .venv
    } else {
        & virtualenv .venv
    }
}

# Activate virtual environment
. .\.venv\Scripts\Activate.ps1

# Install Python requirements
& python -m pip install -r requirements.txt

# Print active invoke parameters
& invoke get-info

# List available invoke commands
& invoke --list
