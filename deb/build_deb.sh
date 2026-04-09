#!/bin/bash

set -e

COMPRESSORS="gzip xz zstd bzip2 lzma none"

usage() {
    echo "Usage: $0 -v <folder> [-s] [-a <compressor> <level>]"
    echo ""
    echo "  -v <folder>              Path to the folder with deb package structure"
    echo "  -s                       Interactively select compressor and compression level"
    echo "  -a <compressor> <level>  Set compressor and level directly"
    echo ""
    echo "  Compressors: $COMPRESSORS"
    echo "  Level: 1-9 (not applicable for 'none')"
    exit 1
}

validate_compressor() {
    local c="$1"
    for valid in $COMPRESSORS; do
        [ "$c" = "$valid" ] && return 0
    done
    return 1
}

validate_level() {
    local l="$1"
    [[ "$l" =~ ^[1-9]$ ]]
}

FOLDER=""
COMPRESSOR=""
LEVEL=""
INTERACTIVE=0

# Manual arg parsing to support -a <compressor> <level> (two args after flag)
while [ $# -gt 0 ]; do
    case "$1" in
        -v) FOLDER="$2"; shift 2 ;;
        -s) INTERACTIVE=1; shift ;;
        -a)
            COMPRESSOR="$2"
            LEVEL="$3"
            shift 3
            ;;
        -h|--help) usage ;;
        *) echo "Error: Unknown option '$1'"; usage ;;
    esac
done

if [ -z "$FOLDER" ]; then
    echo "Error: -v <folder> is required"
    usage
fi

# Validate -a arguments
if [ -n "$COMPRESSOR" ]; then
    if ! validate_compressor "$COMPRESSOR"; then
        echo "Error: Unknown compressor '$COMPRESSOR'. Valid: $COMPRESSORS"
        exit 1
    fi
    if [ "$COMPRESSOR" != "none" ] && [ -z "$LEVEL" ]; then
        echo "Error: -a requires a level (1-9) after the compressor"
        exit 1
    fi
    if [ -n "$LEVEL" ] && ! validate_level "$LEVEL"; then
        echo "Error: Invalid level '$LEVEL'. Must be 1-9"
        exit 1
    fi
fi

# Interactive mode
if [ "$INTERACTIVE" = 1 ]; then
    if [ -n "$COMPRESSOR" ]; then
        echo "Warning: -s ignored because -a is already set"
    else
        echo "Available compressors: $COMPRESSORS"
        while true; do
            read -rp "Compressor: " COMPRESSOR
            if validate_compressor "$COMPRESSOR"; then
                break
            fi
            echo "  Invalid compressor. Try again."
        done

        if [ "$COMPRESSOR" != "none" ]; then
            while true; do
                read -rp "Compression level (1-9): " LEVEL
                if validate_level "$LEVEL"; then
                    break
                fi
                echo "  Invalid level. Enter a number from 1 to 9."
            done
        fi
    fi
fi

if [ ! -d "$FOLDER" ]; then
    echo "Error: '$FOLDER' is not a directory or does not exist"
    exit 1
fi

if [ ! -d "$FOLDER/DEBIAN" ]; then
    echo "Error: '$FOLDER/DEBIAN' directory not found"
    exit 1
fi

if [ ! -f "$FOLDER/DEBIAN/control" ]; then
    echo "Error: '$FOLDER/DEBIAN/control' file not found"
    exit 1
fi

# Get package name and version from control file
PKG_NAME=$(grep -i "^Package:" "$FOLDER/DEBIAN/control" | awk '{print $2}')
PKG_VERSION=$(grep -i "^Version:" "$FOLDER/DEBIAN/control" | awk '{print $2}')
PKG_ARCH=$(grep -i "^Architecture:" "$FOLDER/DEBIAN/control" | awk '{print $2}')

if [ -z "$PKG_NAME" ] || [ -z "$PKG_VERSION" ] || [ -z "$PKG_ARCH" ]; then
    echo "Error: Could not read Package, Version or Architecture from control file"
    exit 1
fi

OUTPUT="${PKG_NAME}_${PKG_VERSION}_${PKG_ARCH}.deb"

echo "Building: $OUTPUT"
echo "  Package:      $PKG_NAME"
echo "  Version:      $PKG_VERSION"
echo "  Architecture: $PKG_ARCH"
echo "  Source:       $FOLDER"
if [ -n "$COMPRESSOR" ]; then
    echo "  Compressor:   $COMPRESSOR${LEVEL:+ (level $LEVEL)}"
fi

# Fix permissions on DEBIAN scripts
for script in preinst postinst prerm postrm; do
    if [ -f "$FOLDER/DEBIAN/$script" ]; then
        chmod 755 "$FOLDER/DEBIAN/$script"
    fi
done

# Build compression flags
COMPRESS_FLAGS=()
if [ -n "$COMPRESSOR" ]; then
    COMPRESS_FLAGS+=("-Z$COMPRESSOR")
    if [ -n "$LEVEL" ] && [ "$COMPRESSOR" != "none" ]; then
        COMPRESS_FLAGS+=("-z$LEVEL")
    fi
fi

dpkg-deb --build --root-owner-group "${COMPRESS_FLAGS[@]}" "$FOLDER" "$OUTPUT"

echo ""
echo "Done: $OUTPUT"