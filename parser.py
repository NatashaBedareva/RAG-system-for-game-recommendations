from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from datetime import datetime
import sqlite3
from db import add_data_to_db
import time

def parser_card(driver):
  
    try:
        name_game = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH,  '//*[@id="info"]/h1'))) 
    
        name_game_text = name_game.text
    except Exception:
        return

    name_game_text = name_game.text

    grade_text=None
    try:
        grade_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='ReviewsTotal-module__progressText']")))
        grade_text = grade_element.text
    except Exception:
        print("Оценки нет")

    grade_text = f"Средняя оценка: {grade_text}" if grade_text is not None else "Средняя оценка: нет"
    
    about_game_block = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#about-game-description"))
    )

    about_game_text = about_game_block.text

    genres = driver.find_elements(By.CSS_SELECTOR, "a[class*='genreChip']")
   
    genre_list = []
    for genre in genres:
        if genre.text:
            genre_list.append(genre.text)

    genre_text = ", ".join(genre_list)

    order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    url_game = str(driver.current_url)

    add_data_to_db(
        (name_game_text, url_game, "Жанр: " + genre_text + " "+ grade_text + about_game_text, order_date)
    )

    

def run_parser():

    options = Options()
    #options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--remote-allow-origins=*") 
    options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    driver = webdriver.Chrome(options=options)

    driver.get("https://vkplay.ru/play/")
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='GameCardHover-module__cardContainer']")))

    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    max_num_page = int(driver.find_element(By.CSS_SELECTOR, "a[data-test='last_page']").text)

    print(max_num_page) 
    
   
    for i in range(max_num_page-5):
    
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='GameCardHover-module__cardContainer']")))
        cards = driver.find_elements(By.CSS_SELECTOR,"div[class*='GameCardHover-module__cardContainer']")
        total_cards = len(cards)
        print(i,total_cards)

        main_window = driver.current_window_handle
        for num_card in range(total_cards):
            
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable( cards[num_card]))
            
            try: 
                cards[num_card].click()
                all_windows = driver.window_handles

                if len(all_windows) > 1:
                    driver.switch_to.window(all_windows[-1]) 
                print(num_card)
                parser_card(driver)
                
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(main_window)
            except Exception as e :
                print(f"Не получилось: {type(e).__name__}: {e}")
                    

        button_next_page = driver.find_element(By.XPATH, '//*[@id="vkp-app-shell"]/div/main/div/div[3]/div/div[4]/button[2]')
        button_next_page.click()


