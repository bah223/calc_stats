# Analysis Scripts Menu for PowerShell
# UTF-8 support for Cyrillic characters

$host.UI.RawUI.BackgroundColor = 'Black'
$host.UI.RawUI.ForegroundColor = 'White'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ''
Write-Host '================================================================================' -ForegroundColor Cyan
Write-Host '                          ANALYSIS SCRIPTS MENU' -ForegroundColor Cyan
Write-Host '================================================================================' -ForegroundColor Cyan
Write-Host ''
Write-Host '1 - angelina_report.py' -ForegroundColor Yellow
Write-Host '   Report with transaction counts by status (CAPTURED, CANCELLED, DECLINED, REFUNDED)' -ForegroundColor Gray
Write-Host ''
Write-Host '2 - calc_stats.py' -ForegroundColor Yellow
Write-Host '   Overall statistics: total operations, success rate, daily turnover' -ForegroundColor Gray
Write-Host ''
Write-Host '3 - 12oo.py' -ForegroundColor Yellow
Write-Host '   Count transactions before 12:00 Moscow time, aggregated by merchant' -ForegroundColor Gray
Write-Host ''
Write-Host '4 - mosteh.py (REQUIRES PARAMETERS!)' -ForegroundColor Yellow
Write-Host '   MosTech report with date filtering' -ForegroundColor Gray
Write-Host '   Usage: mosteh.py --start_date YYYY-MM-DD --end_date YYYY-MM-DD' -ForegroundColor Gray
Write-Host '   Example: mosteh.py --start_date 2025-01-15 --end_date 2025-01-15' -ForegroundColor Gray
Write-Host ''
Write-Host '5 - rep0000.py' -ForegroundColor Yellow
Write-Host '   Interactive analysis with manual input for 5 merchant accounts' -ForegroundColor Gray
Write-Host '   Growth/decline analysis with full analytics visibility' -ForegroundColor Gray
Write-Host ''
Write-Host '================================================================================' -ForegroundColor Cyan
Write-Host ''

$choice = Read-Host 'Enter choice 1-5'
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

switch ($choice) {
    '1' {
        Write-Host 'Running angelina_report.py ...' -ForegroundColor Green
        & python "$scriptPath\angelina_report.py"
    }
    '2' {
        Write-Host 'Running calc_stats.py ...' -ForegroundColor Green
        & python "$scriptPath\calc_stats.py"
    }
    '3' {
        Write-Host 'Running 12oo.py ...' -ForegroundColor Green
        & python "$scriptPath\12oo.py"
    }
    '4' {
        Write-Host ''
        $start = Read-Host 'Enter start date (YYYY-MM-DD)'
        $end = Read-Host 'Enter end date (YYYY-MM-DD)'
        
        if ([string]::IsNullOrWhiteSpace($start) -or [string]::IsNullOrWhiteSpace($end)) {
            Write-Host 'Error: Both dates are required!' -ForegroundColor Red
        } else {
            Write-Host "Generating report for $start - $end..." -ForegroundColor Green
            & python "$scriptPath\mosteh.py" --start_date $start --end_date $end
        }
    }
    '5' {
        Write-Host 'Running rep0000.py ...' -ForegroundColor Green
        & python "$scriptPath\rep0000.py"
    }
    default {
        Write-Host "Invalid choice: $choice" -ForegroundColor Red
    }
}

Write-Host ''
Write-Host 'Press any key to exit...' -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
