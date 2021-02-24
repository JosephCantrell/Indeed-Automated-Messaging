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

# Open Browser                                  Done
# Go to Indeed and Click Login                  Done
# Login                                         Done
# Get Gmail Link                                Done
# Visit Link if not visited before              Done
# Create Message                                Done
# Send Message                                  Done
# Store visited link in a list                  Done
# Allow for emails to be deleted once visited   Done
# Repeat                                        Done

class Messager:

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

# Determines if the email date is within the time range that we want
    def parseEmailDate(self, emailDate):
    
        try:
            # Remove the last 21 characters
            tempDate = emailDate[:-21]
        
            # Convert the stripped date into a datetime object
            email_date =  datetime.strptime(tempDate, "%a, %d %b %Y")
            # Get todays date
            today = date.today()
            # Convert todays date into a datettime object
            today = datetime(today.year, today.month, today.day)
            
            # Add our search time  to the email date
            end_date = email_date + timedelta(days=days_past)
            
            # Compare our adjusted email date to todays date.
            if end_date < today:
                return False
            else:
                return True
        except:
            # This can occur with incorrect dates from the email like "Fe" for Feb
            print('Date error in email. Skipping')
            return True

# Bulk of the work is done here
    def read_email_from_gmail(self):
        try:
            # Set up a mail server
            self.mail = imaplib.IMAP4_SSL(SMTP_SERVER)
            self.mail.login(FROM_EMAIL,FROM_PWD)
            # Select the inbox section
            self.mail.select('inbox')

            # Grab all emails.
            data = self.mail.search(None, 'ALL')
            mail_ids = data[1]
            id_list = mail_ids[0].split()   
            first_email_id = int(id_list[0])
            latest_email_id = int(id_list[-1])

            for i in range(latest_email_id,first_email_id, -1):
                # Fetch the email information
                data = self.mail.fetch(str(i), '(RFC822)' )
                # For each of the responses in the email
                for response_part in data:
                    arr = response_part[0]
                    if isinstance(arr, tuple):
                        # Get the email message information
                        msg = email.message_from_string(str(arr[1],'utf-8'))
                        email_date = msg['date']
                        # If the email is not older than our given time span
                        if self.parseEmailDate(email_date):
                            email_subject = msg['subject']
                            # If the subject has the text that we are looking for. in Config.py
                            if TARGET_EMAIL_SUBJECT in email_subject.lower():
                                print('Found an email')
                                # We need to check over every payload to find the correct link
                                for payload in msg.get_payload():
                                    payloadStr = str(payload.get_payload(decode=True))
                                    # If this payload has the link that we are looking for
                                    if "https://messages.indeed.com/conversations/new?token" in payloadStr:
                                        # String manipulation to find the entire link that we are looking for. Find the position of the first char of the link
                                        start = payloadStr.find('https://messages.indeed.com/conversations/new?token')
                                        # Create a new string starting at the beginning of our link
                                        newStr = payloadStr[start:len(payloadStr)]
                                        # Find the first text that says "" and record the position plus our start position
                                        end = newStr.find("' style") + start
                                        # Create the link
                                        link = payloadStr[start:end]
                                        # These random characters appear in the HTML response. Remove them
                                        link = link.replace('3D','')
                                        link = link.replace('amp;','')
                                        link = link.replace("\\","")
                                        # If we have not recorded this link before
                                        if not self.hasSentBefore(link):
                                            # If we successfully sent the message
                                            if self.sendMessage(link):
                                                # Write the link to our saved file
                                                self.writeLinkToFile(link)
                                                # If user requests to delete the email, delete it.
                                                if self.args.deleteEmail:
                                                    self.deleteMessage(str(i))
                                                    self.mail.expunge()
                                        else:
                                            # If we have sent it before, we need to check if the user wants to delete the email
                                            if self.args.deleteEmail:
                                                self.deleteMessage(str(i))
                                                self.mail.expunge()
                            else:
                                print('Not the right email subject')
                        else:
                            print('Emails too old now. Breaking')
                            return True 
            # close the mailbox
            self.mail.close()
            # logout from the account
            self.mail.logout()
            
        except Exception as e:
            traceback.print_exc() 
            print(str(e))
            
# Writes the given link to our previously messaged companies
    def writeLinkToFile(self, link):
        file = open('sentMessage.csv', 'a')
        file.writelines(link + '\n') 
        file.close()
        print('Wrote the link to the file')

# Marks a given email with a deletion tag
    def deleteMessage(self, mail):
        # Mark the given email position a tag to be deleted
        self.mail.store(mail, "+FLAGS", "\\Deleted")
        print('Deleted Email Number ' + mail)

# This function opens a new tab, finds the text field, sends a generated message, and clicks send. 
    def sendMessage(self, link):
        # Open a new tab
        self.openTab(link)
        time.sleep(random.uniform(2,3) * self.sleepMulti)
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
            time.sleep(random.uniform(.5,1) * self.sleepMulti)
            self.closeTab()
            return True
        else:
            print('Could not find the Send button. Ensure XPath is correct')
            self.closeTab()
            return False

# Checks our current URL against a targetURL to ensure we are where we want to be. Only used for logging in
    def check_target_url(self, targetURL):
        if self.browser.current_url == targetURL:
            return True
        return False

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

# Writes the link given into our previously messaged to list of links
    def writeToFile(self, link):
        file = open('sentMessage.csv', 'a')
        file.writelines(link + '\n')
        file.close() 

# Does as it says, closes tabs
    def closeTab(self):
        # Close the tab and refocus on the main page
        self.browser.close()
        self.browser.switch_to.window(self.browser.window_handles[0])

# Does as it says, opens tabs
    def openTab(self, url):
        self.browser.execute_script("window.open('');")
        # Switch to the new window
        self.browser.switch_to.window(self.browser.window_handles[1])
        time.sleep(1 * self.sleepMulti)
        # Go to the given link
        self.browser.get(url)
        time.sleep(1 * self.sleepMulti)

# Main function that controls the order in which items happen        
    def run(self):
    
        # first thing is to load all of our previously messaged to links into an array for future use.
        with open('sentMessage.csv', 'r') as csvfile:
            for line in csvfile:
                tempLine = line.replace('\n',"")
                tempLine = tempLine.replace('\\','')
                self.appliedToLinks.append(tempLine)

        self.start_up()
        # If the function returns true that means the emails are too old and skipped the close functions
        if self.read_email_from_gmail():
            # close the mailbox
            self.mail.close()
            # logout from the account
            self.mail.logout()

# Checks against our list of links to ensure that we dont send a duplicate email
    def hasSentBefore(self, link):
        # Loop through the links in the stored array 'appliedToLinks'
        for appliedLinks in self.appliedToLinks:
            # If we found a match, return True
            if link == appliedLinks:
                print('Have sent a message to this link before')
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

parser = argparse.ArgumentParser(description='Indeed Automatic Email Responses')
parser.add_argument('-slow','--slowInternet', help='Enable this if you need more time for each page to load', required=False ,action='store_true' ,default=False)
parser.add_argument('-d','--deleteEmail', help='Enable this if you want to delete the emails after sending a message', required=False ,action='store_true' ,default=False)

args = parser.parse_args()

bot = Messager(args)

bot.run()


