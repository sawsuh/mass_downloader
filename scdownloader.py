import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import selenium
import time
from massdownloader import MassDownloader

def rem_sc(link: str):
    return link[len('https://soundcloud.com/'):]

class SCDownloader(MassDownloader): 
    def __init__(
        self, 
        *args, 
        adblocker_file: str = '/home/prashant/sdler/ablocker.crx', 
        button_wait_time: float = 20,
        click_wait_time: float = 0.01,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.button_wait_time = button_wait_time
        self.click_wait_time = click_wait_time
        self.adblocker_file = adblocker_file
        self.chrdriver_stagerrer = threading.Semaphore(1)

    def dl_target(self, link: str):
        while True:
            try:
                self.spots_left.acquire()
                try:
                    self.chrdriver_stagerrer.acquire()
                    chop = webdriver.ChromeOptions()
                    chop.page_load_strategy = 'eager'
                    prefs = {'download.default_directory' : self.dl_folder}
                    chop.add_experimental_option('prefs', prefs)
                    chop.add_extension(self.adblocker_file)
                    chop.add_argument("--headless=new")

                    driver = webdriver.Chrome(options = chop)
                except Exception as e:
                    raise e
                finally:
                    self.chrdriver_stagerrer.release()

                def click_fast(
                    xpath: str, 
                    message: str, 
                    return_element: bool = False, 
                    click: bool = True
                ):
                    self.event_staggerer.block_until_event(message = message)
                    WebDriverWait(driver, self.button_wait_time).until(EC.presence_of_element_located((By.XPATH, xpath)))
                    if click:
                        el = WebDriverWait(driver, self.button_wait_time).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                        time.sleep(self.click_wait_time)
                        Hover = ActionChains(driver).move_to_element(el)
                        Hover.click().perform()
                    if return_element:
                        return driver.find_element(By.XPATH, xpath)

                driver.get("https://soundcloudmp3.org/")

                input_xpath = '/html/body/div[2]/div[3]/div/div/div[1]/form/div/input[2]'
                input_box = click_fast(input_xpath, return_element=True, message = f'typing url in {rem_sc(link)}')
                input_box.send_keys(link)

                dl_xpath = '/html/body/div[2]/div[3]/div/div/div[1]/form/div/span/button'
                click_fast(dl_xpath, message = f'clicking get dl for {rem_sc(link)}')

                #time.sleep(3)
                dl_xpath = '/html/body/div[2]/div[3]/div/div/div[1]/div[2]/div[5]/a'
                click_fast(dl_xpath, message = f'clicking dl for {rem_sc(link)}')
                print(f'DOWNLOADING {rem_sc(link)}')
                time.sleep(self.dl_wait_time)
                print(f'{rem_sc(link)} downloaded (hopefully)')

                driver.close()
                return
            except Exception as e:
                print(f'{rem_sc(link)} died because {e}')
                time.sleep(0.1)
                pass
            finally:
                self.spots_left.release()