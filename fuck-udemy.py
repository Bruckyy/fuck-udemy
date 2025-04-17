import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv
import argparse
import os
import time
import random
from tqdm import tqdm

parser = argparse.ArgumentParser(description="Launch and monitor multiple video tabs.")
parser.add_argument('--no-headless', action='store_true', help='Run browser in non-headless mode')
parser.add_argument('--wait-timeout', type=int, default=10, help='WebDriver wait timeout in seconds')
parser.add_argument('--video-file', type=str, default='videos.txt', help='Path to file with video URLs')
parser.add_argument('--max-runtime', type=int, default=2, help='Maximum runtime in hours (default: 2 hours)')
parser.add_argument('--log-timestamps', action='store_true', help='Log video timestamps every 60 seconds /!\\ DEBUG purpose ONLY otherwise the program will be very slow, especially with large batch of videos')
parser.add_argument('--max-tabs', type=int, default=30, help='Maximum number of tabs per browser instance')
args = parser.parse_args()

HEADLESS = not args.no_headless
WAIT_TIMEOUT = args.wait_timeout
VIDEO_FILE = args.video_file
MAX_TABS = args.max_tabs

load_dotenv(".cookies")
cookies = [
    {'name': 'access_token', 'value': os.getenv("ACCESS_TOKEN")},
    {'name': 'dj_session_id', 'value': os.getenv("DJ_SESSION_ID")}
]

if not os.path.isfile(VIDEO_FILE):
    print(f"[x] Error: The file '{VIDEO_FILE}' does not exist.")
    exit(1)

if os.path.getsize(VIDEO_FILE) == 0:
    print(f"[x] Error: The file '{VIDEO_FILE}' is empty.")
    exit(1)

with open(VIDEO_FILE, 'r') as f:
    video_urls = [line.strip() for line in f if line.strip()]


def create_driver():
    options = uc.ChromeOptions()

    if HEADLESS:
        options.add_argument("--headless=new")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-notifications")
    options.add_argument("--mute-audio")
    options.add_argument("--disable-extensions")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-popup-blocking")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    return uc.Chrome(options=options)

def inject_cookies(driver, domain):
    driver.get(domain)
    WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            print(f"[x] Failed to inject cookie: {e}")

def simulate_human(driver):
    try:
        ActionChains(driver).move_by_offset(random.randint(5, 30), random.randint(5, 30)).perform()
    except:
        pass

def play_video(driver):
    try:
        WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.TAG_NAME, 'video')))
        time.sleep(0.1)
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.SPACE)
    except Exception as e:
        print(f"[x] Could not trigger play: {e}")

def is_video_ended(driver):
    try:
        return driver.execute_script("return document.querySelector('video')?.ended")
    except Exception as e:
        print(f"[x] Could not determine if video is ended: {e}")
        return False
    
def is_video_paused(driver):
    try:
        return driver.execute_script("return document.querySelector('video')?.paused")
    except Exception as e:
        print(f"[x] Could not determine if video is paused: {e}")
        return False


def get_video_timestamp(driver):
    try:
        seconds = driver.execute_script("return document.querySelector('video')?.currentTime")
        if seconds is not None:
            minutes = round(seconds / 60, 2)
            return minutes
        else:
            return None
    except Exception as e:
        print(f"[x] Could not get video timestamp: {e}")
        return None


from threading import Thread

def main():
    video_chunks = [video_urls[i:i + MAX_TABS] for i in range(0, len(video_urls), MAX_TABS)]
    drivers = []

    print("\n")
    for chunk_num, chunk in enumerate(video_chunks):
        print(f"\n=== [Chunk {chunk_num + 1}/{len(video_chunks)}] Processing {len(chunk)} videos ===")

        driver = create_driver()
        drivers.append(driver)
        tab_urls = []

        for i, url in tqdm(enumerate(chunk), total=len(chunk), desc="Loading Videos", unit="video"):
            domain = "https://" + url.split("/")[2]

            if i == 0:
                inject_cookies(driver, domain)
                driver.get(url)
            else:
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
                inject_cookies(driver, domain)
                driver.get(url)

            time.sleep(1)
            simulate_human(driver)
            time.sleep(0.2)
            play_video(driver)

            tab_urls.append(driver.current_url)

    print(f"\n[+] {sum(len(d.window_handles) for d in drivers)} videos started successfully.")

    try:
        end_time = time.time() + (args.max_runtime * 3600)
        while time.time() < end_time:
            all_closed = True

            for driver in drivers:
                if not driver.window_handles:
                    continue

                all_closed = False

                if args.log_timestamps:
                    print("--------------------------------")

                for handle in driver.window_handles[:]:
                    try:
                        driver.switch_to.window(handle)
                        simulate_human(driver)

                        timestamp = get_video_timestamp(driver)

                        try:
                            video_id = driver.current_url.split('/lecture/', 1)[1].split('/', 1)[0].split('#', 1)[0]
                        except IndexError:
                            video_id = "unknown"

                        if args.log_timestamps:
                            print(f"[{video_id}] {timestamp} min")

                        if is_video_ended(driver):
                            print(f"[{video_id}] Video ended")
                            driver.close()
                            continue

                        if is_video_paused(driver):
                            play_video(driver)

                    except Exception as e:
                        print(f"[x] Failed to check or close tab: {e}")
                        continue

            if all_closed:
                break

            time.sleep(30)

    except Exception as e:
        print(f"[x] WebDriver session ended unexpectedly: {e}")

    print("[+] All video tabs have been closed.")

    for driver in drivers:
        try:
            driver.quit()
        except:
            pass


if __name__ == "__main__":
    main()
