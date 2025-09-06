from pytube import YouTube

class YouTubeVideoDownloader:
    def __init__(self):
        pass

    def download(self, url):
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        print(f"Downloading: {yt.title}")
        # stream.download()  # Uncomment to actually download
        print("Download complete.")

    def demo(self):
        self.download('https://www.youtube.com/watch?v=dQw4w9WgXcQ')

if __name__ == "__main__":
    print("YouTube Video Downloader Demo")
    downloader = YouTubeVideoDownloader()
    # downloader.demo()  # Uncomment to run
