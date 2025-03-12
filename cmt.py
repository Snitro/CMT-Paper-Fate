import requests
import json
import os

class CMT:
    """
    A class to handle login, session management, and acception status checking for CMT3.
    """

    COOKIE_FILE = "cookies.json"  # File to store session cookies
    STATUS_DICT = {
        1: "Pending Decision",
        2: "🎉 Accepted!",
        3: "Rejected"
    }

    def __init__(self, email: str, password: str, conference: str):
        """
        Initialize the CMT class with login credentials and a conference name.

        :param email: User's email address
        :param password: User's password
        :param conference: Conference name (e.g., "CVPR2025")
        """
        self.session = requests.Session()
        self.base_url = "https://cmt3.research.microsoft.com"
        self.email = email
        self.password = password
        self.conference = conference  # Store the conference name

        # Default headers
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0"
        }

        # Try to load session from cache
        if not self.load_cookies():
            self.login()  # If no valid session, perform login

    def login(self) -> bool:
        """
        Perform the login operation to CMT3 and cache session cookies.

        :return: True if login is successful, False otherwise
        """
        login_url = f"{self.base_url}/api/odata/Users/Login?ReturnUrl=%2F"
        login_data = {
            "Request": {
                "Email": self.email,
                "Password": self.password
            }
        }

        try:
            response = self.session.post(login_url, json=login_data, headers=self.headers)

            if response.status_code == 200:
                print("Login successful!")
                self.save_cookies()
                return True
            else:
                print("Login failed! Status code:", response.status_code)
                print("Response:", response.text)
                return False

        except requests.RequestException as e:
            print("An error occurred during login:", e)
            return False

    def save_cookies(self):
        """
        Save session cookies to a local file.
        """
        with open(self.COOKIE_FILE, "w") as file:
            json.dump(self.session.cookies.get_dict(), file)
        print("Session cookies saved.")

    def load_cookies(self) -> bool:
        """
        Load session cookies from the local file if available.

        :return: True if cookies were successfully loaded, False otherwise.
        """
        if os.path.exists(self.COOKIE_FILE):
            with open(self.COOKIE_FILE, "r") as file:
                cookies = json.load(file)
                self.session.cookies.update(cookies)
            print("Loaded cached session cookies.")
            return True
        return False

    def get_acception_status(self, paper_id: int, retry: bool = True):
        """
        Fetch acception status for a given paper ID.
        If response status is 403 (forbidden), retry login once.

        :param paper_id: The submission ID (e.g., 1352)
        :param retry: Whether to retry the request after re-authentication if 403 occurs.
        :return: Tuple (status_id, status_text)
        """
        acception_status_url = f"{self.base_url}/api/odata/{self.conference}/Submissions/{paper_id}"

        try:
            response = self.session.get(acception_status_url, headers=self.headers)

            # If the session is invalid, re-login and retry once
            if response.status_code == 403 and retry:
                print("Session expired or unauthorized. Re-authenticating...")
                if self.login():
                    return self.get_acception_status(paper_id, retry=False)
                else:
                    print("Re-authentication failed.")
                    return None, "Authentication Failed"

            if response.status_code == 200:
                print(f"Successfully retrieved acception status for paper {paper_id}.")
                data = response.json()
                
                # Extract status ID and map it using STATUS_DICT
                status_id = data.get("StatusId", -1)
                status_text = self.STATUS_DICT.get(status_id, "Unknown Status")  # Default to "Unknown Status"
                
                return status_id, status_text
            else:
                print(f"Failed to retrieve acception status for paper {paper_id}. Status code:", response.status_code)
                print("Response:", response.text)
                return None, "Error fetching status"

        except requests.RequestException as e:
            print(f"An error occurred while fetching acception status for paper {paper_id}:", e)
            return None, "Request Error"
