param(
    [Parameter(Mandatory = $true)]
    [string]$InputDocx,
    [Parameter(Mandatory = $true)]
    [string]$OutputDirectory
)

$ErrorActionPreference = "Stop"
$inputPath = (Resolve-Path -LiteralPath $InputDocx).Path
$outputPath = [System.IO.Path]::GetFullPath(
    (Join-Path -Path (Get-Location) -ChildPath $OutputDirectory)
)
[System.IO.Directory]::CreateDirectory($outputPath) | Out-Null
$pdfPath = Join-Path -Path $outputPath -ChildPath (
    [System.IO.Path]::GetFileNameWithoutExtension($inputPath) + ".pdf"
)

$word = $null
$document = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $document = $word.Documents.Open($inputPath, $false, $true)
    # SaveAs2 is more reliable than ExportAsFixedFormat for image-rich reports
    # in the installed Word 16 COM runtime. Format 17 is PDF.
    $document.SaveAs2($pdfPath, 17)
}
finally {
    if ($null -ne $document) {
        $document.Close($false)
    }
    if ($null -ne $word) {
        $word.Quit()
    }
}

$pagePrefix = Join-Path -Path $outputPath -ChildPath "page"
& pdftoppm -png -r 150 $pdfPath $pagePrefix
if ($LASTEXITCODE -ne 0) {
    throw "pdftoppm failed with exit code $LASTEXITCODE"
}

Get-ChildItem -LiteralPath $outputPath -Filter "page-*.png" |
    Sort-Object Name |
    Select-Object FullName, Length
