# Automated Indeed Messaging

This program allows the user to automate email indeed messages as well as messages from the applied jobs page

## Setup  

To run the code, you must install the requirement. You must have pip downloaded on your pc

```bash
pip install -r requirements.txt
```

Enter the required information in the `config.py` file

__NOTE: YOU MUST ALLOW LESS SECURE APPS TO LOGIN ON GOOGLE. WILL NOT WORK WITHOUT

```
config.py
_____________________
main_page = ''	Dont change this

username = '' Enter your Indeed username here	(REQUIRED)
password = '' Enter your Indeed password here	(REQUIRED)

days_past = #	This number determines how far back to look at emails.
TARGET_EMAIL_SUBJECT = ''	This determines what emails to look at based off of the subject line

FROM_EMAIL = '' 	Enter your Google Email here			(REQUIRED)
FROM_PWD = ''		Enter your Google Email Password Here	(REQUIRED)
SMTP_PORT = 993		Dont Change This
SMTP_SERVER = ''	Only change this if you are NOT using google as an email service

sentences...		Modify these to let the code generate a unique message for companies	(REQUIRED)
```
__NOTE: AFTER EDITING CONFIG.PY, DO NOT COMMIT THE FILE__

__NOTE: This program does not upload or store your username/password anywhere else. I will never get any passwords from this program.__

# Main.py

## Execute

To execute the bot, run the following in your terminal
```
python3 main.py

OR

main.py
```

### Parameters  

```
-h			Parameter Help
-slow		Increases delay time to be friendly to slower internet connections
-d 			Deletes emails after successfully sending a message. Only deletes the emails we are looking for.
```

## Usage

This program will log into Indeed and pause. While paused, it searches the given email account for 
specific emails with the subject line that was designated. When it finds one, it extracts the link
to the conversation and sends a unique message to the company. 

## SendMessageFromPage.py

## Execute

To execute the bot, run the following in your terminal
```
python3 sendmessagefrompage.py

OR

sendmessagefrompage.py
```

### Parameters  

```
-h			Parameter Help
-slow		Increases delay time to be friendly to slower internet connections
-d 			Deletes emails after successfully sending a message. Only deletes the emails we are looking for.
```

## Usage

This program will log into Indeed, navigate to the My Jobs page and search for "Message This Employer". 
This tells the bot that there is a link here and that is what we are looking for. It then
Visits the link and sends a unique message to the company. 

## Contact Information
Joseph D Cantrell
JosephCantrell@josephdcantrell.com
 
