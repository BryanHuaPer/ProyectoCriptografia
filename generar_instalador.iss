[Setup]
; Información básica de la aplicación
AppName=CryptoVA
AppVersion=1.0.0
AppPublisher=UNJBG - Ingeniería de Sistemas
; Carpeta de instalación por defecto (Archivos de Programa)
DefaultDirName={autopf}\CryptoVA
DefaultGroupName=CryptoVA
; Dónde se guardará el instalador final y cómo se llamará
OutputDir=.\InstaladorFinal
OutputBaseFilename=Instalador_CryptoVA
Compression=lzma2/max
SolidCompression=yes
; Opcional: configurar un ícono para el instalador
; SetupIconFile=icono.ico

[Tasks]
Name: "desktopicon"; Description: "Crear un acceso directo en el escritorio"; GroupDescription: "Accesos directos adicionales:"

[Files]
; NOTA: Si tu ejecutable no está directamente en "build\windows", actualiza estas dos líneas
; con la ruta correcta (por ejemplo, "build\windows\x64\runner\Release\cryptova.exe")
Source: "build\windows\cryptova.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\windows\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Crea los accesos directos en el Menú Inicio y en el Escritorio
Name: "{group}\CryptoVA"; Filename: "{app}\cryptova.exe"
Name: "{autodesktop}\CryptoVA"; Filename: "{app}\cryptova.exe"; Tasks: desktopicon

[Run]
; Permite ejecutar la aplicación justo al terminar la instalación
Filename: "{app}\cryptova.exe"; Description: "Ejecutar CryptoVA"; Flags: nowait postinstall skipifsilent
