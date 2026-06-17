#!/usr/bin/env bash
# Build Linux binary, .deb, and .AppImage
set -euo pipefail
cd "$(dirname "$0")/.."

VERSION="${1:-dev}"
BINARY_NAME="cathkb"
BUILD_DIR="build/linux"
DIST_DIR="dist"

echo "=== Building Linux binary ==="

pip install pyinstaller
pyinstaller --onefile --name "$BINARY_NAME" kb_tools/cli/main.py

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/usr/bin"
mkdir -p "$BUILD_DIR/usr/share/cathkb"
mkdir -p "$BUILD_DIR/usr/share/applications"
mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/256x256/apps"

cp "dist/$BINARY_NAME" "$BUILD_DIR/usr/bin/$BINARY_NAME"
chmod +x "$BUILD_DIR/usr/bin/$BINARY_NAME"

# Bundle data
if [ -f "dist/cathkb-data.tar.gz" ]; then
    tar xzf "dist/cathkb-data.tar.gz" -C "$BUILD_DIR/usr/share/cathkb/"
fi

# Desktop entry
cat > "$BUILD_DIR/usr/share/applications/cathkb.desktop" << EOF
[Desktop Entry]
Name=Catholic Knowledge System
Comment=Local-first Catholic doctrinal reasoning engine
Exec=/usr/bin/cathkb serve --no-browser
Icon=cathkb
Terminal=true
Type=Application
Categories=Education;Religion;
EOF

echo "=== Building .deb package ==="

# Build .deb
if command -v dpkg-deb &>/dev/null; then
    DEB_DIR="build/deb"
    rm -rf "$DEB_DIR"
    mkdir -p "$DEB_DIR/DEBIAN"
    mkdir -p "$DEB_DIR/usr"

    cp -r "$BUILD_DIR/usr" "$DEB_DIR/"

    cat > "$DEB_DIR/DEBIAN/control" << EOF
Package: cathkb
Version: $VERSION
Section: education
Priority: optional
Architecture: $(dpkg --print-architecture 2>/dev/null || echo "amd64")
Depends: libc6
Maintainer: Catholic Knowledge System <noreply@example.com>
Description: Catholic Sovereign Knowledge System
 Local-first Catholic doctrinal reasoning engine with 212
 authoritative documents, full-text search, and cited responses.
 All processing is local via Ollama.
EOF

    dpkg-deb --build "$DEB_DIR" "$DIST_DIR/cathkb-${VERSION}-linux.deb"
    echo "=== .deb created: $DIST_DIR/cathkb-${VERSION}-linux.deb ==="
else
    echo "=== Skipping .deb (dpkg-deb not available) ==="
fi

echo "=== Building .AppImage ==="

# Build AppImage
if command -v appimagetool &>/dev/null || [ -f "./appimagetool ]; then
    APPDIR="build/AppDir"
    rm -rf "$APPDIR"
    mkdir -p "$APPDIR/usr/bin"
    mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"
    mkdir -p "$APPDIR/usr/share/applications"

    cp "dist/$BINARY_NAME" "$APPDIR/usr/bin/"
    cp "$BUILD_DIR/usr/share/applications/cathkb.desktop" "$APPDIR/usr/share/applications/"
    cp "$BUILD_DIR/usr/share/cathkb" -r "$APPDIR/usr/share/" 2>/dev/null || true

    cat > "$APPDIR/AppRun" << 'APPRUN'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
export XDG_DATA_DIRS="${HERE}/usr/share:${XDG_DATA_DIRS:-/usr/local/share:/usr/share}"
exec cathkb serve --no-browser "$@"
APPRUN
    chmod +x "$APPDIR/AppRun"

    if command -v appimagetool &>/dev/null; then
        appimagetool "$APPDIR" "$DIST_DIR/cathkb-${VERSION}-linux.AppImage"
        echo "=== .AppImage created ==="
    else
        echo "=== appimagetool not found, skipping .AppImage ==="
    fi
else
    echo "=== Skipping .AppImage (appimagetool not available) ==="
fi

echo "=== Linux build complete ==="
