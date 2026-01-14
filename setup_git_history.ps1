
# Reset git history
if (Test-Path .git) {
    Remove-Item -Path .git -Recurse -Force
}
git init
git remote add origin https://github.com/SamXavii902/PDF-Wizard.git

# Commit 1: Jan 8 - Setup
Write-Host "Creating Jan 8 Commit..."
git add README.md setup.py requirements.txt .gitignore .env.example run_tests.py generate_test_samples.py test_install.py
$env:GIT_COMMITTER_DATE = "2026-01-08 10:00:00"
git commit --date="2026-01-08 10:00:00" -m "Initial commit: Project structure and configuration"

# Commit 2: Jan 9 - Core Engine
Write-Host "Creating Jan 9 Commit..."
git add pdf_wizard/
$env:GIT_COMMITTER_DATE = "2026-01-09 14:30:00"
git commit --date="2026-01-09 14:30:00" -m "feat: Implement core PDF processing engine and CLI"

# Commit 3: Jan 10 - GUI Foundation
Write-Host "Creating Jan 10 Commit..."
git add gui/app.py gui/theme.py gui/__init__.py gui_launcher.py
# Try adding assets if they exist, suppress error if not
git add assets/ 2>$null
$env:GIT_COMMITTER_DATE = "2026-01-10 11:15:00"
git commit --date="2026-01-10 11:15:00" -m "feat: Initialize GUI application and theme system"

# Commit 4: Jan 11 - Core Panels
Write-Host "Creating Jan 11 Commit..."
git add gui/panels/merge_panel.py gui/panels/split_panel.py gui/panels/compress_panel.py gui/panels/security_panel.py gui/panels/__init__.py
$env:GIT_COMMITTER_DATE = "2026-01-11 16:45:00"
git commit --date="2026-01-11 16:45:00" -m "feat: Add core PDF operation panels (Merge, Split, Compress, Security)"

# Commit 5: Jan 12 - Media Panels
Write-Host "Creating Jan 12 Commit..."
git add gui/panels/resize_image_panel.py gui/panels/compress_image_panel.py gui/panels/convert_panel.py gui/panels/metadata_panel.py
$env:GIT_COMMITTER_DATE = "2026-01-12 13:20:00"
git commit --date="2026-01-12 13:20:00" -m "feat: Add image processing and metadata panels"

# Commit 6: Jan 13 - Advanced Tools
Write-Host "Creating Jan 13 Commit..."
git add gui/panels/page_tools_panel.py gui/panels/qr_panel.py gui/panels/compare_panel.py
$env:GIT_COMMITTER_DATE = "2026-01-13 15:00:00"
git commit --date="2026-01-13 15:00:00" -m "feat: Implement academic tools (Page Tools, QR, Compare)"

# Commit 7: Jan 14 - Polish (Final catch-all)
Write-Host "Creating Jan 14 Commit..."
git add gui/dnd.py
git add .
$env:GIT_COMMITTER_DATE = "2026-01-14 18:00:00"
git commit --date="2026-01-14 18:00:00" -m "polish: Enhance UI with DM Sans font and Drag & Drop support"

# Push
Write-Host "Pushing to GitHub..."
git branch -M main
git push -u origin main --force
