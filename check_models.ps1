$baseUrl = "http://127.0.0.1:8317/v1"
$apiKey = "test-key-123"

$modelsToCheck = @(
    @{ id = "gemini-claude-sonnet-4-5-thinking"; role = "Architect/Reviewer" },
    @{ id = "gemini-2.5-pro"; role = "Manager" },
    @{ id = "gemini-2.5-flash"; role = "Coder" }
)

Write-Host "`n--- AI NEXUS STUDIO: Model Connectivity Check ---" -ForegroundColor Cyan

foreach ($model in $modelsToCheck) {
    Write-Host "`nChecking Role: $($model.role) (ID: $($model.id))..." -NoNewline
    
    $body = @{
        model = $model.id
        messages = @(
            @{ role = "user"; content = "Hello! Briefly state your role and say 'Ready to code'." }
        )
        max_tokens = 50
    } | ConvertTo-Json

    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/chat/completions" -Method Post -Headers @{
            "Authorization" = "Bearer $apiKey"
            "Content-Type" = "application/json"
        } -Body $body -ErrorAction Stop

        if ($response.choices[0].message.content) {
            Write-Host " [OK]" -ForegroundColor Green
            Write-Host "   Response: $($response.choices[0].message.content.Trim())" -ForegroundColor Gray
        }
    }
    catch {
        Write-Host " [FAILED]" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Write-Host "`n--- Check Complete ---`n" -ForegroundColor Cyan