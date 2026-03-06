param(
  [Parameter(Mandatory = $true)]
  [string]$RepoUrl,
  [string]$Message = "chore: update ai news digest"
)

Set-Location (Join-Path $PSScriptRoot "..")

if (-not (Test-Path ".git")) {
  git init
  git branch -M main
}

git add .
git commit -m $Message

git remote get-url origin *> $null
if ($LASTEXITCODE -ne 0) {
  git remote add origin $RepoUrl
} else {
  git remote set-url origin $RepoUrl
}

git push -u origin main
