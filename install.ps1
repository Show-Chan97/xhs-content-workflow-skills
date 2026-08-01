param(
    [Parameter(Position = 0)]
    [string]$Requested
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$strictUtf8 = New-Object System.Text.UTF8Encoding($false, $true)
[Console]::InputEncoding = $utf8NoBom
[Console]::OutputEncoding = $utf8NoBom
$OutputEncoding = $utf8NoBom

$repoDir = $PSScriptRoot
$availableSkills = @(
    "xhs-trend-content",
    "xhs-daily-monitor",
    "xhs-competitor-research",
    "xhs-note-performance-diagnosis",
    "xhs-base-daily-ops",
    "content-commerce-meeting-execution",
    "xhs-decision-path-mining"
)

function Show-Usage {
    Write-Host "Usage: .\install.ps1 all|xhs-trend-content|xhs-daily-monitor|xhs-competitor-research|xhs-note-performance-diagnosis|xhs-base-daily-ops|content-commerce-meeting-execution|xhs-decision-path-mining"
}

function Test-Utf8SkillFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $bytes = [System.IO.File]::ReadAllBytes($Path)
    if (
        $bytes.Length -ge 3 -and
        $bytes[0] -eq 0xEF -and
        $bytes[1] -eq 0xBB -and
        $bytes[2] -eq 0xBF
    ) {
        throw "SKILL.md must be UTF-8 without BOM: $Path"
    }

    try {
        $null = $strictUtf8.GetString($bytes)
    }
    catch {
        throw "SKILL.md is not valid UTF-8: $Path"
    }

    $content = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
    if (-not ($content.StartsWith("---`n") -or $content.StartsWith("---`r`n"))) {
        throw "SKILL.md does not start with YAML frontmatter: $Path"
    }
}

if ([string]::IsNullOrWhiteSpace($Requested)) {
    Show-Usage
    exit 2
}

if ($Requested -eq "all") {
    $selectedSkills = $availableSkills
}
elseif ($availableSkills -contains $Requested) {
    $selectedSkills = @($Requested)
}
else {
    [Console]::Error.WriteLine("Unknown skill: $Requested")
    Show-Usage
    exit 2
}

if ([string]::IsNullOrWhiteSpace($env:CODEX_HOME)) {
    if ([string]::IsNullOrWhiteSpace($env:USERPROFILE)) {
        throw "USERPROFILE is not available. Set CODEX_HOME and run the installer again."
    }
    $codexRoot = Join-Path $env:USERPROFILE ".codex"
}
else {
    $codexRoot = $env:CODEX_HOME
}

$installRoot = Join-Path $codexRoot "skills"

foreach ($skillName in $selectedSkills) {
    $sourceDir = Join-Path $repoDir $skillName
    $skillFile = Join-Path $sourceDir "SKILL.md"
    $targetDir = Join-Path $installRoot $skillName

    if (-not (Test-Path -LiteralPath $skillFile -PathType Leaf)) {
        throw "Invalid skill directory: $sourceDir"
    }

    Test-Utf8SkillFile -Path $skillFile

    if (Test-Path -LiteralPath $targetDir) {
        throw "Installation stopped: $targetDir already exists. Back up or move the existing directory, then run this command again."
    }
}

New-Item -ItemType Directory -Path $installRoot -Force | Out-Null

foreach ($skillName in $selectedSkills) {
    $sourceDir = Join-Path $repoDir $skillName
    $targetDir = Join-Path $installRoot $skillName

    Copy-Item -LiteralPath $sourceDir -Destination $targetDir -Recurse
    Test-Utf8SkillFile -Path (Join-Path $targetDir "SKILL.md")
    Write-Host "Installed and validated $skillName -> $targetDir"
}

Write-Host "Installation complete. Start a new Codex task to use the installed skills."
