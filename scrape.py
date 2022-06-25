import json
import pickle
import re
import time

import pandas as pd
import plotly.express as px
import urllib3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from get_otp_code import get_otp_code

urllib3.disable_warnings()

serialize = False
# You can get the country code from https://myair.resmed.com/CountrySelection.aspx?redirectPage=0
country_code = '24'  # France

config = None
with open('config.json') as fh:
    config = json.loads(fh.read())


url_resmed = 'https://myair2.resmed.com/'


def get_page_soup():

    # Select "headless"
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")

    # Instantiate the ChromeDriver
    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s, options=options)

    # Connect to Resmed website, type in fields and submit
    print('Connecting to Resmed website : ', url_resmed)
    driver.get(url_resmed)

    # driver.execute_script("__doPostBack('ctl00$ctl00$PageContent$MainPageContent$franceSelector$linkCountry','')")
    # WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "ctl00$ctl00$PageContent$MainPageContent$franceSelector$linkCountry"))).click()
    
    try:
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id = "region-EU"]/div/div[1]/ul/li[6]/a'))).click()
        print("Country chosen")
    except TimeoutException:
        print("Country not found")
    
    # https://stackoverflow.com/questions/59374469/how-to-paginate-through-the-page-numbers-when-href-contains-javascript-dopostb/59377905#59377905

    # driver.find_element(
    #     By.ID, 'ctl00$ctl00$PageContent$MainPageContent$franceSelector$linkCountry').click()
    driver.find_element(By.ID,
                        'okta-signin-username').send_keys(config['rs_email'])
    driver.find_element(By.ID,
                        'okta-signin-password').send_keys(config['rs_password'])
    driver.find_element(By.ID,
                        'okta-signin-submit').send_keys(Keys.RETURN)

    # Sleep 5 second to receive the OTP email on gmail
    time.sleep(5)
    # if driver.find_element(By.CLASS_NAME,'c-alert--small'): print('Too many auth error please wait')

    # GEt the the OTP password and submit

    driver.find_element(By.ID,
                        'input112').send_keys(get_otp_code(config['gm_email'], config['gm_password']))
    print('Sending OTP password')
    driver.find_element(By.XPATH,
                        '//*[@id="form96"]/div[2]/input').send_keys(Keys.RETURN)

    # Sleep to have time to switch page
    time.sleep(5)

    # Get the url session aprameter => u=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    session = driver.current_url.split('?')[1]

    # Get the history page with the session argument
    print('Accessing the History page')
    driver.get('https://myair.resmed.eu/History.aspx?'+session)

    # return the page source
    return BeautifulSoup(driver.page_source, features='lxml')


if __name__ == '__main__':

    soup = get_page_soup()

    scripts = soup.find_all('script')
    scores_script = [x.renderContents()
                     for x in scripts if b'myScores' in x.renderContents()][0]
    matches = re.findall(
        r'\{\"HistorySummary.*\}\]\}\]\}', scores_script.decode('UTF-8'))

    my_scores = json.loads(''.join(matches))

    if serialize:
        with open('old/my_scores.pickle', 'wb') as f:
            pickle.dump(my_scores, f)

    DF = pd.DataFrame([])
    for i in range(12):
        month_score = my_scores['HistorySummary'][i]['Data']
        DF = DF.append(pd.DataFrame(month_score))
    DF[['DayNumber', 'Score', 'UsageScore', 'MaskScore', 'EventsScore']] = DF[[
        'DayNumber', 'Score', 'UsageScore', 'MaskScore', 'EventsScore']].astype(int)
    print(DF.to_csv())
