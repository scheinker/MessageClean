#!/usr/bin/env python3
"""
Bulk Image Importer - Phase 1 of Messages Cleanup

This script handles the massive number of images in iMessage attachments by:
1. Scanning for all image files
2. Bulk importing to Photos (Photos handles duplicate detection)
3. Moving images to review folder (not deleting)
4. Creating detailed log

Safe because:
- Photos automatically detects and handles duplicates
- Images are moved (not deleted) to review folder
- You verify Photos has everything before final cleanup
- Detailed logging of all actions

Author: Created for safe cleanup of Messages storage
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Configuration
ATTACHMENTS_DIR = Path.home() / 'Library' / 'Messages' / 'Attachments'
PHOTOS_LIBRARY = Path.home() / 'Pictures' / 'Photos Library.photoslibrary'
DESKTOP = Path.home() / 'Desktop'

# Output locations
REVIEW_DIR = DESKTOP / 'iMessage_Images_REVIEW'
IMPORT_LOG = DESKTOP / 'iMessage_Image_Import_Log.txt'

# Image extensions to process
IMAGE_EXTENSIONS = [
    '.jpg', '.jpeg', '.png', '.gif', '.heic', '.heif',
    '.bmp', '.tiff', '.tif', '.webp', '.svg'
]


def format_size(bytes_size):
    """Format bytes to human-readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


def log_message(message, log_file=None):
    """Log message to console and optionally to file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    if log_file:
        with open(log_file, 'a') as f:
            f.write(log_entry + '\n')


def scan_images():
    """Scan for all image files in iMessage attachments"""
    print("=" * 80)
    print("Bulk Image Importer - Phase 1")
    print("=" * 80)
    print()
    print(f"Scanning: {ATTACHMENTS_DIR}")
    print("This may take 1-2 minutes...")
    print()

    # Check permissions
    if not ATTACHMENTS_DIR.exists():
        print(f"ERROR: Attachments directory not found: {ATTACHMENTS_DIR}")
        return None

    try:
        _ = list(ATTACHMENTS_DIR.iterdir())
    except PermissionError:
        print("=" * 80)
        print("PERMISSION DENIED")
        print("=" * 80)
        print()
        print("Terminal needs Full Disk Access.")
        print("See README for instructions on how to grant access.")
        return None

    # Find all image files
    image_files = []
    extension_stats = defaultdict(lambda: {'count': 0, 'size': 0})

    for ext in IMAGE_EXTENSIONS:
        found = list(ATTACHMENTS_DIR.rglob(f'*{ext}'))
        found.extend(ATTACHMENTS_DIR.rglob(f'*{ext.upper()}'))

        for img_path in found:
            try:
                size = img_path.stat().st_size
                image_files.append({
                    'path': img_path,
                    'size': size,
                    'ext': ext
                })
                extension_stats[ext]['count'] += 1
                extension_stats[ext]['size'] += size
            except Exception as e:
                print(f"Warning: Could not process {img_path.name}: {e}")

    return image_files, extension_stats


def show_summary(image_files, extension_stats):
    """Display summary of found images"""
    if not image_files:
        print("No image files found in iMessage attachments.")
        return False

    total_count = len(image_files)
    total_size = sum(img['size'] for img in image_files)

    print("=" * 80)
    print("FOUND IMAGES")
    print("=" * 80)
    print(f"Total images: {total_count:,}")
    print(f"Total size: {format_size(total_size)}")
    print()

    print("Breakdown by type:")
    print("-" * 80)
    sorted_exts = sorted(extension_stats.items(), key=lambda x: x[1]['size'], reverse=True)
    for ext, stats in sorted_exts:
        count = stats['count']
        size = stats['size']
        pct = (size / total_size * 100) if total_size > 0 else 0
        print(f"  {ext:8} : {count:6,} files | {format_size(size):>10} ({pct:5.1f}%)")
    print()

    return True


def confirm_proceed():
    """Ask user for confirmation"""
    print("=" * 80)
    print("WHAT WILL HAPPEN")
    print("=" * 80)
    print()
    print("1. Import all images to Photos app")
    print("   - Photos will automatically detect duplicates")
    print("   - Duplicates will be handled gracefully (not imported twice)")
    print()
    print("2. Move images from iMessage to review folder:")
    print(f"   {REVIEW_DIR}")
    print()
    print("3. Create detailed log:")
    print(f"   {IMPORT_LOG}")
    print()
    print("4. You verify Photos has everything")
    print()
    print("5. When satisfied, you manually delete the review folder")
    print()
    print("=" * 80)
    print()

    while True:
        response = input("Do you want to proceed? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Please enter 'yes' or 'no'")


def import_to_photos(image_files, log_file):
    """Import images to Photos using AppleScript"""
    log_message("=" * 80, log_file)
    log_message("IMPORTING TO PHOTOS", log_file)
    log_message("=" * 80, log_file)
    log_message("", log_file)

    total = len(image_files)
    imported = 0
    failed = 0
    failed_files = []

    # Import in batches to avoid overwhelming Photos
    batch_size = 50
    batches = [image_files[i:i + batch_size] for i in range(0, len(image_files), batch_size)]

    for batch_num, batch in enumerate(batches, 1):
        print(f"\nImporting batch {batch_num} of {len(batches)} ({len(batch)} images)...")

        for i, img_data in enumerate(batch):
            img_path = img_data['path']
            try:
                # Import to Photos using AppleScript
                script = f'''
                    tell application "Photos"
                        activate
                        import POSIX file "{img_path}" skip check duplicates false
                    end tell
                '''
                result = subprocess.run(
                    ['osascript', '-e', script],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    imported += 1
                    if (i + 1) % 10 == 0:
                        print(f"  Progress: {imported}/{total} imported...")
                else:
                    failed += 1
                    failed_files.append(str(img_path))
                    log_message(f"  FAILED to import: {img_path.name}", log_file)

            except Exception as e:
                failed += 1
                failed_files.append(str(img_path))
                log_message(f"  ERROR importing {img_path.name}: {e}", log_file)

        # Small delay between batches
        if batch_num < len(batches):
            import time
            time.sleep(2)

    log_message("", log_file)
    log_message(f"Import complete: {imported} succeeded, {failed} failed", log_file)

    return imported, failed, failed_files


def move_to_review_folder(image_files, failed_files, log_file):
    """Move images to review folder"""
    log_message("=" * 80, log_file)
    log_message("MOVING TO REVIEW FOLDER", log_file)
    log_message("=" * 80, log_file)
    log_message("", log_file)

    # Create review directory
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)

    moved = 0
    move_failed = 0
    skipped = 0

    for img_data in image_files:
        img_path = img_data['path']

        # Skip files that failed to import
        if str(img_path) in failed_files:
            skipped += 1
            log_message(f"  SKIPPED (import failed): {img_path.name}", log_file)
            continue

        try:
            # Create subdirectory structure to avoid name conflicts
            rel_path = img_path.relative_to(ATTACHMENTS_DIR)
            target_path = REVIEW_DIR / rel_path

            # Create parent directories
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Move the file
            shutil.move(str(img_path), str(target_path))
            moved += 1

            if moved % 100 == 0:
                print(f"  Moved {moved} files...")

        except Exception as e:
            move_failed += 1
            log_message(f"  ERROR moving {img_path.name}: {e}", log_file)

    log_message("", log_file)
    log_message(f"Move complete: {moved} moved, {move_failed} failed, {skipped} skipped", log_file)

    return moved, move_failed, skipped


def main():
    """Main execution"""
    try:
        # Initialize log
        if IMPORT_LOG.exists():
            IMPORT_LOG.unlink()

        log_message("Bulk Image Importer started", IMPORT_LOG)
        log_message("", IMPORT_LOG)

        # Scan for images
        result = scan_images()
        if result is None:
            return 1

        image_files, extension_stats = result

        # Show summary
        if not show_summary(image_files, extension_stats):
            return 0

        # Get confirmation
        if not confirm_proceed():
            print("\nOperation cancelled by user.")
            return 0

        print()
        print("=" * 80)
        print("STARTING IMPORT")
        print("=" * 80)
        print()
        print("This will take a while. Photos may become active/visible.")
        print("Please don't quit Photos or Terminal during this process.")
        print()

        # Import to Photos
        imported, failed, failed_files = import_to_photos(image_files, IMPORT_LOG)

        # Move to review folder
        print()
        print("=" * 80)
        print("MOVING TO REVIEW FOLDER")
        print("=" * 80)
        print()

        moved, move_failed, skipped = move_to_review_folder(
            image_files, failed_files, IMPORT_LOG
        )

        # Final summary
        print()
        print("=" * 80)
        print("COMPLETE!")
        print("=" * 80)
        print()
        log_message("=" * 80, IMPORT_LOG)
        log_message("FINAL SUMMARY", IMPORT_LOG)
        log_message("=" * 80, IMPORT_LOG)
        log_message(f"Total images found: {len(image_files):,}", IMPORT_LOG)
        log_message(f"Successfully imported to Photos: {imported:,}", IMPORT_LOG)
        log_message(f"Failed to import: {failed:,}", IMPORT_LOG)
        log_message(f"Moved to review folder: {moved:,}", IMPORT_LOG)
        log_message(f"Failed to move: {move_failed:,}", IMPORT_LOG)
        log_message(f"Skipped (import failed): {skipped:,}", IMPORT_LOG)
        log_message("", IMPORT_LOG)
        log_message(f"Review folder: {REVIEW_DIR}", IMPORT_LOG)
        log_message(f"Detailed log: {IMPORT_LOG}", IMPORT_LOG)
        log_message("", IMPORT_LOG)
        log_message("NEXT STEPS:", IMPORT_LOG)
        log_message("1. Open Photos and verify images are there", IMPORT_LOG)
        log_message("2. Check the review folder to see moved images", IMPORT_LOG)
        log_message("3. When satisfied, manually delete the review folder:", IMPORT_LOG)
        log_message(f"   rm -rf '{REVIEW_DIR}'", IMPORT_LOG)
        log_message("", IMPORT_LOG)

        # Show on console too
        print(f"Total images: {len(image_files):,}")
        print(f"Imported to Photos: {imported:,}")
        print(f"Moved to review folder: {moved:,}")
        print()
        print(f"Review folder: {REVIEW_DIR}")
        print(f"Detailed log: {IMPORT_LOG}")
        print()
        print("NEXT STEPS:")
        print("1. Open Photos and verify images are there")
        print("2. Check the review folder")
        print("3. When satisfied, manually delete:")
        print(f"   rm -rf '{REVIEW_DIR}'")
        print()

        return 0

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        log_message("Operation cancelled by user", IMPORT_LOG)
        return 1
    except Exception as e:
        print(f"\n\nERROR: {e}")
        log_message(f"ERROR: {e}", IMPORT_LOG)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
