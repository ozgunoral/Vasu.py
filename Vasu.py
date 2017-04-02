# -*- coding: utf-8 -*-
"""
Created on Sun Apr 02 2017

@author: Ozgun Oral

Vasu is an automated HR helper to take over birthday emails when needed.
Vasu can detect the day's birthdays and send emails with a birthday message
and a cake.

Flow:
- read birthdays.csv and check birthdays against today
- if no birthday, report and exit
- if birthday:
    - report name(s), prompt for sending emails
        - if user does not want to send emails, exit
        - if user wants to send emails
            - generate named cakes
            - read messages.csv 
            - For each birthday:
                - generate an email with named cake and a random message
                - send message to address
            - Remove cakes
            - Report emails sent
"""
import os
import csv
from datetime import datetime, date
from random import randint
from PIL import Image, ImageDraw, ImageFont
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def CheckBirthdays():
    global birthdaysData
    
    # Read birthdays
    birthdaysFile = open('./birthdays.csv')
    birthdaysReader = csv.reader(birthdaysFile)
    birthdaysData = list(birthdaysReader)
    
    # Check if any birthdays today
    today = date.today()
    todaysBirthdays = [] # Initiate birthdays list
    
    # Check each birthday and append to birthdays list
    for i in range (1, len(birthdaysData)):
        birthdate = datetime.strptime(birthdaysData[i][1], '%d-%b').date()
        if birthdate.month == today.month and birthdate.day == today.day:
            todaysBirthdays.append(i)
    return todaysBirthdays

def ReportBirthdays(BirthdaysList):
    # Report today's birthdays
    if len(BirthdaysList) == 0:
        print "No birthdays today :("
        selection = "N"
    elif len(BirthdaysList) == 1:
        print "Today's birthday is:"
        for i in BirthdaysList:
            print birthdaysData[i][0]
        selection = raw_input("Would you like to send an email(Y/N)?").upper()
    else:
        print "Today's birthdays are:"
        for i in BirthdaysList:
            print birthdaysData[i][0]
        selection = raw_input("Would you like to send emails(Y/N)?").upper()
            
    if selection in ("Y", "N"):
        return selection
    else:
        print "\nPlease enter 'Y' or 'N'\n"
        ReportBirthdays(BirthdaysList)

def BakeCakes(BirthdaysList):
    # Generate cake images
    for i in BirthdaysList:
        cake = Image.open("./cake.jpg")
        birthdayKid = birthdaysData[i][0]
        fontsize = 900/len(birthdayKid) # Calculate the font size based on name length
        dynamicFont = ImageFont.truetype("arial.ttf", fontsize)
        draw = ImageDraw.Draw(cake)
        draw.text((270, 410), birthdayKid, fill='white', font=dynamicFont)
        cake.save("./cake"+str(i)+".jpg")

def SendEmails(BirthdaysList):
    # Read birthday messages
    messagesFile = open('./messages.csv')
    messagesReader = csv.reader(messagesFile)
    messageData = list(messagesReader)
    
    # Read sender email creds from the text file
    emailCreds = open('./sender_creds.txt', 'r')
    username, password = emailCreds.read().split('|')
    
    for i in BirthdaysList:
        birthdayKid = birthdaysData[i][0]
        birthdayAddress = birthdaysData[i][2]
        randomMessage = messageData[randint(1,len(messageData)-1)][0]
        
        # Prepare the email
        subject = 'Happy Birthday '+birthdayKid
        body = 'Hi %s,\n\n%s\n\n' % (birthdayKid, randomMessage)
        body = body.replace('\n' , '<br />') # Line break to html modification
        attachment = "./cake"+str(i)+".jpg"
        from_address = username
        to_address = birthdayAddress
        
        msg = MIMEMultipart()
        msg["From"] = from_address
        msg["To"] = to_address
        msg["Subject"] = subject
        
        msgText = MIMEText('<b>%s</b><br><img src="cid:%s"><br>' % (body, "Chocolate_cake"), 'html')
        msg.attach(msgText)
        
        fp = open(attachment, 'rb')                                                    
        img = MIMEImage(fp.read())
        fp.close()
        msg.add_header('Content-ID', '<Chocolate_cake>')
        msg.attach(img)
        
        # Make the connection and send emails
        smtpObj = smtplib.SMTP('smtp.office365.com', 587)
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.login(username, password)
        smtpObj.sendmail(from_address, to_address, msg.as_string())
        smtpObj.quit()
        
def ReportEmails(BirthdaysList):
    # Delete cakes
    for i in BirthdaysList:
        os.remove("./cake"+str(i)+".jpg")
    
    # Report emails being sent
    if len(BirthdaysList) == 1:
        print '1 email sent. Thanks for using Vasu.py'
    else:
        print '%d emails sent. Thanks for using Vasu.py!' % (len(BirthdaysList))

def Main():
    
    todaysBirthdays = CheckBirthdays() # Reads birthdays.csv and generates birthdays list
    
    userSelects = ReportBirthdays(todaysBirthdays) # Reports day's birthdays
    
    if userSelects == "Y":
        BakeCakes(todaysBirthdays) # Generates cake images
        SendEmails(todaysBirthdays) # Generates and sends emails
        ReportEmails(todaysBirthdays) # Reports emails sent and cleans up
    elif userSelects == "N":
        print 'No emails sent. Thanks for using Vasu.py!'
        
Main()