; =====================================================================
; Script Inno Setup Compiler - IndexRadar Pro (v1.0.0)
; Membuat Windows Installer Resmi (.exe Setup Wizard)
; =====================================================================

#define MyAppName "IndexRadar Pro"
#define MyAppVersion "1.0.1"
#define MyAppPublisher "Skylark"
#define MyAppURL "https://github.com/silent404s/IndexRadar"
#define MyAppExeName "IndexRadar.exe"

[Setup]
; Identifikasi Unik Aplikasi (Konsisten antar versi agar menimpa instalasi lama)
AppId={{5F8A2D91-E41B-4712-B67D-89F3A981C021}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Direktori Instalasi Default & Timpa Direktori Sebelumnya Secara Bersih
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
UsePreviousAppDir=yes

; Icon Setup & Uninstaller
SetupIconFile=indexradar_icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

; Kompresi Maksimal
Compression=lzma2/max
SolidCompression=yes
OutputDir=Output
OutputBaseFilename=IndexRadar_Setup_v{#MyAppVersion}
WizardStyle=modern

; Hak Akses Instalasi User-Level (tanpa wajib admin)
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Otomatis Menutup & Mematikan Aplikasi Lama Jika Sedang Berjalan Saat Update
CloseApplications=yes
CloseApplicationsFilter=*IndexRadar*.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
; Executable Utama
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Assets & Icons
Source: "indexradar_icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "indexradar_icon.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "config.json.example"; DestDir: "{app}"; Flags: ignoreversion

; Konfigurasi Pengguna (Hanya dipasang jika belum ada agar setting API key tidak tertimpa saat update)
Source: "config.json.example"; DestDir: "{app}"; DestName: "config.json"; Flags: onlyifdoesntexist

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\indexradar_icon.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\indexradar_icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  Exec('taskkill.exe', '/F /T /IM "IndexRadar.exe"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;
