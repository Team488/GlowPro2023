REM delete any existing python files so we know it's only going to run our new ones
del d:\*.py
REM copy over our python files
xcopy *.py d:\ /Y
REM copy over our lib files
xcopy lib d:\lib /Y