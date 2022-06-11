#listar todos los procesos
get-process

#listar los procesos filtrando por chrome
get-process | select-string "chrome"

#listar los procesos chrome formateando en una lista
get-process chrome | Format-List *

#listar los procesos chrome ordenando por ID
get-process chrome | Sort-Object -Property Id

#listar servicios
Get-Service

#ver el contenido de un fichero
Get-Content C:\Windows\System32\drivers\etc\hosts

#escribir en un fichero
"Hello, World!" | Out-File C:\ps\test.txt

#crear un nuevo directorio
New-Item -Path '\\fs\Shared\NewFolder' -ItemType Directory

#crear un nuevo fichero
New-Item -Path '\\fs\Shared\NewFolder\newfile.txt' -ItemType File

#eliminar un fichero
Remove-Item -Path '\\fs\shared\it\' -Recurse