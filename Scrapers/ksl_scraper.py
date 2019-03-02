# import libraries
import time
import requests
import re
from bs4 import BeautifulSoup
import json

from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys


# Opens an instance of Chrome to enable the JS scroll update, adding more listings to the search, then collect their URIs 
def seleniumScrape(pagedown_count=2):
    listingIDs = []

    browser = webdriver.Chrome(ChromeDriverManager().install())
    browser.get("https://homes.ksl.com/search/?reset=0")
    time.sleep(2)

    # Page-down here for the page to load more content.     
    elem = browser.find_element_by_tag_name("body")
    while pagedown_count:
        elem.send_keys(Keys.PAGE_DOWN)
        elem.send_keys(Keys.PAGE_DOWN)
        # TODO: end early if revisiting previous obs
        time.sleep(1)
        pagedown_count-=1

    # Find all listing after scrolling down and loading more content 
    listingObjs = browser.find_elements_by_class_name("Listing")
    for listing in listingObjs:
        listingIDs.append(listing.get_attribute("id"))
    return listingIDs


def extractListingDetails(base_url, listingID):
    # url = "https://homes.ksl.com/listing/40310982"
    # Need to send a proper user agent header so that we don't get a 403 Forbidden response
    print("Extracting from Listing: ", listingID)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36',
    }
    # make request with requests library, parse it with BeautifulSoup
    page_response = requests.get(base_url + listingID, headers= headers, timeout=5)
    page_cotent = BeautifulSoup(page_response.content, "html.parser")

    # Find the relevant features
    listingDetails = re.search(r'pageDetails":(.*?})', page_cotent.text).group(1)

    # parse the string into a python dictionary
    listingContent = json.loads(listingDetails)
    listingDict = {
        "key": listingID,
        "content":listingContent
    }
    return listingDict

def saveToLog(listingIDs):
    listings = []
    for listingID in listingIDs:
        listings.append(extractListingDetails("https://homes.ksl.com/listing/", listingID))
    with open('listings.json', 'w+') as outfile:  
        json.dump(listings, outfile, indent=4)
    print("Saved listings to log")

if __name__ == "__main__":
    listingIDs = seleniumScrape()
    saveToLog(listingIDs)