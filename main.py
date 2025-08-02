import os
import yt_dlp
from rich.progress import Progress
from rich.console import Console

console = Console()

def get_user_input(prompt, options):
    console.print(f"\n[bold cyan]{prompt}[/bold cyan]")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    choice = input("Choose an option (number): ").strip()
    while not (choice.isdigit() and 1 <= int(choice) <= len(options)):
        choice = input("Invalid input. Choose a valid option (number): ").strip()
    return options[int(choice) - 1]

def ask_for_range(total):
    console.print(f"\nPlaylist contains [green]{total}[/green] videos.")
    start = input("Start from video number (default 1): ").strip()
    end = input("End at video number (default last): ").strip()
    start = int(start) if start.isdigit() else 1
    end = int(end) if end.isdigit() else total
    return start - 1, end  # yt-dlp uses 0-based index for playlist_items

def get_formats_from_video(video_info):
    formats = video_info.get('formats', [])
    video_formats = [
        f"{f['format_id']} - {f.get('resolution', 'audio')} - {f.get('ext')} - {f.get('format_note', '')}"
        for f in formats if f.get('vcodec') != 'none'
    ]
    return video_formats

def select_quality_from_video(video_info):
    formats = get_formats_from_video(video_info)
    console.print("\n📺 Available formats from first video:")
    selected = get_user_input("Select desired format:", formats)
    return selected.split()[0]  # Extract format_id

class RichProgressHook:
    def __init__(self):
        self.progress = Progress()
        self.task = None

    def __call__(self, d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            if not self.task and total_bytes:
                self.task = self.progress.add_task("[green]Downloading...", total=total_bytes)
                self.progress.start()
            if self.task and total_bytes:
                self.progress.update(self.task, completed=d['downloaded_bytes'])
        elif d['status'] == 'finished':
            if self.task:
                self.progress.update(self.task, completed=self.progress.tasks[0].total)
                self.progress.stop()

def main():
    console.print("[bold yellow]📥 YouTube Playlist Downloader[/bold yellow]")

    # Playlist URL
    playlist_url = input("\n🔗 Enter the YouTube playlist URL: ").strip()

    # Ask for Chrome profile name
    chrome_profile = input("\n🧠 Enter your Chrome profile name (e.g., Default, Profile 1, etc.): ").strip() or "Default"

    # Get playlist metadata (including first video)
    ydl_init_opts = {
        'quiet': True,
        'extract_flat': False,
        'cookiesfrombrowser': ('chrome', chrome_profile)

    }


    with yt_dlp.YoutubeDL(ydl_init_opts) as ydl:
        playlist_info = ydl.extract_info(playlist_url, download=False)
        entries = playlist_info['entries']
        total_videos = len(entries)
        first_video = entries[0] if entries else None
        if not first_video:
            console.print("[red]No videos found in playlist.[/red]")
            return

    # Let user choose format from first video
    selected_format_id = select_quality_from_video(first_video)

    # Output directory and naming
    output_path = input("\n📁 Enter output directory (leave empty for current folder): ").strip() or os.getcwd()
    filename_template = "%(playlist_index)s - %(title)s.%(ext)s"

    # Ask for range of videos
    start_index, end_index = ask_for_range(total_videos)
    videos_to_download = entries[start_index:end_index]

    not_found_format = []

    for video in videos_to_download:
        if not video:
            continue
        console.print(f"\n🎬 Processing: {video['title']}")
        available_format_ids = [f['format_id'] for f in video.get('formats', []) if f.get('vcodec') != 'none']
        if selected_format_id not in available_format_ids:
            console.print(f"[red]❌ Format {selected_format_id} not available for this video.[/red]")
            not_found_format.append(video['webpage_url'])
            continue

        ydl_opts = {
            'format': selected_format_id,
            'outtmpl': os.path.join(output_path, filename_template),
            'progress_hooks': [RichProgressHook()],
            'quiet': True,
            'cookiesfrombrowser': ('chrome', chrome_profile),
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video['webpage_url']])

    # Retry for skipped videos
    if not_found_format:
        console.print("\n⚠️ Some videos didn't have the selected format.")
        reselect = input("Do you want to reselect quality and download them? (y/n): ").strip().lower()
        if reselect == 'y':
            with yt_dlp.YoutubeDL({'quiet': True, 'cookiesfrombrowser': ('chrome', chrome_profile)}) as ydl:
                sample_retry_info = ydl.extract_info(not_found_format[0], download=False)
            selected_format_id = select_quality_from_video(sample_retry_info)
            for url in not_found_format:
                ydl_opts = {
                    'format': selected_format_id,
                    'outtmpl': os.path.join(output_path, filename_template),
                    'progress_hooks': [RichProgressHook()],
                    'quiet': True,
                    'cookiesfrombrowser': ('chrome', chrome_profile),
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
        else:
            console.print("Skipped those videos.")

    console.print("\n✅ [bold green]All done![/bold green]")

if __name__ == "__main__":
    main()
