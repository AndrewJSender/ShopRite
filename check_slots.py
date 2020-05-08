import sys, os, re, time, datetime, getpass
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if sys.platform == 'win32':
    import winsound
    chromedriver = ROOT_DIR + "/chromedriver.exe"
else:
    chromedriver = ROOT_DIR + "/chromedriver"

repeat_interval_sec  = 30
refresh_interval_sec = 10
max_attempts         = 12
g_infinite_alert     = True
shoprite_creds = {}
with open ("config.txt", "r") as myfile:
    for line in myfile.readlines():
        if line.startswith('#'):
            continue
        else:
            try:
                [key, value] = line.strip("\n").split(':')
                shoprite_creds[key] = value
            except:
                pass

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
        driver.get('https://shop.shoprite.com/store/{}'.format(shoprite_creds['store_id']))
        time.sleep(2.0)
        email_field = driver.find_element_by_name('Email')
        email_field.send_keys(shoprite_creds['email'])
        password_field = driver.find_element_by_name('Password')
        password_field.send_keys(shoprite_creds['password'])
        driver.find_element_by_id('SignIn').click()
        time.sleep(1.5)

        print('Checkout Step One ...')
        cart = driver.find_element_by_class_name('accountMenu__cart')
        cart.click()
        time.sleep(1.5)
        print('Checkout Step Two ... Reserve Slot')
        driver.get('https://shop.shoprite.com/store/{}/cart'.format(shoprite_creds['store_id']))
        time.sleep(1.5)
        driver.get('https://shop.shoprite.com/store/{}/reserve-timeslot'.format(shoprite_creds['store_id']))
        time.sleep(2.5)

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
                if slot.text != 'Sold Out' and slot.text != '':
                    slots_available.append(slot)
            if slots_available:
                alert_sound("ShopRite Slot Available.", infinite=g_infinite_alert)
                select_available_slot(driver, slots_available)
                return None
            else:
                print('No slots available. Refreshing and Retrying {} seconds'.format(refresh_interval_sec))
                driver.refresh()
                time.sleep(refresh_interval_sec)

        terminate(driver)
        return None
    except Exception as e:
        terminate(driver)
        print("Script Failed.  Ctrl + C to terminate script")
        alert_sound("Failed", g_infinite_alert)
        raise ValueError(str(e))

def alert_sound(statement = "Beep", infinite = False):
    if infinite:
        while infinite:
            if sys.platform == 'win32':
                winsound.MessageBeep()
            else:
                os.system('say "{}"'.format(statement))
            time.sleep(1)
    else:
        for i in range(1,4):
            if sys.platform == 'win32':
                winsound.MessageBeep()
            else:
                os.system('say "{}"'.format(statement))
            time.sleep(1)

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
        driver.get('https://shop.shoprite.com/store/{}}/checkout'.format(shoprite_creds['store_id']))
        driver.find_element_by_id('includingPlasticBag_No').click()
        checkout_buttons = driver.find_element_by_css_selector('button.checkoutStep__continueButton')
        for checkout_button in checkout_buttons:
            if checkout_button.text == 'Continue To Payment':
                checkout_button.click()
                break
        driver.find_element_by_id('SelectedPaymentMethodId').click()

        checkout_buttons = driver.find_element_by_css_selector('button.checkoutStep__continueButton')
        for checkout_button in checkout_buttons:
            if checkout_button.text == 'Place Order':
                checkout_button.click()
                break
        
        driver.find_element_by_id('ccNumber').send_keys(shoprite_creds['credit_card_number'])
        driver.find_element_by_id('CreditExpiryMonth').send_keys(shoprite_creds['credit_card_exp_month'])
        driver.find_element_by_id('creditExpiryYear').send_keys(shoprite_creds['credit_card_exp_year'])
        driver.find_element_by_id('ccvv').send_keys(shoprite_creds['credit_card_security_code'])

        driver.find_element_by_id('order_Continue_Btn').click()
    except Exception as e:
        print("failed here")
        terminate(driver)
        raise ValueError(str(e))

if __name__ == "__main__":
    print("Sound Test ...")
    alert_sound("Beep", False)
    while not check_slots():
        print("Retrying in {} seconds".format(repeat_interval_sec))
        time.sleep(repeat_interval_sec)
