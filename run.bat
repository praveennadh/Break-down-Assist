@echo off

REM Start the Flask server in the background
start /B python app.py

REM Wait for a few seconds (adjust as needed) to ensure the server starts up
timeout /T 5

REM Open the default web browser to the specified URL
start "" "http://127.0.0.1:5000"
