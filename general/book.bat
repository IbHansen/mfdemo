@echo off
rem Run the shared launcher for this book, from this folder.
rem All options are in one place:  book --help   (C:\deploy\books\start_book.bat)
cd /d "%~dp0"
call C:\deploy\books\start_book.bat %*
