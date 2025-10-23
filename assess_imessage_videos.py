#!/usr/bin/env python3
"""
Quick Assessment Script for iMessage Video Attachments

This script analyzes the iMessage attachments folder to determine:
- How many video files exist
- Size distribution of videos
- Total storage used
- Which files would be processed by the main cleaner script

This is read-only and completely safe - it doesn't modify anything.
Run this first to understand the scope of the problem.
"""

import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Configuration
ATTACHMENTS_DIR = Path.home() / 'Library' / 'Messages' / 'Attachments'
VIDEO_EXTENSIONS = ['.mov', '.mp4', '.m4v', '.avi']
MIN_SIZE_MB = 10  # Same threshold as main script


def format_size(bytes_size):
    """Format bytes to human-readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


def get_size_bucket(size_mb):
    """Categorize file size into buckets"""
    if size_mb < 10:
        return "< 10 MB"
    elif size_mb < 50:
        return "10-50 MB"
    elif size_mb < 100:
        return "50-100 MB"
    elif size_mb < 500:
        return "100-500 MB"
    else:
        return "500+ MB"


def analyze_videos():
    """Analyze all video files in iMessage attachments"""

    print("=" * 70)
    print("iMessage Video Attachment Assessment")
    print("=" * 70)
    print()

    # Check if directory exists
    if not ATTACHMENTS_DIR.exists():
        print(f"ERROR: Attachments directory not found at:")
        print(f"  {ATTACHMENTS_DIR}")
        print()
        print("This might mean:")
        print("  - iMessage attachments are stored elsewhere")
        print("  - iMessage hasn't saved any attachments yet")
        print("  - The path has changed in a newer macOS version")
        return

    print(f"Scanning: {ATTACHMENTS_DIR}")
    print("This may take a minute...")
    print()

    # Find all video files
    video_files = []
    for ext in VIDEO_EXTENSIONS:
        video_files.extend(ATTACHMENTS_DIR.rglob(f'*{ext}'))
        video_files.extend(ATTACHMENTS_DIR.rglob(f'*{ext.upper()}'))

    if not video_files:
        print("No video files found in iMessage attachments.")
        print()
        print("This might mean:")
        print("  - No videos have been received via iMessage")
        print("  - Videos are stored elsewhere")
        print("  - All videos have already been deleted")
        return

    # Analyze files
    total_count = 0
    total_size_bytes = 0
    size_buckets = defaultdict(int)
    size_bucket_bytes = defaultdict(int)
    extension_counts = defaultdict(int)
    extension_bytes = defaultdict(int)

    large_files = []  # Files >= 10MB
    all_files_data = []

    for video_path in video_files:
        try:
            size_bytes = video_path.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            modified = datetime.fromtimestamp(video_path.stat().st_mtime)
            ext = video_path.suffix.lower()

            total_count += 1
            total_size_bytes += size_bytes

            bucket = get_size_bucket(size_mb)
            size_buckets[bucket] += 1
            size_bucket_bytes[bucket] += size_bytes

            extension_counts[ext] += 1
            extension_bytes[ext] += size_bytes

            all_files_data.append({
                'path': video_path,
                'size_bytes': size_bytes,
                'size_mb': size_mb,
                'modified': modified
            })

            if size_mb >= MIN_SIZE_MB:
                large_files.append({
                    'name': video_path.name,
                    'size_mb': size_mb,
                    'modified': modified
                })

        except Exception as e:
            print(f"Warning: Could not process {video_path.name}: {e}")

    # Sort large files by size
    large_files.sort(key=lambda x: x['size_mb'], reverse=True)

    # Print results
    print("-" * 70)
    print("SUMMARY")
    print("-" * 70)
    print(f"Total video files found: {total_count:,}")
    print(f"Total storage used: {format_size(total_size_bytes)}")
    print(f"Average file size: {format_size(total_size_bytes / total_count if total_count > 0 else 0)}")
    print()

    # Files that would be processed
    large_count = len(large_files)
    large_size = sum(f['size_mb'] for f in large_files) * 1024 * 1024
    print(f"Files >= {MIN_SIZE_MB}MB (would be processed): {large_count:,}")
    print(f"Storage in large files: {format_size(large_size)}")
    print(f"Files < {MIN_SIZE_MB}MB (would be skipped): {total_count - large_count:,}")
    print()

    # Size distribution
    print("-" * 70)
    print("SIZE DISTRIBUTION")
    print("-" * 70)
    bucket_order = ["< 10 MB", "10-50 MB", "50-100 MB", "100-500 MB", "500+ MB"]
    for bucket in bucket_order:
        if bucket in size_buckets:
            count = size_buckets[bucket]
            size = size_bucket_bytes[bucket]
            pct = (count / total_count * 100) if total_count > 0 else 0
            print(f"{bucket:12} : {count:4} files ({pct:5.1f}%) - {format_size(size)}")
    print()

    # File types
    print("-" * 70)
    print("FILE TYPES")
    print("-" * 70)
    for ext in sorted(extension_counts.keys()):
        count = extension_counts[ext]
        size = extension_bytes[ext]
        pct = (count / total_count * 100) if total_count > 0 else 0
        print(f"{ext:6} : {count:4} files ({pct:5.1f}%) - {format_size(size)}")
    print()

    # Largest files
    print("-" * 70)
    print(f"TOP 10 LARGEST FILES (>= {MIN_SIZE_MB}MB)")
    print("-" * 70)
    if large_files:
        for i, file_info in enumerate(large_files[:10], 1):
            print(f"{i:2}. {file_info['size_mb']:7.1f} MB - {file_info['name']}")
            print(f"    Modified: {file_info['modified'].strftime('%Y-%m-%d %I:%M %p')}")
    else:
        print(f"No files >= {MIN_SIZE_MB}MB found.")
    print()

    # Recommendations
    print("=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    if large_count == 0:
        print("No large video files found. The main cleaner script may not be needed.")
    elif large_count < 20:
        print(f"You have {large_count} large videos totaling {format_size(large_size)}.")
        print("This is a small number - manual cleanup might be easier than running the script.")
    elif large_count < 100:
        print(f"You have {large_count} large videos totaling {format_size(large_size)}.")
        print("The main cleaner script would be helpful for this volume.")
        print(f"Estimated time to review: {large_count * 0.5:.0f}-{large_count:.0f} minutes")
    else:
        print(f"You have {large_count} large videos totaling {format_size(large_size)}!")
        print("The main cleaner script is definitely recommended.")
        print(f"Estimated time to review: {large_count * 0.5:.0f}-{large_count:.0f} minutes")

    print()
    print(f"Potential storage savings: {format_size(large_size)}")
    print("(After moving files to Photos and deleting review folders)")
    print()


def main():
    try:
        analyze_videos()
    except KeyboardInterrupt:
        print("\n\nAnalysis cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
