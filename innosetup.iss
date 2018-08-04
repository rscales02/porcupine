; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define PorcupineVersion "X.Y.Z"     ; replaced with an actual version in windows-build.py
#define PorcupineURL "https://github.com/Akuli/porcupine"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{9CBB67ED-8435-4284-8C20-84B7E6BFF145}
AppName=Porcupine
AppVersion={#PorcupineVersion}
;AppVerName=Porcupine {#PorcupineVersion}
AppPublisherURL={#PorcupineURL}
AppSupportURL={#PorcupineURL}
AppUpdatesURL={#PorcupineURL}
DefaultDirName={pf}\Porcupine
DisableProgramGroupPage=yes
LicenseFile=LICENSE
OutputDir=.
OutputBaseFilename=porcupine-setup
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "windows-build\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

; TODO: fix the icons
[Icons]
Name: "{commonprograms}\Porcupine"; Filename: "{app}\python\python.exe"; Parameters: "-m porcupine"
Name: "{commondesktop}\Porcupine"; Filename: "{app}\python\python.exe"; Parameters: "-m porcupine"; Tasks: desktopicon

[Run]
Filename: "{app}\python\python.exe"; Parameters: "-m porcupine"; Description: "{cm:LaunchProgram,Porcupine}"; Flags: nowait postinstall skipifsilent
