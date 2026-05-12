# Quick Start Script for Tiki Recommendation System - Windows
# Hướng dẫn chạy nhanh cho hệ thống gợi ý sản phẩm Tiki

Write-Host "🚀 Tiki Recommendation System - Quick Start" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Check if backend is running
Write-Host "⏳ Kiểm tra backend..." -ForegroundColor Yellow
$backendRunning = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($backendRunning) {
    Write-Host "✅ Backend đã chạy trên port 8000" -ForegroundColor Green
} else {
    Write-Host "❌ Backend chưa chạy. Vui lòng khởi động backend trước:" -ForegroundColor Red
    Write-Host ""
    Write-Host "  cd backend" -ForegroundColor Cyan
    Write-Host "  uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload" -ForegroundColor Cyan
    Write-Host ""
}

# Check frontend dependencies
Write-Host ""
Write-Host "⏳ Kiểm tra Frontend dependencies..." -ForegroundColor Yellow
$nodeModulesPath = "frontend/node_modules"
if (-Not (Test-Path $nodeModulesPath)) {
    Write-Host "📦 Cài đặt Node dependencies..." -ForegroundColor Yellow
    Push-Location frontend
    npm install
    Pop-Location
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✅ Dependencies đã được cài đặt" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎉 Tất cả sẵn sàng!" -ForegroundColor Green
Write-Host ""
Write-Host "Bước tiếp theo:" -ForegroundColor Cyan
Write-Host "  1. Mở terminal mới" -ForegroundColor Cyan
Write-Host "  2. cd frontend && npm run dev" -ForegroundColor Cyan
Write-Host "  3. Mở http://localhost:5173 trong browser" -ForegroundColor Cyan
Write-Host ""

# Optional: Ask to start frontend
$response = Read-Host "Bạn muốn khởi động frontend ngay không? (y/n)"
if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host ""
    Write-Host "🚀 Khởi động frontend..." -ForegroundColor Green
    Push-Location frontend
    npm run dev
} else {
    Write-Host ""
    Write-Host "Để khởi động frontend sau, chạy:" -ForegroundColor Cyan
    Write-Host "  cd frontend && npm run dev" -ForegroundColor Cyan
}
