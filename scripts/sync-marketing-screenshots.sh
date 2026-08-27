#!/usr/bin/env bash

set -euo pipefail

site_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_root="${1:-"${site_root}/../Before-Leaving/Screenshots/Rendered/default"}"
quality="${WEBP_QUALITY:-86}"
app_icon_source="${APP_ICON_SOURCE:-"${site_root}/../Before-Leaving/Before Leaving/Images.xcassets/AppIcon.appiconset/ios-marketing-1024x1024.png"}"

command -v cwebp >/dev/null 2>&1 || {
    echo "cwebp is required. Install WebP tools before syncing screenshots." >&2
    exit 1
}

command -v sips >/dev/null 2>&1 || {
    echo "sips is required to generate the website icon variants." >&2
    exit 1
}

command -v magick >/dev/null 2>&1 || {
    echo "ImageMagick is required to generate favicon.ico." >&2
    exit 1
}

scenes=(
    01_departure
    02_assistant
    03_location
    04_travel
    06_ecosystem
    07_pet_care
    08_plant_care
    09_groups
    11_errands
)

sync_profile() {
    local source_profile="$1"
    local destination_profile="$2"
    local source_directory="${source_root}/${source_profile}/en_US"
    local destination_directory="${site_root}/images/marketing/${destination_profile}"

    mkdir -p "${destination_directory}"

    for scene in "${scenes[@]}"; do
        local source_file="${source_directory}/${scene}.png"
        local destination_file="${destination_directory}/${scene}.webp"

        if [[ ! -f "${source_file}" ]]; then
            echo "Missing marketing screenshot: ${source_file}" >&2
            exit 1
        fi

        cwebp -quiet -q "${quality}" -m 6 -af "${source_file}" -o "${destination_file}"
    done
}

sync_profile "official" "iphone"
sync_profile "official-ipad" "ipad"

if [[ ! -f "${app_icon_source}" ]]; then
    echo "Missing App Store icon: ${app_icon_source}" >&2
    exit 1
fi

cp "${app_icon_source}" "${site_root}/images/app-icon-large.png"
sips -z 180 180 "${app_icon_source}" --out "${site_root}/images/app-icon.png" >/dev/null
cp "${site_root}/images/app-icon.png" "${site_root}/apple-touch-icon.png"
sips -z 32 32 "${app_icon_source}" --out "${site_root}/favicon.png" >/dev/null
magick "${app_icon_source}" -resize 32x32 "${site_root}/favicon.ico"

echo "Updated ${#scenes[@]} iPhone screenshots, ${#scenes[@]} iPad screenshots, and all website app icons."
