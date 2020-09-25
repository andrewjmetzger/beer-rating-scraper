import csv
import json
import pickle
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("user-agent=selenium-project")


def update_reviews_cbb():
    driver = webdriver.Chrome('driver/chromedriver', options=chrome_options)

    result_urls = ['https://beerandbrewing.com/beer-reviews/?q=&hPP=20&idx=cbb_web_review_search&p={}'.format(x)
                   for x in range(55)]
    links = []
    for result in result_urls:
        try:
            driver.get(result)
        except Exception as e:
            print(e)
            driver.quit()

        for i in range(1, 21):
            link = driver.find_element_by_xpath('//*[@id="hits"]/div/div[{}]/div/div/a'.format(i)).get_attribute('href')
            print(link)
            print("=" * 50)
            links.append(link)

        print("Finished dumping", result)
        driver.quit()

        print("Pickle contains {} review links".format(len(links)))
    pickle.dump(links, open('beer_cbb.pkl', 'wb'))
    driver.quit()


def export_pickled_beers():
    driver = webdriver.Chrome('driver/chromedriver', options=chrome_options)

    with open('beers_cbb.pkl', 'rb') as f:
        lst = pickle.load(f)
        f.close()

    csv_file = open('ratings_cbb.csv', 'w', encoding='utf-8')
    writer = csv.writer(csv_file)

    writer.writerow(
        ["total", "name", "brewer", "style", "abv", "ibu", "aroma_score", "appearance", "flavor_score", "mouthfeel",
         "brewer_description", "aroma_description", "flavor_description", "overall_description", "review_link", "title",
         "image", "brewer_split"])

    review_dict = {}

    index = 1
    for url in lst:
        brewer_split = "Not Available"
        brewer_description = "Not Available"
        aroma_description = "Not Available"
        flavor_description = "Not Available"
        overall_description = "Not Available"

        try:
            driver.get(url)
        except Exception as e:
            print(e)
            driver.quit()

        print("Scraping beer {} of {} ".format(index, len(lst)))
        try:
            title = driver.find_element_by_xpath('//*[@id="article-body"]/h1').text
        except Exception as e:
            print(e)
            title = "Fail"
        try:
            total = driver.find_element_by_class_name('main-score-overall').text
            total = re.findall(r'(.+)/100', total)[0]
        except Exception as e:
            print(e)
            total = "Fail"
        try:
            aroma_score = driver.find_element_by_xpath('//*/table/tbody/tr[1]/td[2]').text
        except Exception as e:
            print(e)
            aroma_score = "Fail"
        try:
            appearance = driver.find_element_by_xpath('//*/table/tbody/tr[2]/td[2]').text
        except Exception as e:
            print(e)
            appearance = "Fail"
        try:
            flavor_score = driver.find_element_by_xpath('//*/table/tbody/tr[3]/td[2]').text
        except Exception as e:
            print(e)
            flavor_score = "Fail"
        try:
            mouthfeel = driver.find_element_by_xpath('//*/table/tbody/tr[4]/td[2]').text
        except Exception as e:
            print(e)
            mouthfeel = "Fail"
        try:
            image = driver.find_element_by_xpath('//*/div[@id="article-image"]/img').get_attribute('src')
        except Exception as e:
            print(e)
            image = "Fail"
        try:
            style = driver.find_element_by_xpath('//*/div[@class="review-meta-holder"]/p[1]').text
            style = style.replace('Style: ', '')
        except Exception as e:
            print(e)
            style = "Fail!"
        try:
            abv = driver.find_element_by_xpath('//div[@class="review-meta-holder"]/p[2]').text
            if len(abv) > 0:
                abv = re.findall(r'ABV: (.+\..+) IBU:', abv)[0]
            else:
                abv = "Not Available"
        except Exception as e:
            print(e)
            abv = "Not Available"
        try:
            ibu = driver.find_element_by_xpath('//div[@class="review-meta-holder"]/p[2]').text
            ibu = re.findall(r'IBU: (.+)', ibu)[0]
        except Exception as e:
            print(e)
            ibu = "Not Available"

        # Review content
        # TODO:  Edge cases. This XPath expression should grab all paragraphs of the article-body,
        #  which SHOULD be 4. Sometimes this is not 4, though, which is sad.
        try:
            # Get every paragraph in the review
            review_paragraphs = driver.find_elements_by_xpath('//*[@id="article-body"]/*/p')
            review_text = []

            # Make a list containing all paragraphs
            for p in review_paragraphs:
                review_text.append(p.text)

            # Flatten every paragraph into one long string
            review_text = "".join(review_text)

            # Remove paragraph labels
            review_text = review_text.replace('Aroma: ', '')
            review_text = review_text.replace('Flavor: ', '')
            review_text = review_text.replace('Overall: ', '')

            # Split at each quotation mark
            review_text = re.split('”“', review_text)
            print("len review-text:", len(review_text))
            if len(review_text) < 3:
                print(url)
                print("/!\\ " * 5)
                print("WARNING: Paragraphs should have at least 3, but has {}. See below:".format(len(review_text)))
                print(*review_text, sep='\n')
                print("/!\\ " * 5)

            if len(review_text) > 3:
                try:
                    brewer_description = review_text[0][1:]
                except IndexError:
                    brewer_description = "Not Available"
                try:
                    aroma_description = review_text[1]
                except IndexError:
                    aroma_description = "Not Available"
                try:
                    flavor_description = review_text[2]
                except IndexError:
                    flavor_description = "Not Available"
                try:
                    overall_description = review_text[3][:-1]
                except IndexError:
                    overall_description = "Not Available"
        except Exception as e:
            print(e)
            overall_description = "Fail"
            brewer_description = "Fail"
            aroma_description = "Fail"
            flavor_description = "Fail"
        try:
            brewer_split = re.findall(r'/review/(\S+)/', url)[0]
            xyz = brewer_split.replace('-', ' ')
            if len(re.findall(' ', xyz)) > 0:
                xyz = xyz.split(' ')
                brewer = re.findall('(.+) ' + xyz[0][:-2], title, re.IGNORECASE)[0]
                name = re.findall(brewer + ' (.+)', title, re.IGNORECASE)[0]
            elif len(re.findall('(.+) ' + xyz[0][:-2], title, re.IGNORECASE)) > 0:
                brewer = re.findall('(.+) ' + xyz[0][:-2], title, re.IGNORECASE)[0]
                name = re.findall(brewer + ' (.+)', title, re.IGNORECASE)[0]
            else:
                name = title
                brewer = "Fail: See Title"
        except Exception as e:
            print(e)
            name = "Fail"
            brewer = "Fail"

        # Assemble the dict entry for each beer
        review_dict["total"] = total
        review_dict["name"] = name
        review_dict["brewer"] = brewer
        review_dict["style"] = style
        review_dict["abv"] = abv
        review_dict["ibu"] = ibu
        review_dict["aroma_score"] = aroma_score
        review_dict["appearance"] = appearance
        review_dict["flavor_score"] = flavor_score
        review_dict["mouthfeel"] = mouthfeel
        review_dict["brewer_description"] = brewer_description
        review_dict["aroma_description"] = aroma_description
        review_dict["flavor_description"] = flavor_description
        review_dict["overall_description"] = overall_description
        review_dict["review_link"] = url
        review_dict["page_title"] = title
        review_dict["image"] = image
        review_dict["brewer_split"] = brewer_split

        if False:
            print(json.dumps(review_dict, indent=2))

        writer.writerow(review_dict.values())
        index += 1
        print("*" * 50)

    csv_file.close()
    driver.quit()


export_pickled_beers()
