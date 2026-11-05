# Optional preparation dependency installer. Offline by default; no global installs.
[CmdletBinding()]
param(
    [ValidateSet('venv','acceptance-venv')][string]$EnvironmentName = 'venv',
    [switch]$Download
)
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$local = Join-Path $root '.local/oss-integration'
$target = Join-Path $local $EnvironmentName
$manifestPath = Join-Path $root 'dependencies/property-wheels-win-py313.json'
$lock = Join-Path $root 'requirements-property-win-py313.lock'
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$platform = & python -B -c "import sys, platform; print(f'{sys.implementation.name}|{sys.version_info.major}.{sys.version_info.minor}|{platform.system()}|{platform.machine()}')"
if ($LASTEXITCODE -ne 0 -or $platform -ne 'cpython|3.13|Windows|AMD64') {
    throw 'This reviewed wheel lock supports only Windows x64 CPython 3.13; keep stdlib mode elsewhere.'
}
New-Item -ItemType Directory -Path $local -Force | Out-Null
foreach ($package in $manifest.packages) {
    if ($package.filename -notmatch '^[A-Za-z0-9_.-]+\.whl$' -or $package.sha256 -notmatch '^[a-f0-9]{64}$') {
        throw 'Invalid wheel manifest entry'
    }
    $uri = [Uri]$package.url
    if ($uri.Scheme -ne 'https' -or $uri.Host -ne 'files.pythonhosted.org') { throw 'Unapproved download origin' }
    $wheel = Join-Path $local $package.filename
    if (-not (Test-Path -LiteralPath $wheel)) {
        if (-not $Download) { throw 'Reviewed wheel absent. Download explicitly in the owner preparation environment.' }
        Invoke-WebRequest -Uri $uri -OutFile $wheel -TimeoutSec 30
    }
    if ((Get-FileHash -LiteralPath $wheel -Algorithm SHA256).Hash -ne $package.sha256) {
        throw 'Wheel hash mismatch; stop without installing or silently replacing it'
    }
}
$python = Join-Path $target 'Scripts/python.exe'
if (-not (Test-Path -LiteralPath $target)) {
    & python -m venv $target
    if ($LASTEXITCODE -ne 0) { throw 'Local venv creation failed' }
} elseif (-not (Test-Path -LiteralPath (Join-Path $target 'pyvenv.cfg'))) {
    throw 'Target exists without a venv marker; preserve it and stop'
}
$config = Get-Content -LiteralPath (Join-Path $target 'pyvenv.cfg') -Raw
if ($config -notmatch 'include-system-site-packages = false') { throw 'Venv must exclude system site packages' }
& $python -m pip --isolated --disable-pip-version-check install --no-index --find-links $local --only-binary=:all: --require-hashes --no-deps --no-compile -r $lock
if ($LASTEXITCODE -ne 0) { throw 'Locked offline install failed' }
& $python -m pip --isolated --disable-pip-version-check check
if ($LASTEXITCODE -ne 0) { throw 'Installed dependency consistency failed' }
& $python -B -c "import importlib.metadata as m, sys; print({'python': sys.version.split()[0], 'isolated': sys.prefix != sys.base_prefix, 'hypothesis': m.version('hypothesis'), 'sortedcontainers': m.version('sortedcontainers')})"
if ($LASTEXITCODE -ne 0) { throw 'Installed runtime readback failed' }
