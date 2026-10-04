#Requires -RunAsAdministrator
<#
.SYNOPSIS
  Percenty MySQL Windows pre-restore prep helpers (folders, firewall, post-install checks).

.DESCRIPTION
  Does NOT download or install MySQL MSI — run Phase A-2 manually per docs/runbooks/mysql_backup_restore_runbook.md

.EXAMPLE
  .\mysql_prep.ps1
  .\mysql_prep.ps1 -Phase PrepOnly
  .\mysql_prep.ps1 -Phase Verify -MySqlServiceName MySQL84
#>
[CmdletBinding()]
param(
    [ValidateSet('All', 'PrepOnly', 'Firewall', 'Verify')]
    [string] $Phase = 'All',

    [string] $DataRoot = 'C:\MySQL',
    [string] $BackupRoot = 'D:\percenty_backups\mysql\daily',
    [string] $FirewallRuleName = 'MySQL 3306 LAN',
    [string] $LanCidr = '192.168.0.0/24',
    [int] $Port = 3306,
    [string] $MySqlServiceName = 'MySQL84'
)

$ErrorActionPreference = 'Stop'

function Write-Step([string] $Message) {
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Ensure-Directories {
    Write-Step 'Creating MySQL and backup directories'
    $dirs = @(
        Join-Path $DataRoot 'Data',
        Join-Path $DataRoot 'Logs',
        Join-Path $DataRoot 'Tmp',
        Join-Path $DataRoot 'Backup',
        $BackupRoot
    )
    foreach ($d in $dirs) {
        if (-not (Test-Path -LiteralPath $d)) {
            New-Item -ItemType Directory -Force -Path $d | Out-Null
            Write-Host "  Created: $d"
        } else {
            Write-Host "  Exists:  $d"
        }
    }
}

function Ensure-FirewallRule {
    Write-Step "Firewall inbound TCP $Port for $LanCidr"
    $existing = Get-NetFirewallRule -DisplayName $FirewallRuleName -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "  Rule already exists: $FirewallRuleName"
        return
    }
    New-NetFirewallRule -DisplayName $FirewallRuleName `
        -Direction Inbound -Protocol TCP -LocalPort $Port `
        -RemoteAddress $LanCidr -Action Allow -Profile Private | Out-Null
    Write-Host "  Created rule: $FirewallRuleName"
}

function Test-MySqlPostInstall {
    Write-Step 'Post-install verification (service, port, paths)'

    $svc = Get-Service -Name $MySqlServiceName -ErrorAction SilentlyContinue
    if (-not $svc) {
        Write-Warning "Service '$MySqlServiceName' not found. List: $(Get-Service *mysql* | ForEach-Object Name)"
    } else {
        Write-Host "  Service: $($svc.Name) — Status: $($svc.Status)"
        if ($svc.Status -ne 'Running') {
            Write-Warning 'MySQL service is not Running. Start it before restore.'
        }
    }

    $dataDir = Join-Path $DataRoot 'Data'
    if (Test-Path -LiteralPath $dataDir) {
        Write-Host "  Data directory exists: $dataDir"
    } else {
        Write-Warning "Data directory missing: $dataDir (set datadir in my.ini / installer)"
    }

    $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if ($listener) {
        Write-Host "  Port $Port is LISTENING (local address(es): $($listener.LocalAddress -join ', '))"
    } else {
        Write-Warning "Nothing listening on port $Port yet."
    }

    $iniCandidates = @(
        'C:\ProgramData\MySQL\MySQL Server 8.4\my.ini',
        'C:\ProgramData\MySQL\MySQL Server 8.0\my.ini'
    )
    foreach ($ini in $iniCandidates) {
        if (Test-Path -LiteralPath $ini) {
            Write-Host "  Found my.ini: $ini"
            $hit = Select-String -Path $ini -Pattern 'max_allowed_packet|innodb_buffer_pool_size|datadir' -ErrorAction SilentlyContinue
            if ($hit) {
                $hit | ForEach-Object { Write-Host "    $($_.Line.Trim())" }
            }
            break
        }
    }

    Write-Host ''
    Write-Host 'Manual checks (see runbook Phase A-5):' -ForegroundColor Yellow
    Write-Host '  mysql -u root -p -e "SELECT VERSION(); SHOW VARIABLES LIKE ''datadir'';"'
    Write-Host "  mysql -h 127.0.0.1 -P $Port -u root -p -e ""SELECT 1;"""
}

switch ($Phase) {
    'PrepOnly' { Ensure-Directories }
    'Firewall' { Ensure-FirewallRule }
    'Verify'   { Test-MySqlPostInstall }
    'All'      {
        Ensure-Directories
        Ensure-FirewallRule
        Test-MySqlPostInstall
    }
}

Write-Step 'Done. Next: install/configure MySQL 8.4 (Phase A-2, A-3) then restore when SQL download completes.'
