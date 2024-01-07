from scdownloader import SCDownloader

if __name__ == '__main__':
    with open('urls.txt') as urls:
        downloader = SCDownloader(rm_dls = False)
        downloader.load_urls(
            [url for url in urls.read().split('\n') if len(url)>0]
        )
        downloader.execute()