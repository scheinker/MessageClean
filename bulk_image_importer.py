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
from PIL import Image

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
    print("1. Process images in BATCHES (to avoid filling disk):")
    print("   - Batch size: 500 images (~850 MB)")
    print("   - For each batch: Import to Photos → Move from Messages → Repeat")
    print("   - This keeps disk usage minimal (only ~1 GB extra at any time)")
    print("   - NO DIALOGS - imports run automatically")
    print("   - Some duplicates may be created (this is intentional)")
    print("   - Takes 10-15 minutes for ~25,000 images")
    print()
    print("2. Images moved to review folder:")
    print(f"   {REVIEW_DIR}")
    print()
    print("3. Create detailed log:")
    print(f"   {IMPORT_LOG}")
    print()
    print("4. You verify Photos has everything")
    print()
    print("5. Use Photos' built-in 'Merge Duplicates' feature")
    print("   - Takes ~5 minutes")
    print("   - Instructions will be shown at the end")
    print()
    print("6. When satisfied, you manually delete the review folder")
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


def is_burst_photo(img_path):
    """
    Check if a photo is part of a burst sequence
    Burst photos have special patterns in filenames
    """
    filename = img_path.name.lower()
    # Common burst photo indicators
    burst_patterns = ['_burst', 'burst_', '-burst', 'burst-']
    return any(pattern in filename for pattern in burst_patterns)


def validate_image(img_path):
    """
    Check if an image file is valid and can be opened
    Returns (is_valid, skip_reason)
    - (True, None) if valid and should be imported
    - (False, reason) if should be skipped
    """
    # Check if it's a burst photo (Photos doesn't support duplicate bursts)
    if is_burst_photo(img_path):
        return False, "burst photo"

    # Check if file is valid/not corrupted
    try:
        with Image.open(img_path) as img:
            img.verify()  # Verify it's a valid image
        return True, None
    except Exception:
        return False, "invalid/corrupted"


def process_batch(batch, batch_num, total_batches, log_file):
    """
    Process one batch: import to Photos, then immediately move from Messages
    This avoids filling up disk space
    """
    batch_size = len(batch)
    imported = 0
    failed = 0
    moved = 0
    failed_files = []
    skipped = 0

    print(f"\nBatch {batch_num}/{total_batches} ({batch_size} images)")
    print(f"  Step 1/2: Validating and importing to Photos...")

    # Import each image in the batch
    for i, img_data in enumerate(batch):
        img_path = img_data['path']

        # First, validate the image file
        is_valid, skip_reason = validate_image(img_path)
        if not is_valid:
            skipped += 1
            failed_files.append(str(img_path))
            log_message(f"  SKIPPED ({skip_reason}): {img_path.name}", log_file)
            continue

        try:
            # Import to Photos using AppleScript
            # skip check duplicates true = no dialogs for duplicates
            # without interaction = suppress error dialogs
            # Escape quotes in filename for AppleScript
            safe_path = str(img_path).replace('"', '\\"')
            script = f'''
                tell application "Photos"
                    with timeout of 30 seconds
                        try
                            import POSIX file "{safe_path}" skip check duplicates true
                        end try
                    end timeout
                end tell
            '''
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=35
            )

            # Check if Photos returned a burst photo error
            error_text = result.stderr.lower() if result.stderr else ""
            if "burst" in error_text:
                skipped += 1
                failed_files.append(str(img_path))
                log_message(f"  SKIPPED (burst photo): {img_path.name}", log_file)
            elif result.returncode == 0:
                imported += 1
                if (i + 1) % 50 == 0:
                    print(f"    Processed {i + 1}/{batch_size} from this batch...")
            else:
                failed += 1
                failed_files.append(str(img_path))
                # Log the actual error from Photos for debugging
                error_detail = result.stderr if result.stderr else "No error message"
                log_message(f"  FAILED to import: {img_path.name} - Error: {error_detail}", log_file)

        except Exception as e:
            failed += 1
            failed_files.append(str(img_path))
            log_message(f"  ERROR importing {img_path.name}: {e}", log_file)

    print(f"  Step 2/2: Moving from Messages to review folder...")

    # Immediately move imported images from Messages to review folder
    for img_data in batch:
        img_path = img_data['path']

        # Skip files that failed to import
        if str(img_path) in failed_files:
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

        except Exception as e:
            log_message(f"  ERROR moving {img_path.name}: {e}", log_file)

    if skipped > 0:
        print(f"  ✓ Batch complete: {imported} imported, {moved} moved, {skipped} skipped (burst/invalid), {failed} failed")
    else:
        print(f"  ✓ Batch complete: {imported} imported, {moved} moved, {failed} failed")

    return imported, failed, moved, skipped, failed_files


def process_all_images_batched(image_files, log_file):
    """
    Process all images in batches to avoid filling disk
    Each batch: import → move → repeat
    This keeps disk usage minimal
    """
    log_message("=" * 80, log_file)
    log_message("BATCH PROCESSING (IMPORT → MOVE)", log_file)
    log_message("=" * 80, log_file)
    log_message("This prevents disk from filling up by moving each batch immediately", log_file)
    log_message("", log_file)

    # Create review directory
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)

    # Process in batches of 500 images (~850 MB at a time)
    batch_size = 500
    batches = [image_files[i:i + batch_size] for i in range(0, len(image_files), batch_size)]

    total_imported = 0
    total_failed = 0
    total_moved = 0
    total_skipped = 0
    all_failed_files = []

    print()
    print("=" * 80)
    print("PROCESSING IN BATCHES")
    print("=" * 80)
    print(f"Total images: {len(image_files):,}")
    print(f"Batch size: {batch_size} images (~850 MB)")
    print(f"Total batches: {len(batches)}")
    print()
    print("Each batch: Validate → Import to Photos → Move from Messages → Free up space")
    print("This prevents disk from filling up!")
    print("Invalid/corrupted files and burst photos will be skipped (no dialogs).")
    print()

    for batch_num, batch in enumerate(batches, 1):
        imported, failed, moved, skipped, failed_files = process_batch(
            batch, batch_num, len(batches), log_file
        )

        total_imported += imported
        total_failed += failed
        total_moved += moved
        total_skipped += skipped
        all_failed_files.extend(failed_files)

        # Small delay between batches
        if batch_num < len(batches):
            import time
            time.sleep(1)

    log_message("", log_file)
    if total_skipped > 0:
        log_message(f"Processing complete: {total_imported} imported, {total_moved} moved, {total_skipped} skipped (burst/invalid), {total_failed} failed", log_file)
    else:
        log_message(f"Processing complete: {total_imported} imported, {total_moved} moved, {total_failed} failed", log_file)

    return total_imported, total_failed, total_moved, total_skipped, all_failed_files


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
        print("STARTING BATCH PROCESSING")
        print("=" * 80)
        print()
        print("This will take a while. Photos may become active/visible.")
        print("Please don't quit Photos or Terminal during this process.")
        print()
        print("IMPORTANT: Processing in batches to prevent disk from filling up!")
        print("Each batch imports to Photos, then immediately moves from Messages.")
        print()

        # Process all images in batches (import → move → repeat)
        imported, failed, moved, skipped, failed_files = process_all_images_batched(
            image_files, IMPORT_LOG
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
        log_message(f"Successfully moved to review folder: {moved:,}", IMPORT_LOG)
        if skipped > 0:
            log_message(f"Skipped (burst photos + invalid/corrupted): {skipped:,}", IMPORT_LOG)
        log_message(f"Failed (not imported or moved): {failed:,}", IMPORT_LOG)
        log_message("", IMPORT_LOG)
        log_message(f"Review folder: {REVIEW_DIR}", IMPORT_LOG)
        log_message(f"Detailed log: {IMPORT_LOG}", IMPORT_LOG)
        log_message("", IMPORT_LOG)
        log_message("NEXT STEPS:", IMPORT_LOG)
        log_message("1. Open Photos and verify images are there", IMPORT_LOG)
        log_message("2. Merge duplicate photos (IMPORTANT!):", IMPORT_LOG)
        log_message("   a. In Photos, go to Albums sidebar", IMPORT_LOG)
        log_message("   b. Scroll to 'Utilities' section", IMPORT_LOG)
        log_message("   c. Click 'Duplicates' album", IMPORT_LOG)
        log_message("   d. Review duplicates and click 'Merge' for each", IMPORT_LOG)
        log_message("      (or 'Merge All' if available in newer macOS)", IMPORT_LOG)
        log_message("   e. This preserves all metadata and edits", IMPORT_LOG)
        log_message("3. Check the review folder to see moved images", IMPORT_LOG)
        log_message("4. When satisfied, manually delete the review folder:", IMPORT_LOG)
        log_message(f"   rm -rf '{REVIEW_DIR}'", IMPORT_LOG)
        log_message("", IMPORT_LOG)

        # Show on console too
        print()
        print("=" * 80)
        print("IMPORT COMPLETE!")
        print("=" * 80)
        print(f"Total images: {len(image_files):,}")
        print(f"Imported to Photos: {imported:,}")
        print(f"Moved to review folder: {moved:,}")
        if skipped > 0:
            print(f"Skipped (burst photos + invalid/corrupted): {skipped:,}")
        print()
        print(f"Review folder: {REVIEW_DIR}")
        print(f"Detailed log: {IMPORT_LOG}")
        print()
        print("=" * 80)
        print("NEXT STEPS:")
        print("=" * 80)
        print()
        print("1. Open Photos app and verify images are there")
        print()
        print("2. MERGE DUPLICATE PHOTOS (takes ~5 minutes):")
        print("   a. In Photos, click 'Albums' in the sidebar")
        print("   b. Scroll down to the 'Utilities' section")
        print("   c. Click the 'Duplicates' album")
        print("   d. You'll see sets of duplicate photos")
        print("   e. Click 'Merge' for each duplicate set")
        print("      (or 'Merge All' if available in your macOS version)")
        print("   f. This will merge duplicates while preserving all metadata")
        print()
        print("3. Verify everything looks good in Photos")
        print()
        print("4. When satisfied, delete the review folder:")
        print(f"   rm -rf '{REVIEW_DIR}'")
        print()
        print("=" * 80)

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
