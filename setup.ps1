# Smart Analytics System - Setup Script for Windows
# This script will set up both backend and frontend

$ErrorActionPreference = "Stop"

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Smart Analytics System Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Color functions
function Write-Success {
    Write-Host $args -ForegroundColor Green
}

function Write-Error {
    Write-Host $args -ForegroundColor Red
}

function Write-Info {
    Write-Host $args -ForegroundColor Yellow
}

# Check Python
Write-Info "🔍 Checking Python installation..."
try {
    $pythonVersion = python --version
    Write-Success "✅ Python found: $pythonVersion"
} catch {
    Write-Error "❌ Python not found. Please install Python 3.8+"
    exit 1
}

# Check Node.js
Write-Info "🔍 Checking Node.js installation..."
try {
    $nodeVersion = node --version
    Write-Success "✅ Node.js found: $nodeVersion"
} catch {
    Write-Error "❌ Node.js not found. Please install Node.js 14+"
    exit 1
}

# Setup Backend
Write-Host ""
Write-Info "================================"
Write-Info "Setting up Backend..."
Write-Info "================================"

Set-Location backend

Write-Info "📦 Installing backend dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Success "✅ Backend dependencies installed successfully"
} else {
    Write-Error "❌ Failed to install backend dependencies"
    exit 1
}

# Setup Frontend
Write-Host ""
Write-Info "================================"
Write-Info "Setting up Frontend..."
Write-Info "================================"

Set-Location ../frontend

Write-Info "📦 Installing frontend dependencies..."
npm install

if ($LASTEXITCODE -eq 0) {
    Write-Success "✅ Frontend dependencies installed successfully"
} else {
    Write-Error "❌ Failed to install frontend dependencies"
    exit 1
}

Set-Location ..

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

Write-Host "🚀 Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Start Backend (in terminal 1):"
Write-Host "   cd backend"
Write-Host "   python -m uvicorn app.main:app --reload" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Start Frontend (in terminal 2):"
Write-Host "   cd frontend"
Write-Host "   npm run dev" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Open browser:"
Write-Host "   http://localhost:5173" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. Login with Admin:"
Write-Host "   Username: admin"
Write-Host "   Password: admin123" -ForegroundColor Yellow
Write-Host ""
Write-Host "📖 For more details, see README.md" -ForegroundColor Cyan
Write-Host ""
