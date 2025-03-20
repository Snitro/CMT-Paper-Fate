import re
import json
import time
import traceback
import configparser
from cmt import CMT
from mail import Mail

# Read configuration
config = configparser.ConfigParser()
config.read("config.ini")

# Load status dictionary from JSON file
STATUS_CONFIG_FILE = "status_config.json"

def load_status_dict():
    """
    Loads the status dictionary from a JSON configuration file.

    :return: A dictionary where keys are regex patterns and values are status texts.
    """
    try:
        with open(STATUS_CONFIG_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data
    except Exception as e:
        print(f"Error loading status configuration: {e}")
        return {".*": "Pending Decision"}  # Default fallback

STATUS_DICT = load_status_dict()

# Retrieve the first and second values from STATUS_DICT
STATUS_VALUES = list(STATUS_DICT.values())
FIRST_STATUS_VALUE = STATUS_VALUES[0] if len(STATUS_VALUES) > 0 else "🎉 Accepted!"
SECOND_STATUS_VALUE = STATUS_VALUES[1] if len(STATUS_VALUES) > 1 else "Rejected"

def get_status_text(status_id: int) -> str:
    """
    Determines the status text based on the given status ID using regex matching.

    :param status_id: The numerical status ID returned by CMT.
    :return: The corresponding status description.
    """
    status_str = str(status_id)
    for pattern, text in STATUS_DICT.items():
        if re.fullmatch(pattern, status_str):
            return text
    return STATUS_DICT.get(".*", "Pending Decision")  # Default if no match

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
    """
    Periodically checks the paper acceptance status and sends email notifications
    when there is a status change.
    """
    global last_status_ids
    print("Checking paper acceptance status...")

    for paper_id in paper_ids:
        error_messages = []
        for attempt in range(max_retries):
            try:
                status_id = cmt.get_acception_status(paper_id)  # Retrieve status_id
                status_text = get_status_text(status_id)  # Fetch status text using regex mapping
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
                last_status_ids[paper_id] = -1  # Ensure notification is triggered on the first check

        if status_id != last_status_ids[paper_id]:
            last_status_ids[paper_id] = status_id  # Update last known status
            subject, body = "", ""
            
            # Check if status matches the first value (Accepted)
            if status_text == FIRST_STATUS_VALUE:
                subject = "🎉 Paper Acceptance Notification!"
                body = f"Congratulations! Your paper (ID: {paper_id}) has been accepted to {cmt_conference}."

            # Check if status matches the second value (Rejected)
            elif status_text == SECOND_STATUS_VALUE:
                subject = "ℹ️ Paper Rejection Notification"
                body = f"Your paper (ID: {paper_id}) has been rejected for {cmt_conference}."

            # Handle all other status updates
            else:
                subject = "ℹ️ Paper Status Update"
                body = f"Your paper (ID: {paper_id}) status has been updated: {status_text}. Please check the conference system for details."

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
