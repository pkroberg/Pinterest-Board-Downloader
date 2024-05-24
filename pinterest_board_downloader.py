import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# function to run the selenium webdriver
def init_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# function to scrape the pinterest board image urls
def get_image_urls(board_url):
    driver = init_driver()
    driver.get(board_url)
    time.sleep(5) # wait for the pinterest board page to load

    # scroll to the bottom of the page to load all the images
    scroll_pause_time = 2
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    image_tags = soup.find_all("img", {"src": True})
    image_urls = [img["src"] for img in image_tags]
    return image_urls

# function to download the images
def download_images(image_urls, download_dir="downloads"):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    for i, url in enumerate(image_urls):
        try:
            response = requests.get(url)
            response.raise_for_status()
            with open(os.path.join(download_dir, f'image_{i}.jpg'), 'wb') as file:
                file.write(response.content)
            print(f"Downloaded image_{i+1}/{len(image_urls)}")
        except Exception as e:
            print(f"Could not download image {i+1}/{len(image_urls)}. Error: {e}")

# main function
def main(board_url):
    print("Scraping Pinterest board...")
    image_urls = get_image_urls(board_url)
    print(f"Found {len(image_urls)} images. Downloading...")
    download_images(image_urls)
    print("Download complete!")

if __name__ == "__main__":
    board_url = "https://www.pinterest.com/pkroberg/accessories/"
    main(board_url)

