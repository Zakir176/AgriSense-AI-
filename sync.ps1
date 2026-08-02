# AgriSense-AI Sync Script
# Syncs frontend/ to https://github.com/Zakir176/AgriSense-AI-Frontend.git
# Syncs backend/ to https://github.com/Zakir176/AgriSense-AI-Backend.git

Param(
    [string]$TargetBranch = "main"
)

Write-Host "Syncing frontend folder to deployment-frontend repository ($TargetBranch)..." -ForegroundColor Cyan
git subtree split --prefix=frontend -b temp-front-sync
git push deployment-frontend temp-front-sync:${TargetBranch} --force
git branch -D temp-front-sync

Write-Host "`nSyncing backend folder to deployment-backend repository ($TargetBranch)..." -ForegroundColor Cyan
git subtree split --prefix=backend -b temp-back-sync
git push deployment-backend temp-back-sync:${TargetBranch} --force
git branch -D temp-back-sync

Write-Host "`nSync completed successfully!" -ForegroundColor Green
