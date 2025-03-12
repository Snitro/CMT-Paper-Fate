import configparser
import time
from cmt import CMT  # Ensure the CMT module is correctly implemented
from mail import Mail  # Ensure the Mail module is correctly implemented

# Read the configuration file
config = configparser.ConfigParser()
config.read("config.ini")  # Your configuration file name

# Parse EMAIL section
smtp_server = config.get("EMAIL", "SMTP_SERVER")
smtp_port = config.getint("EMAIL", "SMTP_PORT")
sender_email = config.get("EMAIL", "SENDER_EMAIL")
sender_password = config.get("EMAIL", "SENDER_PASSWORD")
receiver_email = config.get("EMAIL", "RECEIVER_EMAIL")

# Parse CMT section
cmt_username = config.get("CMT", "USERNAME")
cmt_password = config.get("CMT", "PASSWORD")
cmt_conference = config.get("CMT", "CONFERENCE")
paper_ids = [paper.strip() for paper in config.get("CMT", "PAPER_ID").split(",")]  # Convert to list

# Parse SETTINGS section
polling_interval = config.getint("SETTINGS", "POLLING_INTERVAL")
send_on_startup = config.getboolean("SETTINGS", "SEND_ON_STARTUP")

# Status dictionary
STATUS_DICT = {
    1: "Pending Decision",
    2: "🎉 Accepted!",
    3: "Rejected"
}

# Track the last known status for each paper
last_status_ids = {}

# Initialize CMT and Mail objects
cmt = CMT(cmt_username, cmt_password, cmt_conference)
mailer = Mail(
    sender_email=sender_email,
    sender_password=sender_password,
    receiver_email=receiver_email,
    smtp_server=smtp_server
)

# Function to check paper acceptance status and send email notifications
def poll_task():
    global last_status_ids

    print("Checking paper acceptance status...")

    for paper_id in paper_ids:
        # Get paper status
        status_id, status_text = cmt.get_acception_status(paper_id)

        print(f"Paper {paper_id} - Status ID: {status_id}, Status: {status_text}")

        # If first check, decide whether to send email based on SEND_ON_STARTUP
        if paper_id not in last_status_ids:
            last_status_ids[paper_id] = status_id
            if not send_on_startup:
                print(f"Initial status retrieved for Paper {paper_id}. Email notification disabled on startup.")
                continue
            else:
                last_status_ids[paper_id] = -1

        # If the status has changed, send an email notification
        if status_id != last_status_ids[paper_id]:
            last_status_ids[paper_id] = status_id  # Update last known status

            if status_id == 2:  # Accepted
                subject = "🎉 Paper Acceptance Notification!"
                body = f"Congratulations! Your paper (ID: {paper_id}) has been accepted to {cmt_conference}."
            elif status_id == 3:  # Rejected
                subject = "ℹ️ Paper Status Update"
                body = f"Your paper (ID: {paper_id}) has been rejected for {cmt_conference}."
            else:
                subject = "ℹ️ Paper Status Update"
                body = f"Your paper (ID: {paper_id}) status has been updated: {STATUS_DICT.get(status_id, 'Unknown Status')}. Please check the conference system for details."

            # Send email notification
            print(f"Sending email notification for Paper {paper_id}: {subject}")
            mailer.send_email(subject, body)
        else:
            print(f"No status change detected for Paper {paper_id}. No email sent.\n")

# Infinite loop to periodically check status
while True:
    poll_task()
    print(f"Sleeping for {polling_interval} seconds...\n")
    time.sleep(polling_interval)
