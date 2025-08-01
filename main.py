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

def get_available_formats(url):
    ydl_opts = {'quiet': True, 'skip_download': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info.get('formats', [])
        video_formats = [
            f"{f['format_id']} - {f.get('resolution', 'audio')} - {f.get('ext')} - {f.get('format_note', '')}"
            for f in formats if f.get('vcodec') != 'none'
        ]
        return info['id'], video_formats

def select_video_quality(sample_url):
    _, formats = get_available_formats(sample_url)
    console.print("\n📺 Available qualities from sample video:")
    return get_user_input("Select desired quality ID (e.g., 18, 22, 137):", formats).split()[0]

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

    # Sample video for quality detection
    sample_url = input("🔍 Enter a sample video URL from this playlist (to fetch available formats): ").strip()
    selected_format_id = select_video_quality(sample_url)

    # Output directory and filename
    output_path = input("\n📁 Enter output directory (leave empty for current folder): ").strip() or os.getcwd()
    filename_template = "%(playlist_index)s - %(title)s.%(ext)s"

    # Get playlist info to ask for range
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
        total_videos = len(info['entries'])

    start_index, end_index = ask_for_range(total_videos)
    videos_to_download = info['entries'][start_index:end_index]

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
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video['webpage_url']])

    # If any videos didn't have selected format
    if not_found_format:
        console.print("\n⚠️ Some videos didn't have the selected format.")
        reselect = input("Do you want to reselect quality and download them? (y/n): ").strip().lower()
        if reselect == 'y':
            selected_format_id = select_video_quality(not_found_format[0])
            for url in not_found_format:
                ydl_opts = {
                    'format': selected_format_id,
                    'outtmpl': os.path.join(output_path, filename_template),
                    'progress_hooks': [RichProgressHook()],
                    'quiet': True
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
        else:
            console.print("Skipped those videos.")

    console.print("\n✅ [bold green]All done![/bold green]")

if __name__ == "__main__":
    main()
