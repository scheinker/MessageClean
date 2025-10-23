#!/usr/bin/env python3
"""
Comprehensive iMessage Attachments Analysis

This script analyzes ALL files in the iMessage attachments folder to help
you understand what's actually taking up storage space.

It shows:
- Total storage used by all files
- Breakdown by file type (videos, images, documents, audio, etc.)
- Top largest files regardless of type
- Storage distribution to help prioritize cleanup efforts

This is read-only and completely safe - it doesn't modify anything.
"""

import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Configuration
ATTACHMENTS_DIR = Path.home() / 'Library' / 'Messages' / 'Attachments'


def format_size(bytes_size):
    """Format bytes to human-readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


def categorize_file(extension):
    """Categorize file by extension into broader categories"""
    ext = extension.lower()

    video_exts = {'.mov', '.mp4', '.m4v', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.mpeg', '.mpg'}
    image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.heic', '.heif', '.bmp', '.tiff', '.webp', '.svg'}
    audio_exts = {'.mp3', '.m4a', '.wav', '.aac', '.flac', '.ogg', '.wma', '.aiff'}
    document_exts = {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.pages', '.odt'}
    archive_exts = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'}

    if ext in video_exts:
        return 'Video'
    elif ext in image_exts:
        return 'Image'
    elif ext in audio_exts:
        return 'Audio'
    elif ext in document_exts:
        return 'Document'
    elif ext in archive_exts:
        return 'Archive'
    elif ext == '.ds_store':
        return 'System'
    elif not ext:
        return 'No Extension'
    else:
        return 'Other'


def analyze_all_files():
    """Analyze all files in iMessage attachments"""

    print("=" * 80)
    print("Comprehensive iMessage Attachments Analysis")
    print("=" * 80)
    print()

    # Check if directory exists
    if not ATTACHMENTS_DIR.exists():
        print(f"ERROR: Attachments directory not found at:")
        print(f"  {ATTACHMENTS_DIR}")
        return

    print(f"Scanning: {ATTACHMENTS_DIR}")
    print("This may take 1-2 minutes for large libraries...")
    print()

    # Check permissions
    try:
        test_list = list(ATTACHMENTS_DIR.iterdir())
    except PermissionError:
        print()
        print("=" * 80)
        print("PERMISSION DENIED")
        print("=" * 80)
        print()
        print("Terminal needs Full Disk Access. See README for instructions.")
        return

    # Scan all files
    print("Scanning all files...")
    all_files = []
    try:
        all_files = [f for f in ATTACHMENTS_DIR.rglob('*') if f.is_file()]
    except Exception as e:
        print(f"Error scanning: {e}")
        return

    if not all_files:
        print("No files found in iMessage attachments.")
        return

    print(f"Found {len(all_files):,} total files")
    print("Analyzing...")
    print()

    # Analyze files
    total_size = 0
    extension_stats = defaultdict(lambda: {'count': 0, 'size': 0, 'files': []})
    category_stats = defaultdict(lambda: {'count': 0, 'size': 0})
    all_files_data = []

    for file_path in all_files:
        try:
            size = file_path.stat().st_size
            ext = file_path.suffix.lower() if file_path.suffix else '(no ext)'
            category = categorize_file(ext)
            modified = datetime.fromtimestamp(file_path.stat().st_mtime)

            total_size += size

            # Track by extension
            extension_stats[ext]['count'] += 1
            extension_stats[ext]['size'] += size
            extension_stats[ext]['files'].append({
                'path': file_path,
                'size': size,
                'modified': modified
            })

            # Track by category
            category_stats[category]['count'] += 1
            category_stats[category]['size'] += size

            # Track all files for top N
            all_files_data.append({
                'path': file_path,
                'name': file_path.name,
                'size': size,
                'ext': ext,
                'category': category,
                'modified': modified
            })

        except Exception as e:
            # Skip files we can't read
            pass

    # Sort files by size
    all_files_data.sort(key=lambda x: x['size'], reverse=True)

    # Print results
    print("=" * 80)
    print("OVERVIEW")
    print("=" * 80)
    print(f"Total files: {len(all_files):,}")
    print(f"Total storage: {format_size(total_size)}")
    print(f"Average file size: {format_size(total_size / len(all_files) if all_files else 0)}")
    print()
    print(f"NOTE: System Settings reports Messages using 126.6 GB")
    print(f"      We found {format_size(total_size)} in attachments")
    if total_size < 126.6 * 1024 * 1024 * 1024:
        diff_gb = (126.6 * 1024 * 1024 * 1024 - total_size) / (1024 * 1024 * 1024)
        print(f"      Difference: ~{diff_gb:.1f} GB (may be in Messages database, backups, or other folders)")
    print()

    # Category breakdown
    print("=" * 80)
    print("STORAGE BY CATEGORY")
    print("=" * 80)
    sorted_categories = sorted(category_stats.items(), key=lambda x: x[1]['size'], reverse=True)
    for category, stats in sorted_categories:
        count = stats['count']
        size = stats['size']
        pct = (size / total_size * 100) if total_size > 0 else 0
        print(f"{category:12} : {count:6,} files | {format_size(size):>10} ({pct:5.1f}%)")
    print()

    # Top extensions by storage
    print("=" * 80)
    print("TOP FILE TYPES BY STORAGE USED")
    print("=" * 80)
    sorted_exts = sorted(extension_stats.items(), key=lambda x: x[1]['size'], reverse=True)
    print(f"{'Extension':<12} {'Files':>8} {'Total Size':>12} {'% of Total':>10} {'Avg Size':>12}")
    print("-" * 80)
    for ext, stats in sorted_exts[:20]:
        count = stats['count']
        size = stats['size']
        pct = (size / total_size * 100) if total_size > 0 else 0
        avg = size / count if count > 0 else 0
        ext_display = ext if ext != '(no ext)' else '<none>'
        print(f"{ext_display:<12} {count:8,} {format_size(size):>12} {pct:9.1f}% {format_size(avg):>12}")
    print()

    # Top 20 largest files
    print("=" * 80)
    print("TOP 30 LARGEST FILES")
    print("=" * 80)
    for i, file_data in enumerate(all_files_data[:30], 1):
        size_mb = file_data['size'] / (1024 * 1024)
        print(f"{i:2}. {format_size(file_data['size']):>10} - {file_data['name']}")
        print(f"    Category: {file_data['category']:<10} | Modified: {file_data['modified'].strftime('%Y-%m-%d')}")
    print()

    # Size distribution
    print("=" * 80)
    print("FILE SIZE DISTRIBUTION")
    print("=" * 80)
    size_buckets = {
        '< 1 MB': (0, 1),
        '1-10 MB': (1, 10),
        '10-50 MB': (10, 50),
        '50-100 MB': (50, 100),
        '100-500 MB': (100, 500),
        '500+ MB': (500, float('inf'))
    }

    bucket_stats = {name: {'count': 0, 'size': 0} for name in size_buckets.keys()}

    for file_data in all_files_data:
        size_mb = file_data['size'] / (1024 * 1024)
        for bucket_name, (min_mb, max_mb) in size_buckets.items():
            if min_mb <= size_mb < max_mb:
                bucket_stats[bucket_name]['count'] += 1
                bucket_stats[bucket_name]['size'] += file_data['size']
                break

    for bucket_name in size_buckets.keys():
        stats = bucket_stats[bucket_name]
        count = stats['count']
        size = stats['size']
        pct = (count / len(all_files_data) * 100) if all_files_data else 0
        size_pct = (size / total_size * 100) if total_size > 0 else 0
        print(f"{bucket_name:12} : {count:6,} files ({pct:5.1f}%) | {format_size(size):>10} ({size_pct:5.1f}%)")
    print()

    # Recommendations
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print()

    # Find the biggest category
    top_category = sorted_categories[0] if sorted_categories else None
    if top_category:
        cat_name, cat_stats = top_category
        cat_pct = (cat_stats['size'] / total_size * 100) if total_size > 0 else 0
        print(f"Largest category: {cat_name} ({format_size(cat_stats['size'])}, {cat_pct:.1f}%)")
        print()

    # Specific recommendations
    video_size = category_stats.get('Video', {}).get('size', 0)
    video_count = category_stats.get('Video', {}).get('count', 0)
    image_size = category_stats.get('Image', {}).get('size', 0)
    image_count = category_stats.get('Image', {}).get('count', 0)

    if video_size > 10 * 1024 * 1024 * 1024:  # > 10 GB
        print(f"📹 VIDEOS: {format_size(video_size)} ({video_count:,} files)")
        video_10mb_plus = sum(1 for f in all_files_data if f['category'] == 'Video' and f['size'] >= 10*1024*1024)
        print(f"   - {video_10mb_plus:,} videos are >= 10 MB")
        print(f"   - Reviewing all would take {video_10mb_plus * 0.5:.0f}-{video_10mb_plus:.0f} minutes")
        print(f"   - SUGGESTION: Focus on videos >= 50 MB or 100 MB instead")
        video_50mb_plus = sum(1 for f in all_files_data if f['category'] == 'Video' and f['size'] >= 50*1024*1024)
        video_100mb_plus = sum(1 for f in all_files_data if f['category'] == 'Video' and f['size'] >= 100*1024*1024)
        print(f"     - Videos >= 50 MB: {video_50mb_plus:,} files")
        print(f"     - Videos >= 100 MB: {video_100mb_plus:,} files")
        print()

    if image_size > 5 * 1024 * 1024 * 1024:  # > 5 GB
        print(f"🖼️  IMAGES: {format_size(image_size)} ({image_count:,} files)")
        print(f"   - Most images are likely duplicates if they're also in Photos")
        print(f"   - Consider bulk moving images to Photos (Photos handles duplicates)")
        print()

    # Strategy suggestion
    print("CLEANUP STRATEGY:")
    print("-" * 80)

    if video_count > 1000 and video_size > 20 * 1024 * 1024 * 1024:
        print("1. You have too many videos to review individually")
        print("   - Consider filtering by size (>= 50 MB or >= 100 MB)")
        print("   - Or use Photos' import feature to bulk import all videos")
        print("   - Photos will detect duplicates automatically")
        print()

    print("2. Based on this analysis, consider:")
    if video_size > image_size:
        print("   - Focus on largest videos first (see 'Top 30 Largest Files' above)")
        print("   - Manually review and delete/move the top 50-100 largest files")
    else:
        print("   - Focus on images - bulk import to Photos, then clear from Messages")

    print()
    print(f"3. Quick wins - manually review top 30 largest files shown above")
    if all_files_data:
        top_30_size = sum(f['size'] for f in all_files_data[:30])
        print(f"   - Top 30 files = {format_size(top_30_size)}")
        print(f"   - Reviewing just 30 files could free up significant space")

    print()
    print("=" * 80)
    print()


def main():
    try:
        analyze_all_files()
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
