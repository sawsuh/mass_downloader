from scdownloader import SCDownloader

sc_urls = '''
https://soundcloud.com/sano-sc/hard
https://soundcloud.com/elevaterecordsuk/turno-x-skantia-engage-1
https://soundcloud.com/boudnb/cous-cous-1
https://soundcloud.com/mackygee/chicken-neck
https://soundcloud.com/harleyd/vibrations
https://soundcloud.com/bladerunner-dnb/rave-machine
https://soundcloud.com/toxinate/nope
https://soundcloud.com/krustydj/katy-b-5-am-krusty-dnb-bootleg
https://soundcloud.com/crucast/spice-so-mi-like-it-burt-cope-bootleg
https://soundcloud.com/dnballstars/phibes-bassdrop
https://soundcloud.com/crossydnb/napes-talk-to-me-proper-crossy-monroller-remix
https://soundcloud.com/beatsbasslife/higherlevel
https://soundcloud.com/filthyhabitsdnb/noxxic-jay-jay-wtf-filthy-habits-remix
https://soundcloud.com/herbzc/latte-load-up-herbz-remix-5k-free-dl
https://soundcloud.com/buunshin/dancing-in-the-dark
https://soundcloud.com/y_u_qt/lo5ive-remix
https://soundcloud.com/monkywow/oppidan-chamber-of-reflection
https://soundcloud.com/sillyugly/marone-ragga-waving-one-year-of-sillyugly
'''

if __name__ == '__main__':
    downloader = SCDownloader(rm_dls = False)
    downloader.load_urls(sc_urls)
    downloader.execute()