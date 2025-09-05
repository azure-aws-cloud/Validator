# Convert python code to exe

```
EXE using python ui code for validation checks
create a folder config in c:\test\config and add config.xml inside it, 
the config.xml should contain a tag <DECAutoName>false</DECAutoName> 
```
```
pyinstaller --onefile --windowed edat_checker.py 
```
# Go to dist directory and run the exec edat_checker.exe