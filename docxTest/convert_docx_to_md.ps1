# PowerShell script to convert all DOCX files to Markdown using pandoc
# Each DOCX file will have its own image directory

$docxDir = ".\docx"
$outputDir = ".\res"

# Create output directory if it doesn't exist
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

# Get all DOCX files
$docxFiles = Get-ChildItem -Path $docxDir -Filter "*.docx"

if ($docxFiles.Count -eq 0) {
    Write-Host "❌ No DOCX files found in $docxDir" -ForegroundColor Red
    exit 1
}

Write-Host "📁 Found $($docxFiles.Count) DOCX file(s) to convert" -ForegroundColor Cyan
Write-Host ""

$successCount = 0
$failCount = 0

foreach ($docxFile in $docxFiles) {
    $fileName = $docxFile.BaseName
    $mdFileName = "$fileName.md"
    $imageDirName = "${fileName}_images"
    
    $inputPath = $docxFile.FullName
    $outputPath = Join-Path $outputDir $mdFileName
    $imagePath = Join-Path $outputDir $imageDirName
    
    Write-Host "🔄 Converting: $fileName" -ForegroundColor Yellow
    
    try {
        # Run pandoc command
        & pandoc -s $inputPath -o $outputPath -t gfm --extract-media=$imagePath
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Success: $mdFileName" -ForegroundColor Green
            
            # Check if images were extracted
            if (Test-Path $imagePath) {
                $imageCount = (Get-ChildItem -Path $imagePath -Recurse -File | Where-Object { $_.Extension -match '\.(png|jpg|jpeg|gif|bmp|svg)$' }).Count
                if ($imageCount -gt 0) {
                    Write-Host "   🖼️  Extracted $imageCount image(s) to $imageDirName" -ForegroundColor Cyan
                } else {
                    Write-Host "   ℹ️  No images found in this document" -ForegroundColor Gray
                }
            }
            
            $successCount++
        } else {
            Write-Host "❌ Failed: $fileName (Exit code: $LASTEXITCODE)" -ForegroundColor Red
            $failCount++
        }
    } catch {
        Write-Host "❌ Error converting $fileName : $_" -ForegroundColor Red
        $failCount++
    }
    
    Write-Host ""
}

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📊 Conversion Summary:" -ForegroundColor Cyan
Write-Host "   ✅ Successful: $successCount" -ForegroundColor Green
Write-Host "   ❌ Failed: $failCount" -ForegroundColor Red
Write-Host "   📁 Output directory: $outputDir" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
