@echo off
REM ============================================================================
REM Cleanup Script for CrewAI Wall Panel QC
REM Removes all generated output files to provide a clean slate between runs
REM ============================================================================

echo.
echo ========================================
echo  CrewAI Wall Panel QC - Cleanup
echo ========================================
echo.

REM Check if results directory exists
if not exist "results\" (
    echo No results directory found. Nothing to clean.
    goto :end
)

echo Cleaning up output files...
echo.

REM Remove JSON files
if exist "results\panel_data.json" (
    del /Q "results\panel_data.json"
    echo [X] Deleted panel_data.json
)

if exist "results\violations.json" (
    del /Q "results\violations.json"
    echo [X] Deleted violations.json
)

REM Remove HTML/PDF reports
if exist "results\*.html" (
    del /Q "results\*.html"
    echo [X] Deleted HTML reports
)

if exist "results\*.pdf" (
    del /Q "results\*.pdf"
    echo [X] Deleted PDF reports
)

REM Remove visualization PNGs
if exist "results\visualizations\*.png" (
    del /Q "results\visualizations\*.png"
    echo [X] Deleted visualization images
)

REM Remove visualizations directory if empty
if exist "results\visualizations\" (
    rmdir "results\visualizations" 2>nul
    if not exist "results\visualizations\" (
        echo [X] Removed visualizations directory
    )
)

REM Remove any PNG files in results root
if exist "results\*.png" (
    del /Q "results\*.png"
    echo [X] Deleted PNG files from results directory
)

REM Remove any files in reports root
if exist "reports\*" (
    del /Q "reports\*"
    echo [X] Deleted files in reports directory
)


echo.
echo ========================================
echo  Cleanup Complete!
echo ========================================
echo.
echo Ready for a fresh run.
echo Run: python main.py --ifc test_data\wall_1.ifc
echo.

:end
pause
