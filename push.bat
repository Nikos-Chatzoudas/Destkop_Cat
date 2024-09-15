@echo off

set commit_message=cat

git add .
git commit -m "%commit_message%"
git push