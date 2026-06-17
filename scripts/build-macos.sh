#!/usr/bin/env bash
# Build macOS .app bundle and .dmg
set -euo pipefail
cd "$(dirname "$0")/.."

APP_NAME="Catholic Knowledge System"
APP_ID="com.cathkb.app"
VERSION="${1:-dev}"
BUILD_DIR="build/macos"
DIST_DIR="dist"
BINARY_NAME="cathkb"

echo "=== Building macOS .app bundle ==="

# Clean
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/$APP_NAME.app/Contents/MacOS"
mkdir -p "$BUILD_DIR/$APP_NAME.app/Contents/Resources"

# Build PyInstaller binary
pip install pyinstaller
pyinstaller --onefile --name "$BINARY_NAME" kb_tools/cli/main.py
cp "dist/$BINARY_NAME" "$BUILD_DIR/$APP_NAME.app/Contents/MacOS/$BINARY_NAME"

# Create launcher script
cat > "$BUILD_DIR/$APP_NAME.app/Contents/MacOS/$APP_NAME" << 'LAUNCHER'
#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
exec "$DIR/cathkb" serve --no-browser "$@"
LAUNCHER
chmod +x "$BUILD_DIR/$APP_NAME.app/Contents/MacOS/$APP_NAME"

# Info.plist
cat > "$BUILD_DIR/$APP_NAME.app/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>$APP_NAME</string>
    <key>CFBundleDisplayName</key>
    <string>$APP_NAME</string>
    <key>CFBundleIdentifier</key>
    <string>$APP_ID</string>
    <key>CFBundleVersion</key>
    <string>$VERSION</string>
    <key>CFBundleShortVersionString</key>
    <string>$VERSION</string>
    <key>CFBundleExecutable</key>
    <string>$APP_NAME</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>11.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.education</string>
</dict>
</plist>
EOF

# Bundle data archive if it exists
if [ -f "dist/cathkb-data.tar.gz" ]; then
    cp "dist/cathkb-data.tar.gz" "$BUILD_DIR/$APP_NAME.app/Contents/Resources/"
fi

echo "=== Creating .dmg ==="

# Install create-dmg if not available
if ! command -v create-dmg &>/dev/null; then
    brew install create-dmg 2>/dev/null || echo "Warning: create-dmg not found, skipping .dmg creation"
fi

if command -v create-dmg &>/dev/null; then
    DMG_NAME="cathkb-${VERSION}-macos.dmg"
    mkdir -p "$DIST_DIR"
    create-dmg \
        --volname "$APP_NAME" \
        --window-pos 200 120 \
        --window-size 600 400 \
        --icon-size 100 \
        --icon "$APP_NAME.app" 175 190 \
        --hide-extension "$APP_NAME.app" \
        --app-drop-link 425 190 \
        "$DIST_DIR/$DMG_NAME" \
        "$BUILD_DIR/$APP_NAME.app"
    echo "=== DMG created: $DIST_DIR/$DMG_NAME ==="
else
    echo "=== Skipping .dmg (create-dmg not available) ==="
    echo "=== .app bundle at: $BUILD_DIR/$APP_NAME.app ==="
fi
