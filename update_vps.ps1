# Quick Update Script for VPS
# Updates the dashboard with new Availability Charts

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Updating Junction Dashboard on VPS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Build the React app
Write-Host "[1/3] Building React app..." -ForegroundColor Yellow
Set-Location "C:\Users\Rutaab\Desktop\Sakina 75 percent script\junction-dashboard"
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed! Please check errors above." -ForegroundColor Red
    exit 1
}

Write-Host "✓ Build completed successfully!" -ForegroundColor Green
Write-Host ""

# Step 2: Show SCP command
Write-Host "[2/3] Uploading files to VPS..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Run this command to upload:" -ForegroundColor Cyan
Write-Host "scp -r dist/* srv1006127:/var/www/junction-dashboard/" -ForegroundColor White
Write-Host ""
Write-Host "After upload, SSH to VPS and run:" -ForegroundColor Cyan
Write-Host "ssh srv1006127" -ForegroundColor White
Write-Host "systemctl restart nginx" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Build Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dashboard will be live at:" -ForegroundColor Yellow
Write-Host "https://75_dependable_yield_charts.pfepltech.com" -ForegroundColor White
Write-Host ""

