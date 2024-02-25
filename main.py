from scdownloader import SCDownloader

if __name__ == '__main__':
    with open('urls.txt') as urls:
        downloader = SCDownloader()
        downloader.load_urls(urls.read())
        downloader.execute()