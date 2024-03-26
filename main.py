from massdownloader import ChromiumDownloader, MassDownloader

if __name__ == "__main__":
    with open("urls.txt") as urls:
        downloader = ChromiumDownloader()
        downloader.load_urls(urls.read())
        downloader.execute()
        print(1, 2, 3)
