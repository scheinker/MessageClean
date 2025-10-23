# MessageClean - iMessage Storage Cleanup Tools

> **⚠️ WARNING: UNTESTED SOFTWARE**
> These tools have not yet been fully tested in production. Created to help manage iMessage storage, but **not validated** on all systems. If you found this repository randomly, please **do not use** until this notice is removed. Use at your own risk.

A suite of safe tools for cleaning up iMessage storage on macOS by handling duplicate images and videos that are already stored in your Photos library.

## What This Does

These tools help free up storage space (potentially 40-60 GB!) on your Mac by:
1. **Bulk importing images to Photos** (handles duplicates automatically)
2. **Smart video cleanup** with hash-based verification to prove videos are already in Photos
3. **Nothing is permanently deleted** - everything moved to review folders first

Designed with multiple safety layers to protect precious family photos and videos.

## The Problem

iMessage stores ALL attachments locally forever. Over time, this can use 100+ GB of storage, even though most of these images/videos are also in your Photos library. You're paying twice - once in Messages, once in Photos.

## The Solution: Two-Phase Cleanup

### Assessment Tool (Run First!)
**`assess_all_imessage_files.py`** - Understand what's taking up space
- Analyzes ALL file types (videos, images, documents, audio)
- Shows storage breakdown by category
- Identifies top 30 largest files
- Recommends cleanup strategy
- **Run this first to understand your situation!**

### Phase 1: Bulk Image Importer
**`bulk_image_importer.py`** - Handle thousands of images quickly (30-40 GB potential savings)
- Scans all images in iMessage attachments
- Bulk imports to Photos (Photos detects duplicates automatically)
- Moves images to review folder
- You verify, then manually delete review folder
- **Time**: 30-60 minutes total

### Phase 2: Smart Video Cleaner
**`smart_video_cleaner.py`** - Handle videos with verification (10-30 GB potential savings)
- Hash-based verification - proves video exists in Photos
- Interactive GUI to review each video
- Start with large videos (≥100MB) for quick wins
- Shows Photos match status for each video
- You approve each decision
- **Time**: 20-40 minutes for 40 largest videos

### Legacy Tools (For Reference)
- **`assess_imessage_videos.py`** - Video-only assessment
- **`imessage_video_cleaner.py`** - Original video cleaner (impractical for 1000+ videos)

## Safety Features

- **No immediate deletion** - Files are moved to review folders, never permanently deleted by the script
- **No disk space duplication** - Files are moved (not copied), requiring zero additional disk space
- **Review folders are your backup** - Files remain in review folders until you manually delete them
- **Human review** - You manually approve every single video
- **Import verification** - Checks that Photos import succeeded before moving files
- **Detailed logging** - Complete audit trail of all actions
- **Resume capability** - Can pause and continue later
- **Conservative matching** - Only processes videos you explicitly approve
- **Easy undo** - Just move files back from review folders if needed

## Requirements

- macOS (tested on macOS 10.15+)
- Python 3 (built into macOS)
- iMessage attachments stored locally
- Photos app with local library

## Installation

No installation needed! The script uses only standard Python libraries included with macOS.

### Verify Python 3 is Available

```bash
python3 --version
```

You should see something like `Python 3.9.6` or higher.

## Important: Grant Full Disk Access

**Before running either script**, you need to grant Terminal (or your terminal app) "Full Disk Access" permission. macOS blocks access to the Messages folder for security.

### How to Grant Full Disk Access:

1. Open **System Settings** (or **System Preferences** on older macOS)
2. Go to **Privacy & Security** → **Full Disk Access**
3. Click the **lock icon** 🔒 at the bottom and authenticate
4. Click the **+** button
5. Navigate to `/Applications/Utilities/`
6. Select **Terminal** and click **Open**
7. **Restart Terminal completely** (Cmd+Q then reopen)
8. Run the script again

### Notes:
- If using iTerm2, VS Code terminal, or another terminal app, add that app instead
- The scripts will detect permission errors and show these instructions if needed
- This is safe - it only allows Terminal to read protected folders

## Comprehensive Assessment (RUN THIS FIRST!)

**Before doing anything else**, run the comprehensive assessment to understand what's ACTUALLY taking up space:

```bash
cd /Users/matte/MessageClean
python3 assess_all_imessage_files.py
```

This will show you:
- **All file types** (videos, images, documents, audio, etc.)
- **Storage by category** - which type uses the most space?
- **Top 30 largest files** - quick wins for manual cleanup
- **Recommended strategy** based on what it finds
- **Size distribution** across all files

**This script is read-only and completely safe** - it doesn't modify anything.

### Why This Matters

System Settings might report "126 GB for Messages", but you need to know:
- Is it videos? Images? PDFs? Audio files?
- Are there a few huge files or thousands of small ones?
- What cleanup strategy makes sense?

### Example: What You Might Discover

```
STORAGE BY CATEGORY
----------------------------------------------------------------------
Video        :  7,054 files | 47.8 GB (38%)
Image        : 15,230 files | 52.1 GB (41%)
Document     :    145 files |  8.2 GB (7%)
Audio        :    892 files |  3.1 GB (2%)

TOP 30 LARGEST FILES
----------------------------------------------------------------------
 1.   146.2 MB - MOV_4445.MOV (Video)
 2.    98.5 MB - vacation_video.mp4 (Video)
 3.    45.2 MB - presentation.pdf (Document)
...

RECOMMENDATIONS
----------------------------------------------------------------------
Quick wins - manually review top 30 largest files
- Top 30 files = 3.2 GB
- Reviewing just 30 files could free up significant space
```

**Run this first** to understand your situation before deciding on a cleanup strategy!

## Complete Workflow - Step by Step

### Step 0: Assessment (REQUIRED FIRST STEP)

```bash
cd MessageClean
python3 assess_all_imessage_files.py
```

This shows you:
- What's taking up space (images? videos?)
- How much you could potentially save
- Which cleanup approach makes sense

### Step 1: Phase 1 - Bulk Image Import

**Purpose**: Handle 25,000+ images (30-40 GB potential savings)

```bash
python3 bulk_image_importer.py
```

**What happens**:
1. Shows summary of images found
2. Asks for confirmation
3. Bulk imports all images to Photos
   - Photos automatically detects duplicates
   - Takes 30-60 minutes depending on volume
4. Moves images from Messages to `~/Desktop/iMessage_Images_REVIEW/`
5. Creates log: `~/Desktop/iMessage_Image_Import_Log.txt`

**After it completes**:
1. Open Photos - verify images are there
2. Check review folder - spot check a few images
3. When satisfied, manually delete review folder:
   ```bash
   rm -rf ~/Desktop/iMessage_Images_REVIEW
   ```

### Step 2: Phase 2 - Smart Video Cleanup

**Purpose**: Handle videos with verification (start with largest for quick wins)

**Start with videos ≥100MB (recommended)**:
```bash
python3 smart_video_cleaner.py --min-size=100
```

**What happens**:
1. Scans for videos ≥100MB (typically 30-40 videos)
2. Calculates file hashes
3. Checks if each video exists in Photos (by size + filename)
4. Opens interactive GUI showing each video:
   - Video info (name, size, date)
   - Photos match status: "✓ FOUND IN PHOTOS" or "✗ NOT FOUND"
   - Three buttons:
     - "Already in Photos - Safe to Remove" (if matched)
     - "Import to Photos First, Then Remove" (if not matched)
     - "Keep in Messages" (skip)
5. You review and decide for each video
6. Moves videos to `~/Desktop/iMessage_Videos_REVIEW/`
7. Creates log: `~/Desktop/iMessage_Video_Cleanup_Log.txt`

**After reviewing all videos**:
1. Open Photos - verify videos are there
2. Check review folders:
   - `already_in_photos/` - Videos that were matched
   - `newly_imported/` - Videos that were just imported
3. When satisfied, manually delete review folder:
   ```bash
   rm -rf ~/Desktop/iMessage_Videos_REVIEW
   ```

**Optional: Process more videos**:
```bash
# Videos ≥50MB (typically 130-170 videos, more time investment)
python3 smart_video_cleaner.py --min-size=50

# Videos ≥10MB (1000+ videos, only if you need maximum cleanup)
python3 smart_video_cleaner.py --min-size=10
```

### Step 3: Reassess Progress

After Phase 1 and Phase 2, run the assessment again to see your progress:

```bash
python3 assess_all_imessage_files.py
```

This will show you:
- How much space you've freed up
- Whether you've hit your storage goal
- If you need to process more videos (e.g., run Phase 2 with `--min-size=50`)

## Expected Results

Based on real-world data:

**Phase 1 (Images)**: 30-42 GB freed
- Depends on how many images are duplicates vs. unique to Messages

**Phase 2 (Videos ≥100MB)**: 3-5 GB freed
- 30-40 largest videos

**Phase 2 (Videos ≥50MB)**: 10-13 GB freed
- 130-170 videos

**Total**: 40-60 GB potential savings

## Files Created During Cleanup

| File/Folder | Purpose |
|------------|---------|
| `~/Desktop/iMessage_Images_REVIEW/` | Images moved from Messages (delete when satisfied) |
| `~/Desktop/iMessage_Videos_REVIEW/` | Videos moved from Messages (delete when satisfied) |
| `~/Desktop/iMessage_Image_Import_Log.txt` | Detailed log of image import |
| `~/Desktop/iMessage_Video_Cleanup_Log.txt` | Detailed log of video cleanup |
| `~/Desktop/iMessage_Video_Decisions.json` | Your decisions (can resume if interrupted) |
| `~/Desktop/iMessage_Video_Inventory.csv` | Assessment data |

## Resuming After Interruption

Both tools support resuming:

**Image Importer**: Just run it again - it will skip already-imported images

**Video Cleaner**: Run the same command - it loads your previous decisions from the JSON file and continues where you left off

## Manual Verification (Critical!)

**Before permanently deleting review folders:**

1. Open Photos app
   - Browse recent imports
   - Spot-check videos are actually there
   - Check a few images are present

2. Check review folders on Desktop
   - `iMessage_Images_REVIEW/` - Spot-check a few images
   - `iMessage_Videos_REVIEW/` - Spot-check a few videos

3. Review the logs
   - `iMessage_Image_Import_Log.txt` - See what was imported
   - `iMessage_Video_Cleanup_Log.txt` - See what was processed

4. When satisfied everything is safe in Photos:
   ```bash
   # Delete image review folder
   rm -rf ~/Desktop/iMessage_Images_REVIEW

   # Delete video review folder
   rm -rf ~/Desktop/iMessage_Videos_REVIEW
   ```

**Don't rush this step!** These are precious memories. Take your time verifying.

## Troubleshooting

### "Photos database not found"

Make sure your Photos library is at the default location:
```
~/Pictures/Photos Library.photoslibrary
```

If it's elsewhere, you'll need to update the `PHOTOS_LIBRARY` variable in the script.

### "Permission denied" errors

If you see `PermissionError: [Errno 1] Operation not permitted`, this means Terminal doesn't have access to the Messages folder.

**Solution**: Grant Terminal "Full Disk Access" - see the detailed instructions in the "Important: Grant Full Disk Access" section above.

The script needs to access:
- `~/Library/Messages/Attachments/` (iMessage attachments)
- `~/Pictures/Photos Library.photoslibrary/` (Photos library)

### Import to Photos fails

If Photos import fails for a video:
- The script will skip that video and leave it in iMessage (not moved)
- Check the log file for details
- The video remains in its original location for safety
- You can manually import it later

### Videos are duplicated in Photos after import

Photos should automatically detect duplicates. If it doesn't:
- Check that "skip check duplicates false" is working
- You can manually delete duplicates in Photos
- All moved files are safe in the review folders

## Configuration

You can modify these settings at the top of the script:

```python
MIN_SIZE_MB = 10          # Minimum video size to process
VIDEO_EXTENSIONS = ['.mov', '.mp4', '.m4v', '.avi']  # File types to process
```

## Safety Notes

- **This script never permanently deletes files** - It only moves them to review folders
- **No disk space duplication** - Files are moved (not copied) to save space
- **Review folders are your backup** - Nothing is deleted until you manually delete the folders
- **You control everything** - Human approval for every single video
- **Logging** - Complete record of what was done
- **Undo-friendly** - Just move files back from review folders to restore

## What Gets Freed Up

The script only processes videos ≥10MB. After completion:
- Videos are removed from `~/Library/Messages/Attachments/`
- iMessage app will show less storage usage
- Videos remain safely in Photos and review folders
- No disk space is saved until you manually delete the review folders
- You can verify everything before permanently deleting the review folders

## Technical Details

- **Hash algorithm**: SHA-256 (cryptographically secure)
- **Duplicate detection**: Conservative approach, relies on Photos' built-in detection
- **GUI framework**: Tkinter (included with Python)
- **Photos integration**: AppleScript for safe import
- **Database access**: Read-only SQLite queries to Photos library

## Support

If you encounter issues:

1. Check the log file: `~/Desktop/iMessage_Cleanup_Log.txt`
2. Review the inventory CSV for details about what was found
3. The review folders contain all moved files if you need to restore them

## Important Reminders

- **These are precious family videos** - Take your time reviewing
- **Don't delete review folders immediately** - Wait a few weeks to be safe
- **Spot-check Photos** - Verify videos are actually there before final deletion
- **Review folders are your only backup** - Once deleted, videos are only in Photos
- **When in doubt, choose "Skip"** - Better safe than sorry

## License

This script is provided as-is for personal use. No warranty expressed or implied.
