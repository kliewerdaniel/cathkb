; Catholic Knowledge System - NSIS Installer Script
; Requires NSIS (https://nsis.sourceforge.io/)
; Pass /DVERSION=x.x.x /DBINARYPATH=path /DDATAPATH=path to makensis

!include "MUI2.nsh"

Name "Catholic Knowledge System"
OutFile "dist\cathkb-${VERSION}-windows.exe"
InstallDir "$PROGRAMFILES\Catholic Knowledge System"
InstallDirRegKey HKLM "Software\Catholic Knowledge System" "InstallDir"
RequestExecutionLevel admin

!define MUI_ABORTWARNING

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; License page (optional)
!insertmacro MUI_PAGE_LICENSE "LICENSE"
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Install files
!insertmacro MUI_PAGE_INSTFILES
; Finish page - offer to launch
!define MUI_FINISHPAGE_RUN "$INSTDIR\cathkb.exe"
!define MUI_FINISHPAGE_RUN_PARAMETERS "serve"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Language
!insertmacro MUI_LANGUAGE "English"

Section "Install"
    SetOutPath "$INSTDIR"

    ; Main binary
    File "${BINARYPATH}"

    ; Data archive if present
    IfFileExists "${DATAPATH}" 0 +2
        File "${DATAPATH}"

    ; Create uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"

    ; Registry entries
    WriteRegStr HKLM "Software\Catholic Knowledge System" "InstallDir" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Catholic Knowledge System" \
        "DisplayName" "Catholic Knowledge System"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Catholic Knowledge System" \
        "UninstallString" '"$INSTDIR\uninstall.exe"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Catholic Knowledge System" \
        "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Catholic Knowledge System" \
        "DisplayVersion" "${VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Catholic Knowledge System" \
        "Publisher" "Catholic Knowledge System"

    ; Start Menu shortcuts
    CreateDirectory "$SMPROGRAMS\Catholic Knowledge System"
    CreateShortCut "$SMPROGRAMS\Catholic Knowledge System\Catholic Knowledge System.lnk" \
        "$INSTDIR\cathkb.exe" "serve" "$INSTDIR\cathkb.exe"
    CreateShortCut "$SMPROGRAMS\Catholic Knowledge System\Uninstall.lnk" \
        "$INSTDIR\uninstall.exe"
SectionEnd

Section "Uninstall"
    ; Remove files
    Delete "$INSTDIR\cathkb.exe"
    Delete "$INSTDIR\cathkb-data.tar.gz"
    Delete "$INSTDIR\uninstall.exe"
    RMDir "$INSTDIR"

    ; Remove Start Menu shortcuts
    Delete "$SMPROGRAMS\Catholic Knowledge System\Catholic Knowledge System.lnk"
    Delete "$SMPROGRAMS\Catholic Knowledge System\Uninstall.lnk"
    RMDir "$SMPROGRAMS\Catholic Knowledge System"

    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Catholic Knowledge System"
    DeleteRegKey HKLM "Software\Catholic Knowledge System"
SectionEnd
