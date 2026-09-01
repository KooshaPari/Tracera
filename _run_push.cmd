@echo off
cd /d E:\Dev\Tracera
git push origin fix/tracera-ci-repair > push_repair.log 2>&1
echo EXITCODE=%ERRORLEVEL% >> push_repair.log