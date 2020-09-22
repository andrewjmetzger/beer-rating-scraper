import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

f = open('beers.csv', 'w')
f.write('Score;Beer;ABV\n')

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome('driver/chromedriver', options=chrome_options)

driver.get('http://www.tastings.com/Search-Beer.aspx')

# Set time range to all listings
driver.find_element_by_xpath('//*[@id="radReviewDate_10"]').click()
# Wait 3 seconds for the filter to apply
time.sleep(3)

# Get total number of pages
last_page = int(driver.find_element_by_xpath('//*[@id="spaSearchPageMsg"]').text.split(' ')[3])
for page in range(last_page):
    current_page = int(driver.find_element_by_xpath('//*[@id="spaSearchPageMsg"]').text.split(' ')[1])
    print("Reading page " + str(page + 1) + ' of ' + str(last_page))

    results = driver.find_elements_by_class_name('m-search-item-container-q')

    for r in results:
        beer = r.find_element_by_class_name('m-search-item-text')
        score = r.find_element_by_class_name('m-search-item-points-container').text.split('\n')[0]
        beer_name = beer.get_attribute('innerHTML').split(' <i>')[0].strip().replace('&amp;', '&')

        try:
            beer_abv = beer.find_element_by_tag_name('i').text
        except NoSuchElementException:
            beer_abv = 'Unknown'

        f.write(score + ';' + beer_name + ';' + beer_abv + '\n')

    # Go to next page
    driver.find_element_by_partial_link_text("»").click()
    time.sleep(3)

driver.quit()
