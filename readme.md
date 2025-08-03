# 🎬 YouTube Playlist Downloader (Interactive CLI)

An interactive command-line script to download entire YouTube playlists using [`yt-dlp`](https://github.com/yt-dlp/yt-dlp).  
Designed to be user-friendly, fully configurable through prompts, and privacy-aware with support for browser cookies.

> 🧠 This script was generated with the assistance of AI (ChatGPT), and refined for human usability and clarity.

---

## ✨ Features

- ✅ **Download full YouTube playlists**
- 🎛️ **Interactive mode** – choose format, quality, range, and output path
- 🎥 **Quality picker** – select from available video resolutions/formats
- 📈 **Download progress bar** using `rich`
- 📦 **Partial playlist support** – download a custom range (e.g., 5–20)
- 🔐 **Chrome browser cookies support** – access age-restricted or private videos
- 🧱 **Fallback handling** – reselect quality if some videos don’t support your choice

---

## 📦 Installation

### 1. Install Python 3.7+
Make sure Python is installed. You can check with:

```bash
python --version
```



🔐 Chrome Cookies Support
-------------------------

This script can extract your session cookies directly from Chrome, enabling:

*   Downloads from **private or unlisted videos**
    
*   Access to **age- or region-restricted content**
    
*   Ability to download videos as if you're logged in
    

### 🧠 How to find your Chrome profile name:

Go to your Chrome user data folder:

*   **Linux:** ~/.config/google-chrome/
    
*   **Windows:** %LOCALAPPDATA%\\Google\\Chrome\\User Data\\
    
*   **macOS:** ~/Library/Application Support/Google/Chrome/
    

Look for folders like:

*   Default (main profile)
    
*   Profile 1
    
*   Profile 2
    
*   etc.
    

Use the folder name as your profile in the prompt.




## 📝 Example
$ python playlist_downloader.py

🔗 Enter the YouTube playlist URL: https://www.youtube.com/playlist?list=PLxyz...

🧠 Enter your Chrome profile name: Profile 1

📺 Available formats from first video:
1. 18 - 360p - mp4
2. 22 - 720p - mp4
3. 137 - 1080p - mp4

Choose an option (number): 2

📁 Enter output directory (leave empty for current folder): /home/user/Videos
Playlist contains 15 videos.

Start from video number (default 1): 3

End at video number (default last): 10

...

✅ All done!




🧩 FAQ
------

### ❓ Why does it ask for a Chrome profile?

To grab your cookies so yt-dlp can access protected content you're signed into.

### ❓ Can I use Firefox instead?

Not yet — but the script can be modified to support firefox with a similar syntax.

### ❓ Will it download private videos from channels I’m subscribed to?

Yes, **if** you're logged in to Chrome with access to that video and choose the correct profile.

💡 License
----------

This script is provided under the MIT License. You’re free to use, modify, and distribute it.