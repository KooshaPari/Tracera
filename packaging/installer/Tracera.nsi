; Tracera Installer Script (NSIS)
; Builds a proper Windows installer for Tracera v2.2.0

Unicode True

;--------------------------------
; General

Name "Tracera"
OutFile "Tracera-Setup-2.2.0.exe"
InstallDir "$PROGRAMFILES64\Tracera"
InstallDirRegKey HKLM "Software\Tracera" "Install_Dir"
RequestExecutionLevel admin
ShowInstDetails show

;--------------------------------
; Modern UI

!include "MUI2.nsh"

!define MUI_ABORTWARNING
!define MUI_ICON "tracera.ico"
!define MUI_UNICON "tracera.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "header.bmp"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Install Section

Section "Tracera Server (required)"
    SectionIn RO

    SetOutPath "$INSTDIR\bin"
    File "..\target\release\tracera-server.exe"
    File "..\target\release\tracera.exe"
    File "..\Cargo.toml"

    SetOutPath "$INSTDIR"
    File "LICENSE.txt"
    File "README.md"
    File "..\SECURITY.md"

    SetOutPath "$INSTDIR\frontend\apps\web\dist"
    File /r "..\frontend\apps\web\dist\*"

    SetOutPath "$INSTDIR\docs"
    File /r "..\docs\*"

    WriteRegStr HKLM "Software\Tracera" "Install_Dir" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Tracera" "DisplayName" "Tracera - Requirements Traceability"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Tracera" "UninstallString" '"$INSTDIR\Uninstall.exe"'
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Tracera" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Tracera" "NoRepair" 1
SectionEnd

Section "Start Menu Shortcuts"
    CreateDirectory "$SMPROGRAMS\PhenotypeApps"
    CreateShortcut "$SMPROGRAMS\PhenotypeApps\Tracera.lnk" "$INSTDIR\bin\tracera-server.exe" "--port 8080" "$INSTDIR"
    CreateShortcut "$SMPROGRAMS\PhenotypeApps\Tracera CLI.lnk" "$INSTDIR\bin\tracera.exe" "" "$INSTDIR"
SectionEnd

Section "Desktop Shortcut"
    CreateShortcut "$DESKTOP\Tracera.lnk" "$INSTDIR\bin\tracera-server.exe" "--port 8080" "$INSTDIR"
SectionEnd

Section "Path Environment Variable"
    Push "$INSTDIR\bin"
    Call AddToPath
SectionEnd

;--------------------------------
; Uninstaller

Section "Uninstall"
    RMDir /r "$INSTDIR"
    RMDir /r "$SMPROGRAMS\PhenotypeApps\Tracera"
    Delete "$DESKTOP\Tracera.lnk"

    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Tracera"
    DeleteRegKey HKLM "Software\Tracera"

    Push "$INSTDIR\bin"
    Call un.RemoveFromPath
SectionEnd

;--------------------------------
; Path manipulation (from NSIS docs)

!include "WordFunc.nsh"

!define env_hk 'HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment'

Function AddToPath
    Exch $0
    Push $1
    Push $2
    Push $3

    ReadRegStr $1 ${env_hk} "PATH"
    ; Check if path already contains our install dir
    StrStr $2 "$1" "$0"
    StrCmp $2 "" 0 next
    ; Append to PATH
    StrCmp $1 ""
        WriteRegExpandStr ${env_hk} "PATH" "$0"
    StrCpy $2 "$1;$0"
    WriteRegExpandStr ${env_hk} "PATH" "$2"
    SendMessage ${HWND_BROADCAST} ${WM_WININICHANGE} 0 "STR:Environment" /TIMEOUT=5000
    next:
    Pop $3
    Pop $2
    Pop $1
    Pop $0
FunctionEnd

Function un.RemoveFromPath
    Exch $0
    Push $1
    Push $2
    Push $3
    Push $4

    ReadRegStr $1 ${env_hk} "PATH"

    StrLen $2 "$0"
    StrCpy $3 $1
    loop:
    StrStr $4 $3 "$0"
    StrCmp $4 "" done
       StrCpy $3 $4 "" $2
       StrCpy $4 $3 1 -1
       StrCmp $4 ";" 0 loop
       StrCpy $3 $3 -1
       Goto loop

    done:
    StrCpy $4 $3 1 -1
    StrCmp $4 ";" +1 copy
       StrCpy $3 $3 -1
    copy:
    StrCmp $3 "" +1 path_exists
       WriteRegExpandStr ${env_hk} "PATH" ""
    Goto path_done
    path_exists:
    WriteRegExpandStr ${env_hk} "PATH" "$3"
    path_done:
    SendMessage ${HWND_BROADCAST} ${WM_WININICHANGE} 0 "STR:Environment" /TIMEOUT=5000

    Pop $4
    Pop $3
    Pop $2
    Pop $1
    Pop $0
FunctionEnd
