# CMT Paper Fate 🚀📄

**CMT Paper Fate** is a simple tool designed to check the acceptance status of submissions on the **CMT (Conference Management Toolkit)** platform. With just a few commands, you can effortlessly track your paper's fate and receive notifications.

📌 **GitHub Repository:** [CMT Paper Fate](https://github.com/Snitro/CMT-Paper-Fate.git)

## Features ✨
- 🔑 **Supports username-password login to CMT** for authentication.
- ✅ **Automatically checks** the acceptance status of your paper on CMT.
- 📧 **Sends email notifications** when your paper's status changes.

## Installation 📥

### Prerequisites
- 🐍 **Python 3.8+** installed
- 📧 **An SMTP email account for notifications (mandatory)**

### Clone the Repository
```sh
git clone https://github.com/Snitro/CMT-Paper-Fate.git
cd CMT-Paper-Fate
```

## Configuration ⚙️

Create a configuration file `config.ini` in the root directory and set the required parameters:

```ini
[EMAIL]
SMTP_SERVER = your_smtp_server
SMTP_PORT = your_smtp_port
SENDER_EMAIL = your_email@example.com
SENDER_PASSWORD = your_email_password
RECEIVER_EMAIL = receiver_email@example.com

[CMT]
USERNAME = your_cmt_username
PASSWORD = your_cmt_password
CONFERENCE = your_conference_name
PAPER_ID = your_paper_id

[SETTINGS]
POLLING_INTERVAL = 600
SEND_ON_STARTUP = True
MAX_RETRIES = 3
RETRY_INTERVAL = 30
SEND_ERROR_EMAIL = True
```

### Important Notes 🚨
- 🔐 **USERNAME and PASSWORD must be stored securely**. Avoid sharing them or committing them to version control.
- 🔗 **CONFERENCE must be obtained from the CMT3 website**. See the next section for details.

## How to Obtain `CONFERENCE` Value from CMT3 🔍

To get the correct **CONFERENCE** value:
1. Log in to [CMT3](https://cmt3.research.microsoft.com/).
2. Navigate to your conference.
3. Look at the **URL in the browser's address bar**.  
   - Example: If the URL is  
     ```
     https://cmt3.research.microsoft.com/MyConference2025/Submission/Index
     ```
     then your **CONFERENCE value is `MyConference2025`**.

## Usage 🚀

Run the script to start tracking your paper:
```sh
python accept.py
```

## How It Works 🛠️
1. The script logs into the **CMT** platform using your **username and password**.
2. It periodically checks the acceptance status of the specified **paper ID**.
3. If there is any update, it **sends an email notification**.

## Troubleshooting 🐞

- **SMTP Authentication Error**: Ensure that you are using the correct SMTP settings and that your email provider allows SMTP access.
- **CMT Login Issues**: Double-check your username and password. Consider using an application-specific password if necessary.

## Contributing 🤝
Contributions are welcome! Feel free to submit an issue or a pull request.

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Commit your changes (`git commit -m "Add new feature"`)
4. Push to the branch (`git push origin feature-branch`)
5. Open a pull request

## License 📜
This project is licensed under the [MIT License](LICENSE).

## Contact 📩
For any questions or feedback, feel free to reach out or open an issue.
