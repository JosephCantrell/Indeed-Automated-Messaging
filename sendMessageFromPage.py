import smtplib
import time
import imaplib
import email
import traceback 
import argparse
import winsound
import random
import datetime
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta, date

from config import *


class SendMessageFromWebpage:

    def __init__(self, args):
    
        self.sleepMulti = 1.5

        self.appliedToLinks = []
        
        self.haveLoggedIn = False
        
        self.mail = None

        self.args = args
        if self.args.slowInternet:
            self.sleepMulti = 3
        self.options = self.browser_options()
        self.browser = webdriver.Chrome(executable_path = 'C:\\Users\josep\.wdm\drivers\chromedriver\win32\88.0.4324.96\chromedriver.exe', options=self.options, )

        self.wait = WebDriverWait(self.browser, 30)
        self.browser.maximize_window()

# Init function to make the browser less detectable      
    def browser_options(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-extensions")
        options.add_experimental_option("excludeSwitches",["enable-automation"])
        options.add_experimental_option('useAutomationExtension',False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        return options

# Generates a random message based off of a few string arrays in the config file
    def createMessage(self):
        temp = self.browser.find_elements_by_xpath('//*[@id="messaging-main-content"]/div/div[2]/div/div[1]/div[2]/div/div[2]')
        companyName = ''
        if temp:
            companyName = temp[0].text
        else:
            companyName = ''
        temp = random.randint(0, len(IntroSentences)-1)
        message = IntroSentences[temp] + companyName + ',\n'
        
        temp = random.randint(0,len(firstSentences)-1)
        message = message + ' ' + firstSentences[temp]
        
        temp = random.randint(0, len(secondSentences)-1)
        message = message + ' ' + secondSentences[temp]
        
        temp = random.randint(0, len(thirdSentences)-1)
        message = message + ' ' + thirdSentences[temp]
        
        temp = random.randint(0, len(fourthSentences)-1)
        message = message + ' ' + fourthSentences[temp]
        
        message = message + Closing
        
        return message

    
    def getJobElements(self):
        parentContainer = self.browser.find_elements_by_xpath('//*[@id="tabpannel"]/div/div[1]')
        if parentContainer:
            childElements = parentContainer[0].find_elements_by_xpath('./*')
            print(len(childElements))
            for i, child in enumerate(childElements):
                className = child.get_attribute('class')
                
                if className == 'atw-AppCard':
                    content = child.find_elements_by_class_name('atw-JobMetadata-content')
                    if content:
                        if content[0].text == 'Message this employer':
                            temp = content[0].find_elements_by_tag_name('a')
                            if temp:
                                print('Found an HREF')
                                # Do the messaging stuff
                                href = temp[0].get_attribute('href')
                                self.openTab(str(href))
                                if not self.checkIfPreviousMessage():
                                    if self.sendMessage():
                                        print('Successfully sent a new message.')
                                time.sleep(2)
        else:
            print('Could not find parent container')
            return False

    def getToJobsPage(self):
        # User Icon button
        temp = self.browser.find_elements_by_xpath('//*[@id="gnav-main-container"]/div/div[1]/div/div[3]/div[1]/div[3]/div[1]')
        if temp:    
            try:
                temp[0].click()
            except:
                print('Could not click on the user button')
                return False
        else:
            print('Could not find the user button')
            return False
        # My Jobs button
        temp = self.browser.find_elements_by_xpath('//*[@id="gnav-main-container"]/div/div[1]/div/div[3]/div[1]/div[3]/div[2]/div/div[2]/a[2]')
        if temp:
            try:
                temp[0].click()
            except:
                print('Could not click on the My Jobs button')
                return False
        else:
            print('Could not find My Jobs button')
            return False
        time.sleep(10)
        # Applied jobs button
        temp = self.browser.find_elements_by_xpath('//*[@id="POST_APPLY"]')
        if temp:
            try:
                temp[0].click()
            except:
                print('Could not click on the applied button')
                return False
        else:
            print('Could not find the Applied button')
            return False
            
        time.sleep(10)
        return True

# Does as it says, opens tabs
    def openTab(self, url):
        self.browser.execute_script("window.open('');")
        # Switch to the new window
        self.browser.switch_to.window(self.browser.window_handles[1])
        time.sleep(1 * self.sleepMulti)
        # Go to the given link
        self.browser.get(url)
        time.sleep(1 * self.sleepMulti)

# Does as it says, closes tabs
    def closeTab(self):
        # Close the tab and refocus on the main page
        self.browser.close()
        self.browser.switch_to.window(self.browser.window_handles[0])

# Main function that controls the order in which items happen        
    def run(self):
    
        self.start_up()
        # If the function returns true that means the emails are too old and skipped the close functions
        if self.getToJobsPage():
            self.getJobElements()
        else:
            print('Error occured, Stopping')

# This function finds the text field, sends a generated message, and clicks send. 
    def sendMessage(self):

        # Find the text input
        temp = self.browser.find_elements_by_xpath('//*[@id="messaging-main-content"]/div/div[2]/div/div[3]/div/div[1]/textarea')
        # If we have found the text input field
        if temp:
            temp[0].click()
            time.sleep(random.uniform(.1,.2) * self.sleepMulti)
            temp[0].send_keys(self.createMessage())
            time.sleep(random.uniform(.5,1) * self.sleepMulti)
        else:
            # Error
            print('Could not find the text field. Ensure XPath is correct')
            self.closeTab()
            return False
        # Find the send button
        temp = self.browser.find_elements_by_xpath('//*[@id="messaging-main-content"]/div/div[2]/div/div[3]/div/div[2]/div[2]/button')
        # If we have found the send button
        if temp:
            temp[0].click()
            time.sleep(random.uniform(1,1.5) * self.sleepMulti)
            self.closeTab()
            return True
        else:
            print('Could not find the Send button. Ensure XPath is correct')
            self.closeTab()
            return False


    def checkIfPreviousMessage(self):
        
            knownSID = ['__InfiniteScrollableList-boundary',
            '__InfiniteScrollableList-loader',
            'indeed-application-event',
            'indeed-initiation-event']
            
            
            
            time.sleep(10)
        
            # Assuming we are on the message page.
            temp = self.browser.find_elements_by_xpath('//*[@id="messaging-main-content"]/div/div[2]/div/div[2]/div/div')
            # We are on the message page.
            if temp:
                childElements = temp[0].find_elements_by_xpath("./*")
                for elements in childElements:
                    elementSID = elements.get_attribute('data-sid')
                    # If the found sid is not equal to any known sid,
                    if elementSID != knownSID[0] and elementSID != knownSID[1] and elementSID != knownSID[2] and elementSID != knownSID[3]:
                        # Found SID does not match any known SID, must be a unique message   
                        print('Found a unique SID: ' + elementSID)
                        return True
                print('Did not find a unique SID')
                return False

# Checks our current URL against a targetURL to ensure we are where we want to be. Only used for logging in
    def check_target_url(self, targetURL):
        if self.browser.current_url == targetURL:
            return True
        return False

# Start up function ensures that we get to the main page, click the login button and then do our login procedure. Looks more human
    def start_up(self):
            self.browser.get(main_page)
            time.sleep(random.uniform(1,3) * self.sleepMulti)
            signInButton = self.browser.find_element_by_xpath('//*[@id="gnav-main-container"]/div/div[1]/div/div[3]/div[3]/a').click()
            time.sleep(random.uniform(1,3) * self.sleepMulti)
            self.login()
       
# Standard login procedure. If there is a captcha (if we did not go to the expected webpage) then we are alerted.
    def login(self):
        print('Login')
        # Select the username element and input the stored username
        select_username = self.browser.find_element_by_xpath('//*[@id="login-email-input"]')
        select_username.send_keys(username)
        
        # Select the password element and input the stored password
        select_password = self.browser.find_element_by_xpath('//*[@id="login-password-input"]')
        select_password.send_keys(password)
        ## press ENTER key 
        select_password.send_keys(Keys.ENTER)
        
        time.sleep(1 * self.sleepMulti)

            
        expectedURL = main_page 
        
        # If we have not reached the expected URL, that means we hit a captcha and the bot needs user input
        if not self.check_target_url(expectedURL):
            print('captcha at login')
            winsound.Beep(2000,2000)
            time.sleep(30 * self.sleepMulti)
            
            select_password = self.browser.find_elements_by_xpath('//*[@id="login-password-input"]')
            if select_password:
                select_password[0].send_keys(password)
                select_password[0].send_keys(Keys.ENTER)
        
        
        print('Finished login')

parser = argparse.ArgumentParser(description='Indeed Automatic Webpage Responses')
parser.add_argument('-slow','--slowInternet', help='Enable this if you need more time for each page to load', required=False ,action='store_true' ,default=False)

args = parser.parse_args()

bot = SendMessageFromWebpage(args)

bot.run()
