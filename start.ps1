# ClearPath — Start Script
# Run this in PowerShell to start both frontend and backend

Write-Host "Starting ClearPath..." -ForegroundColor Cyan
Write-Host ""

# Start backend
Write-Host "Starting Python backend on http://localhost:8000 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\Users\Brahmjot Singh\Downloads\ClearPath\backend'; python -m uvicorn main:app --reload --port 8000"

Start-Sleep -Seconds 2

# Start frontend
Write-Host "Starting React frontend on http://localhost:5173 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\Users\Brahmjot Singh\Downloads\ClearPath\frontend'; npm run dev"

Write-Host ""
Write-Host "ClearPath is starting!" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Yellow
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Magenta
