param (
    [string[]]$Tags,
    [string]$Username,
    [string]$Password,
    [string]$Environment
)

# Ustal URL API Grafany na podstawie środowiska
switch ($Environment) {
    "dev"    { $grafanaApiUrl = "https://grafana-dev.example.com/api" }
    "uat"    { $grafanaApiUrl = "https://grafana-uat.example.com/api" }
    "prod"   { $grafanaApiUrl = "https://grafana-prod.example.com/api" }
    "leprod" { $grafanaApiUrl = "https://grafana-leprod.example.com/api" }
    default  { Write-Error "Nieznane środowisko: $Environment"; exit 1 }
}

# Konwersja tagów na format wymagany przez API
$tagsParam = $Tags -join ','

# Zakodowanie danych logowania w formacie base64
$encodedAuth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("$Username:$Password"))

# Ustawienie nagłówków z Basic Authentication
$headers = @{
    Authorization = "Basic $encodedAuth"
}

# Pobierz listę dashboardów na podstawie tagów
$dashboards = Invoke-RestMethod -Uri "$grafanaApiUrl/search?tag=$tagsParam" -Method Get -Headers $headers

# Główna ścieżka zapisu
$baseDir = "C:\path\to\save\$Environment"

# Funkcja do tworzenia struktury katalogów i zapisywania dashboardów
function Save-Dashboard {
    param (
        [object]$dashboard
    )
    
    # Pobierz dane dashboardu
    $dashboardData = Invoke-RestMethod -Uri "$grafanaApiUrl/dashboards/uid/$($dashboard.uid)" -Method Get -Headers $headers

    # Utwórz strukturę katalogów na podstawie folderu dashboardu
    $folderPath = Join-Path -Path $baseDir -ChildPath $dashboard.folderTitle
    if (-not (Test-Path $folderPath)) {
        New-Item -Path $folderPath -ItemType Directory
    }

    # Ustal nazwę pliku (title dashboardu)
    $filePath = Join-Path -Path $folderPath -ChildPath "$($dashboard.title).json"

    # Zapisz dashboard jako plik JSON
    $dashboardData | ConvertTo-Json -Depth 10 | Out-File -FilePath $filePath
}

# Iteracja przez każdy dashboard i zapisanie go
foreach ($dashboard in $dashboards) {
    Save-Dashboard -dashboard $dashboard
}

Write-Host "Zakończono pobieranie i zapisywanie dashboardów."

# Przejdź do katalogu repozytorium Git
Set-Location -Path "C:\path\to\your\git\repository"

# Sprawdź aktualny branch
$currentBranch = git rev-parse --abbrev-ref HEAD

if ($currentBranch -eq "FeatureBranch") {
    # Jeśli jesteśmy na FeatureBranch, po prostu commit i push
    git add -A
    git commit -m "Dodano dane z Grafany dla środowiska $Environment z tagami: $tagsParam"
    git push
} elseif ($currentBranch -eq "develop" -or $currentBranch -eq "master") {
    # Jeśli jesteśmy na develop lub master, utwórz nowy FeatureBranch
    $newBranchName = "FeatureBranch-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    git checkout -b $newBranchName
    git add -A
    git commit -m "Dodano dane z Grafany dla środowiska $Environment z tagami: $tagsParam"
    git push -u origin $newBranchName
} else {
    Write-Host "Aktualny branch: $currentBranch - brak akcji do wykonania."
}
