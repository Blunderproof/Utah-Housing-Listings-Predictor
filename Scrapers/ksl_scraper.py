# import libraries
import time
import requests
import re
from bs4 import BeautifulSoup
import json
import csv

from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys


def addUniqueListingIDsToQueue(listingIDs, fileSrc):
    # get the current queue of listings
    with open(fileSrc, 'r') as f:
        currQueue = [listing.strip('\n') for listing in f.readlines()]
    uniqueListings = list( set(currQueue) - set(listingIDs))

    with open(fileSrc, 'a') as f:
        for listing in uniqueListings:
            f.write("%s\n" % listing)
    print("Finished adding %s unique listings to the queue", len(uniqueListings))

# Opens an instance of Chrome to enable the JS scroll update, adding more listings to the search, then it collect their URIs 
def seleniumScrape(pagedown_count=200):
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

    listingIDs = [listing.get_attribute("id") for listing in listingObjs]
    # save the Listing IDs to a file
    with open('listingIDs.txt', 'w') as f:
        for listingID in listingIDs:
            f.write("%s\n" % listingID)
    print("Finished collecting listings")

    return listingIDs

def extractListingDetails(base_url, listingID):
    # url = "https://homes.ksl.com/listing/40310982"
    # Need to send a proper user agent header so that we don't get a 403 Forbidden response
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

# save all currently collected listings to a json
def collect(listingIDs):
    # the used listings list is for preventing duplicate searching of a given listing if an exception is encountered
    listingData = []
    usedListingIDs = []

    # if an error is encountered save what has been collected, try again
    try:
        for i, listingID in enumerate(listingIDs):
            print("Extracting from Listing: %s, %s of %s" % (listingID, i, len(listingIDs)))
            
            usedListingIDs.append(listingID)
            listingData.append(extractListingDetails("https://homes.ksl.com/listing/", listingID))

        # Entire queue processed at this point
        # add the listing data to a csv
        print("FINISH PROCESSING QUEUE ----------------")
        keys = listingData[0]['content'].keys()
        with open('listings.csv', 'a', newline='') as outfile:
            dict_writer = csv.DictWriter(outfile, fieldnames=keys)
            dict_writer.writerows(listingData)
        print("Saved listings to log")

        # Remove all listings from queue file
        open('listingIDs.txt', 'w').close()

    except KeyboardInterrupt:
        print("Keyboard Interrupt, saving data to csv")

        # Add the listing data to a csv
        keys = listingData[0].keys()
        with open('listings.csv', 'a', newline='') as outfile:
            dict_writer = csv.DictWriter(outfile, fieldnames=keys)
            dict_writer.writerows(listingData)
        
        # update the queue
        unusedListings = list( set(listingIDs) - set(usedListingIDs))
        with open("listingsIDs.txt", "w") as f:
            for listing in unusedListings:
                f.write("%s\n" % listing)

        
    except Exception as e:
        print("Exception found: ----------------------------------")
        print(e)
        print("\nSaving what has been currently found and continuing listing queue")
        
        # Add the listing data to a csv
        keys = listingData[0].keys()
        with open('listings.csv', 'a', newline='') as outfile:
            dict_writer = csv.DictWriter(outfile, fieldnames=keys)
            dict_writer.writerows(listingData)

        # update the queue
        unusedListings = list( set(listingIDs) - set(usedListingIDs))
        with open("listingsIDs.txt", "w") as f:
            for listing in unusedListings:
                f.write("%s\n" % listing)

        # re-run the collect function on the remaining listings
        collect(unusedListings)


if __name__ == "__main__":
    # scrape IDs
    # listingIDs = seleniumScrape()
    # addUniqueListingIDsToQueue(listingIDs, fileSrc="listingIDs.txt")

    # grab the queue
    with open('listingIDs.txt', 'r') as f:
        listingIDs = [listing.strip('\n') for listing in f.readlines()]
        print("Recovering Listing IDs from file")
    # process the queue

    # Init the CSV
    print("Initializing the CSV")
    sampleListing = extractListingDetails("https://homes.ksl.com/listing/", listingIDs[0])
    keys = sampleListing['content'].keys()
    # print(sampleListing)
    print(keys)
    with open('listings.csv', 'w', newline='') as outfile:
        dict_writer = csv.DictWriter(outfile, fieldnames=keys)
        dict_writer.writeheader()

    collect(listingIDs)