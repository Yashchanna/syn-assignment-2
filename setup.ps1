# Setup Script for the Assignment Environment
Write-Host "Setting up the Python virtual environment..."

# Check for python
if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Error "Python is not installed or not in PATH."
    exit 1
}

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
} else {
    Write-Host "Virtual environment already exists."
}

# Install dependencies
Write-Host "Installing dependencies..."
# Use call operator to execute pip from the virtual environment
& .\venv\Scripts\python.exe -m pip install --upgrade pip
& .\venv\Scripts\python.exe -m pip install -r requirements.txt

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..."
    Set-Content -Path ".env" -Value "OPENAI_API_KEY=your_api_key_here`n"
}

Write-Host "Setup complete. To activate the environment, run: .\venv\Scripts\activate"
