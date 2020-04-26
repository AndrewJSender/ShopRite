import sys, os, re, requests, time, datetime, getpass
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from twilio.rest import Client

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
chromedriver = ROOT_DIR + "/chromedriver"

# amazon credentials
repeat_interval_sec  = 30
refresh_interval_sec = 5
max_attempts         = 12
shoprite_username = "Sender118@aol.com"
# shoprite_password = getpass.getpass(prompt='Enter your password:')
with open ("../../shoprite_password", "r") as myfile:
    shoprite_password=myfile.read().strip("\n")
shoprite_store_id = '1420746' #Chatham


# twilio configuration
to_mobilenumber = "+18888888888"
from_mobilenumber = "+19999999999"
account_sid = "fake_account_sid"
auth_token = "fake_auth_token"
client = Client(account_sid, auth_token)

def create_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    driver = webdriver.Chrome(chromedriver, chrome_options=chrome_options)
    return driver

def terminate(driver):
    driver.quit()

def check_slots():
    try:
        print('Creating Chrome Driver ...')
        driver = create_driver()

        print('Logging into ShopRite ...')
        driver.get('https://shop.shoprite.com/store/{}'.format(shoprite_store_id))
        time.sleep(2.0)
        email_field = driver.find_element_by_name('Email')
        email_field.send_keys(shoprite_username)
        password_field = driver.find_element_by_name('Password')
        password_field.send_keys(shoprite_password)
        driver.find_element_by_id('SignIn').click()
        time.sleep(1.5)

        print('Checkout Step One ...')
        cart = driver.find_element_by_class_name('accountMenu__cart')
        cart.click()
        time.sleep(0.5)
        print('Checkout Step Two ... Reserve Slot')
        driver.get('https://shop.shoprite.com/store/{}/cart'.format(shoprite_store_id))
        time.sleep(1.5)
        driver.get('https://shop.shoprite.com/store/{}/reserve-timeslot'.format(shoprite_store_id))
        time.sleep(1.5)

        slots_available = []
        
        for attempt in range(1,max_attempts):
            print("Attempt #{}".format(attempt))
            select_pickup = driver.find_element_by_css_selector('button.fulfillmentOption__button')
            driver.execute_script("window.scrollTo({}, {})".format(select_pickup.rect['x'], select_pickup.rect['y'])) 
            select_pickup.click()
            time.sleep(2.5)

            #Read & Pick Time Slot
            slots = driver.find_elements_by_css_selector('.timeslotPicker__timeslotButton')
            for slot in slots:
                if slot.text == 'Sold Out' or slot.text == '':
                    print('Not available for slot'.format(slot))
                else:
                    slots_available.append(slot)
            if slots_available:
                # while True:
                #     os.system('say "Beer time."')
                #     os.system('say "ShopRite Slot Available."')
                #     time.sleep(1)
                select_available_slot(driver, slots_available)
                return None
            else:
                print('No slots available. Sleeping ...')
                time.sleep(refresh_interval_sec)
                driver.refresh()

        terminate(driver)
        return None
    except Exception as e:
        terminate(driver)
        raise ValueError(str(e))

def select_available_slot(driver, slots_available):
    print('Slots Available!')
    for avail in slots_available:
        #filtering here
        print(avail.text)

    avail = slots_available[0]
    try:
        driver.execute_script("window.scrollTo({}, {})".format(avail.rect['x'], avail.rect['y'])) 
        avail.click()
        time.sleep(2.3)
        driver.get('https://shop.shoprite.com/store/1420746/checkout')
        driver.find_element_by_id('includingPlasticBag_No').click()
    except Exception as e:
        print("failed here")
        terminate(driver)
        raise ValueError(str(e))

if __name__ == "__main__":
    available_slots = []
    while not check_slots():
        print("Retrying in {} seconds".format(repeat_interval_sec))
        time.sleep(repeat_interval_sec)
