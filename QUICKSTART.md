# MessageClean - Quick Start Guide

**Goal**: Free up 40-60 GB of storage from iMessage attachments safely

**Time Required**: ~90 minutes total

**What You'll Do**: Import images/videos to Photos, then remove from Messages

---

## Prerequisites (5 minutes)

### 1. Grant Terminal Full Disk Access

**macOS Ventura/Sonoma:**
1. Open **System Settings**
2. Click **Privacy & Security** (in sidebar)
3. Click **Full Disk Access**
4. Click the 🔒 lock icon, enter password
5. Click **+** button
6. Navigate to `/Applications/Utilities/`
7. Select **Terminal**, click **Open**
8. **Quit Terminal completely** (Cmd+Q)
9. Reopen Terminal

**macOS Big Sur/Monterey:**
1. Open **System Preferences**
2. Click **Security & Privacy**
3. Click **Privacy** tab
4. Select **Full Disk Access** from list
5. Follow steps 4-9 above

### 2. Download the Tools

```bash
cd ~/Desktop
git clone https://github.com/scheinker/MessageClean.git
cd MessageClean
```

**If you already downloaded it**:
```bash
cd ~/Desktop/MessageClean
git pull
```

---

## Step 1: Understand What You Have (2 minutes)

```bash
python3 assess_all_imessage_files.py
```

**What to look for**:
- How many images? (probably 20,000+)
- How many videos? (probably 7,000+)
- Total storage used
- Recommendations

**Write down the total storage** for comparison later.

---

## Step 2: Import Images to Photos (30-60 minutes)

```bash
python3 bulk_image_importer.py
```

**What happens**:
1. Shows summary of images found
2. Asks: "Do you want to proceed? (yes/no):"
3. Type `yes` and press Enter
4. Photos app will open and start importing
5. **Don't quit Photos or Terminal!**
6. Wait for it to finish (30-60 minutes)

**When complete**:
- You'll see: "COMPLETE!"
- A review folder will be on your Desktop

**Verify** (don't skip this!):
1. Open **Photos** app
2. Look for recently imported images
3. Spot-check a few images are there

**If everything looks good**:
```bash
rm -rf ~/Desktop/iMessage_Images_REVIEW
```

**Expected savings**: 30-42 GB

---

## Step 3: Clean Up Largest Videos (20-40 minutes)

```bash
python3 smart_video_cleaner.py --min-size=100
```

**What happens**:
1. Scans for videos >= 100MB (typically 30-40 videos)
2. Calculates hashes (2-3 minutes)
3. Checks Photos library
4. Opens a window showing each video one at a time

**For each video, you'll see**:
- Video name, size, date
- Whether it's already in Photos: "✓ FOUND IN PHOTOS" or "✗ NOT FOUND"
- Three buttons:
  - **"Already in Photos - Safe to Remove"** - Green (if found in Photos)
  - **"Import to Photos First, Then Remove"** - Blue (if not found)
  - **"Keep in Messages"** - Yellow (skip it)

**What to click**:
- If green button is enabled → click it (safe to remove)
- If blue button is enabled → click it (will import first)
- If unsure → click yellow "Keep" button

**Progress**: Shows "Space to be freed so far: X GB" at top

**When done reviewing all videos**:
- Click "✓ Finish Review & Continue"
- Files will be moved to review folder
- Check the log on your Desktop

**Verify**:
1. Open **Photos** app
2. Look for the videos you reviewed
3. Spot-check a few are there

**If everything looks good**:
```bash
rm -rf ~/Desktop/iMessage_Videos_REVIEW
```

**Expected savings**: 4-5 GB

---

## Step 4: Check Your Progress (2 minutes)

```bash
python3 assess_all_imessage_files.py
```

**Compare to Step 1**:
- How much storage freed up?
- Did you hit your goal?

**If you need more space**, process more videos:

```bash
# Medium videos (50-100MB) - about 130 more videos, 1-2 hours
python3 smart_video_cleaner.py --min-size=50

# All videos (10MB+) - about 1000 videos, 8-10 hours (not recommended)
python3 smart_video_cleaner.py --min-size=10
```

---

## Step 5: Final Cleanup

After everything is verified and you're satisfied:

```bash
# Delete any remaining review folders
rm -rf ~/Desktop/iMessage_Images_REVIEW
rm -rf ~/Desktop/iMessage_Videos_REVIEW

# Optional: Clean up log files
rm ~/Desktop/iMessage_*.txt
rm ~/Desktop/iMessage_*.csv
rm ~/Desktop/iMessage_*.json
```

---

## Expected Results

| Phase | Files Processed | Time | Space Freed |
|-------|----------------|------|-------------|
| Images | ~25,000 | 60 min | 30-42 GB |
| Videos (100MB+) | ~40 | 30 min | 4-5 GB |
| **TOTAL** | **~25,040** | **90 min** | **35-47 GB** |

---

## If Something Goes Wrong

### "Permission denied" error
- You need Full Disk Access (see Prerequisites above)
- Make sure you **quit and reopened Terminal** after granting access

### Photos app won't import
- Make sure Photos is up to date
- Try quitting Photos and running the script again
- Check if Photos has enough space in its library

### Script freezes/crashes
- Press Ctrl+C to cancel
- Run the same command again - it will resume where it left off
- Your progress is saved!

### Want to undo something
- **Images**: Files are in `~/Desktop/iMessage_Images_REVIEW/`
  - To undo: Move files back to `~/Library/Messages/Attachments/`
- **Videos**: Files are in `~/Desktop/iMessage_Videos_REVIEW/`
  - To undo: Move files back to `~/Library/Messages/Attachments/`

### Not sure if videos are in Photos
- Open Photos app
- Use search to find the video filename
- Or browse by date (videos show modified date)

---

## Tips

- **Take breaks**: This doesn't have to be done all at once
- **Don't rush**: These are precious memories
- **Verify first**: Always check Photos before deleting review folders
- **Keep backups**: Consider waiting a week before final deletion
- **Start small**: Do images first, then just the 100MB+ videos

---

## Need Help?

1. Check the full [README.md](README.md) for detailed explanations
2. Look at the log files on your Desktop for errors
3. Create an issue on GitHub: https://github.com/scheinker/MessageClean/issues

---

## Summary Checklist

- [ ] Granted Terminal Full Disk Access
- [ ] Downloaded/updated tools from GitHub
- [ ] Ran assessment to understand storage
- [ ] Ran image importer (30-60 min)
- [ ] Verified images in Photos
- [ ] Deleted image review folder
- [ ] Ran video cleaner for 100MB+ videos (20-40 min)
- [ ] Verified videos in Photos
- [ ] Deleted video review folder
- [ ] Ran assessment again to confirm savings
- [ ] Celebrated freeing up 40+ GB! 🎉
