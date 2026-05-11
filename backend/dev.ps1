& .\env\Scripts\Activate.ps1

Write-Host "Starting TeachWork Backend..."

uvicorn app.main:app --reload