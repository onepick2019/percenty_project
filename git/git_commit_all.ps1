# PowerShell Git Commit Script for Percenty Project
# UTF-8 encoding support
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================" -ForegroundColor Green
Write-Host "Percenty Project Git Commit Script" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Check current Git status
Write-Host "[1/5] Checking Git status..." -ForegroundColor Yellow
git status
Write-Host ""

# Get commit message from user
$commitMessage = Read-Host "Enter commit message (e.g., feat: add new feature)"
if ([string]::IsNullOrWhiteSpace($commitMessage)) {
    Write-Host "Error: Commit message is empty." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Add all changes to staging area
Write-Host "[2/5] Adding all changes to staging area..." -ForegroundColor Yellow
git add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to execute git add." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Done!" -ForegroundColor Green
Write-Host ""

# Commit changes
Write-Host "[3/5] Committing changes..." -ForegroundColor Yellow
git commit -m "$commitMessage"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to execute git commit." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Done!" -ForegroundColor Green
Write-Host ""

# Push to remote repository
Write-Host "[4/5] Pushing to remote repository..." -ForegroundColor Yellow
git push origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to execute git push." -ForegroundColor Red
    Write-Host "Please check network connection or authentication." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Done!" -ForegroundColor Green
Write-Host ""

# Final status check
Write-Host "[5/5] Final Git status check..." -ForegroundColor Yellow
git status
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "All operations completed successfully!" -ForegroundColor Green
Write-Host "Commit message: $commitMessage" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to exit"