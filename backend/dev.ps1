& ..\env\Scripts\Activate.ps1

Write-Host "Starting TeachWork Backend..."

python -m uvicorn app.main:app --reload
