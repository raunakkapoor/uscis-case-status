import smtplib
import time
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

# Set the with USCIS receipt number(s)
receipt_nums = ['IOEXXXXXXXXXX', 
        'EACXXXXXXXXXX', 
        'EACXXXXXXXXXX']

# Set the email details
sender_email = 'sender@corp.com'
receiver_email = 'receiver@corp.com'

# Set the SMTP server details
smtp_server = 'smtp.corp.com'
port = 25


#Query USCIS API every 2 hours and send an email with CASE status 
while True:
    # Make the request to the USCIS API endpoint
    uscis_api_url = "https://egov.uscis.gov/csol-api/case-statuses/"
    results = []
    for receipt_num in receipt_nums:
        response = requests.get(uscis_api_url+receipt_num, verify=False, timeout=300)
        result = response.json()
        result['CaseStatusResponse'].pop('detailsEs', None) #remove the spanish content 
        results.append(result)
       
    # Create the email message
    subjects = []
    for result in results:
        subjects.append(result['CaseStatusResponse']['receiptNumber'] + " - " + result['CaseStatusResponse']['detailsEng']['actionCodeText'])
        
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = "-".join(subjects)
    body = MIMEText(json.dumps(results, indent=4, sort_keys=True))
    message.attach(body)

    # Send the email via the SMTP server
    server = smtplib.SMTP(smtp_server, port)
    server.starttls()
    server.sendmail(sender_email, receiver_email, message.as_string())
    server.quit()

    # Wait for 2 hours before making the next request
    time.sleep(2 * 60 * 60)

