@echo off
echo === Hire Me Backend Setup ===
echo.

echo Step 1: Creating virtual environment...
python -m venv venv
if errorlevel 1 goto error

echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat

echo Step 3: Upgrading pip...
python -m pip install --upgrade pip

echo Step 4: Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 goto error

echo Step 5: Creating migrations...
python manage.py makemigrations
if errorlevel 1 goto error

echo Step 6: Running migrations...
python manage.py migrate
if errorlevel 1 goto error

echo.
echo === Setup Complete! ===
echo.
echo To create a superuser, run: python manage.py createsuperuser
echo To run tests, run: pytest
echo To start the server, run: python manage.py runserver
echo.
goto end

:error
echo.
echo === Setup Failed! ===
echo Please check the error messages above.
exit /b 1

:end
