@echo off
echo Dark Pattern Annotation Server
echo =============================
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting server...
echo.
echo The interface will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python annotation_server.py
pause 