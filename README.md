# iMessage Video Cleaner

> **⚠️ WARNING: UNTESTED SOFTWARE**
> This tool has not yet been tested in production. It was created to help manage iMessage video attachments, but **has not been validated** on real systems with real data. If you found this repository randomly, please **do not use this tool** until this notice is removed. Use at your own risk.

A safe tool for removing duplicate videos from iMessage attachments that are already stored in your Photos library.

## What This Does

This script helps free up storage space on your Mac by identifying and safely removing video files from iMessage attachments that are duplicates of videos already in your Photos library. It's designed with multiple safety layers to protect precious family videos.

## Scripts Included

1. **`assess_imessage_videos.py`** - Quick assessment tool (run this first!)
   - Read-only analysis of iMessage video attachments
   - Shows how many videos, sizes, and distribution
   - Helps you decide if the full cleaner is worth running
   - Takes ~30 seconds to run

2. **`imessage_video_cleaner.py`** - Full cleaning tool
   - Interactive GUI for reviewing each video
   - Safely moves duplicates to review folders
   - Human approval required for every file
   - Takes time depending on number of videos

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

## Quick Assessment (Run This First!)

Before running the full cleaner, use the assessment script to understand the scope of the problem:

```bash
cd /Users/matte/MessageClean
python3 assess_imessage_videos.py
```

This will show you:
- How many video files exist in iMessage attachments
- Total storage used
- Size distribution (how many are <10MB, 10-50MB, 50-100MB, etc.)
- Which files would be processed (≥10MB)
- Top 10 largest files
- Estimated time to review
- Potential storage savings

**This script is read-only and completely safe** - it doesn't modify anything.

Example output:
```
SUMMARY
----------------------------------------------------------------------
Total video files found: 147
Total storage used: 3.2 GB
Files >= 10MB (would be processed): 92
Storage in large files: 2.8 GB

SIZE DISTRIBUTION
----------------------------------------------------------------------
< 10 MB      :   55 files (37.4%) - 245.3 MB
10-50 MB     :   68 files (46.3%) - 1.8 GB
50-100 MB    :   18 files (12.2%) - 1.2 GB
100-500 MB   :    6 files ( 4.1%) - 980.5 MB

Estimated time to review: 46-92 minutes
Potential storage savings: 2.8 GB
```

Run this first on your wife's Mac to see if the full cleaner is worth the effort!

## How to Use the Full Cleaner

### Step 1: Run the Script

```bash
cd /Users/matte/MessageClean
python3 imessage_video_cleaner.py
```

### Step 2: Phase 1 - Discovery (Automatic)

The script will:
- Scan `~/Library/Messages/Attachments/` for videos ≥10MB
- Calculate SHA-256 hash for each video (may take a few minutes)
- Save inventory to `~/Desktop/iMessage_Video_Inventory.csv`

You'll see output like:
```
Found 147 videos totaling 3,245 MB
Calculating file hashes...
✓ Phase 1 complete
```

### Step 3: Phase 2 - Photos Check (Automatic)

The script attempts to check if videos are already in Photos. Currently uses a conservative approach that assumes videos are NOT in Photos unless certain.

### Step 4: Phase 3 - Interactive Review (Manual)

A window will open showing one video at a time:

```
┌─────────────────────────────────────┐
│  Video 23 of 147                    │
│  ━━━━━━━━━━░░░░░░░░░░░ 15%         │
│                                     │
│  Filename: IMG_1234.MOV             │
│  Size: 45.3 MB                      │
│  Date: Jan 15, 2023                 │
│  Status: ✗ Not in Photos            │
│                                     │
│  [✓ Mark for Removal]               │
│  [📥 Import to Photos First]        │
│  [⊘ Skip - Keep in iMessage]        │
│                                     │
│  [💾 Save Progress & Quit]          │
└─────────────────────────────────────┘
```

For each video, choose:

- **Mark for Removal** - Video is already in Photos, safe to remove from iMessage
- **Import to Photos First** - Add to Photos, then remove from iMessage
- **Skip** - Keep in iMessage, don't touch it

**Tips:**
- You can click the file path to open in Finder and preview the video
- Click "Save Progress & Quit" at any time to resume later
- Your decisions are saved to `~/Desktop/iMessage_Video_Decisions.json`

### Step 5: Phase 4 - Safe Execution (Semi-Automatic)

After reviewing all videos, the script will show a summary:

```
Ready to process:
  - 55 videos to remove (already in Photos)
  - 23 videos to import then remove
  - 69 videos to keep in iMessage

Proceed with execution? (yes/no):
```

Type `yes` to proceed. The script will:

1. For each video marked for processing (one at a time):
   - If "Import First": Import to Photos, wait 10 seconds, verify success
   - If import fails: Skip that video and continue
   - If successful: Move (not copy!) from iMessage to review folder
2. **Move files to review folders**:
   - `already_in_photos/` - Videos that were already in Photos
   - `newly_imported/` - Videos that were just imported
3. **Save detailed log**: `~/Desktop/iMessage_Cleanup_Log.txt`

**IMPORTANT**: Files are MOVED (not copied) to save disk space. No backup copies are created. The review folders themselves serve as your backup until you manually delete them.

### Step 6: Manual Verification (Critical!)

**Before deleting anything:**

1. Open `~/Desktop/iMessage_Videos_REVIEW/` in Finder
2. Spot-check several videos in each folder
3. Open Photos app and verify the videos are there
4. Open `~/Desktop/iMessage_Cleanup_Log.txt` and review what was done

### Step 7: Final Cleanup (When Ready)

Only after you're completely satisfied everything is safe:

```bash
# Delete the entire review folder
rm -rf ~/Desktop/iMessage_Videos_REVIEW
```

Or delete individual folders:

```bash
# Delete specific folders
rm -rf ~/Desktop/iMessage_Videos_REVIEW/already_in_photos
rm -rf ~/Desktop/iMessage_Videos_REVIEW/newly_imported
```

**IMPORTANT**: There is no separate backup folder. The review folders ARE your backup. Once you delete them, the videos are gone from iMessage (but still in Photos). If you're nervous, wait a few weeks before deleting.

## Files Created

| File | Purpose |
|------|---------|
| `~/Desktop/iMessage_Video_Inventory.csv` | Complete list of all videos found |
| `~/Desktop/iMessage_Video_Decisions.json` | Your decisions for each video |
| `~/Desktop/iMessage_Cleanup_Log.txt` | Detailed log of all actions |
| `~/Desktop/iMessage_Videos_REVIEW/` | Review folders with moved files |

## Resuming After Interruption

If you quit during Phase 3 (review), simply run the script again:

```bash
python3 imessage_video_cleaner.py
```

The script will:
- Load your previous decisions
- Skip videos you already reviewed
- Continue from where you left off

## Troubleshooting

### "Photos database not found"

Make sure your Photos library is at the default location:
```
~/Pictures/Photos Library.photoslibrary
```

If it's elsewhere, you'll need to update the `PHOTOS_LIBRARY` variable in the script.

### "Permission denied" errors

The script needs to access:
- `~/Library/Messages/Attachments/` (iMessage attachments)
- `~/Pictures/Photos Library.photoslibrary/` (Photos library)

You may need to grant Terminal "Full Disk Access" in System Preferences > Security & Privacy > Privacy.

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
