import time
import traceback
import configparser
from cmt import CMT
from mail import Mail

# Read configuration
config = configparser.ConfigParser()
config.read("config.ini")

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
max_retries = config.getint("SETTINGS", "MAX_RETRIES", fallback=3)
retry_interval = config.getint("SETTINGS", "RETRY_INTERVAL", fallback=5)
send_on_startup = config.getboolean("SETTINGS", "SEND_ON_STARTUP")
send_error_email = config.getboolean("SETTINGS", "SEND_ERROR_EMAIL", fallback=True)

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

def poll_task():
    global last_status_ids
    print("Checking paper acceptance status...")
    
    for paper_id in paper_ids:
        error_messages = []
        for attempt in range(max_retries):
            try:
                status_id, status_text = cmt.get_acception_status(paper_id)
                if status_id is not None:
                    print(f"Paper {paper_id} - Status ID: {status_id}, Status: {status_text}")
                    break  # Exit retry loop if successful
            except Exception as e:
                error_traceback = traceback.format_exc()
                error_messages.append(f"Attempt {attempt + 1}:\n{error_traceback}")
                print(f"Error occurred (attempt {attempt + 1}):\n{error_traceback}")
                time.sleep(retry_interval)
        else:
            print(f"Paper {paper_id} - Failed to retrieve status after {max_retries} attempts.")
            if send_error_email:
                subject = "⚠️ Persistent Error in Polling Task ⚠️"
                body = "Multiple errors occurred in the polling task:\n\n" + "\n\n".join(error_messages)
                mailer.send_email(subject, body)
            continue
        
        if paper_id not in last_status_ids:
            last_status_ids[paper_id] = status_id
            if not send_on_startup:
                print(f"Initial status retrieved for Paper {paper_id}. Email notification disabled on startup.")
                continue
            else:
                last_status_ids[paper_id] = -1

        if status_id != last_status_ids[paper_id]:
            last_status_ids[paper_id] = status_id  # Update last known status
            subject, body = "", ""
            if status_id == 2:
                subject = "🎉 Paper Acceptance Notification!"
                body = f"Congratulations! Your paper (ID: {paper_id}) has been accepted to {cmt_conference}."
            elif status_id == 3:
                subject = "ℹ️ Paper Status Update"
                body = f"Your paper (ID: {paper_id}) has been rejected for {cmt_conference}."
            else:
                subject = "ℹ️ Paper Status Update"
                body = f"Your paper (ID: {paper_id}) status has been updated: {STATUS_DICT.get(status_id, 'Unknown Status')}. Please check the conference system for details."
            
            print(f"Sending email notification for Paper {paper_id}: {subject}")
            mailer.send_email(subject, body)
        else:
            print(f"No status change detected for Paper {paper_id}. No email sent.\n")

# Infinite loop to periodically check status
while True:
    try:
        poll_task()
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"Error occurred:\n{error_traceback}")
        if send_error_email:
            subject = "⚠️ Error Alert in Polling Task ⚠️"
            body = f"An error occurred in the polling task:\n\n{error_traceback}"
            mailer.send_email(subject, body)
    
    print(f"Sleeping for {polling_interval} seconds...\n")
    time.sleep(polling_interval)
