# Procare Connect Photo Downloader

Vibe-coded using Gemini CLI.

This is a Python script that automates the download of your child's photos from the Procare Connect website.

## Features

- Logs into Procare Connect as a parent.
- Navigates to the Photos/Videos section.
- Sets the duration filter to "Monthly".
- Scrolls through the page to load all available photos.
- Initiates download for each photo by hovering and clicking the download icon.
- Saves all downloaded photos to a local directory named `procare_downloads`.

## Setup

1.  **Clone or Download:** Get this project onto your local machine.

2.  **Navigate to Project Directory:** Open your terminal or command prompt and go into the `procare_downloader` directory:

    ```bash
    cd procare-download/procare_downloader
    ```

3.  **Create a Virtual Environment (Recommended):**
    A virtual environment isolates the project's dependencies from your system's Python installation.

    ```bash
    python -m venv .venv
    ```

4.  **Activate the Virtual Environment:**

    -   **Windows:**
        ```bash
        .\.venv\Scripts\activate
        ```
    -   **macOS/Linux:**
        ```bash
        source .venv/bin/activate
        ```

5.  **Install Dependencies:**
    Install the required Python libraries using pip:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the Script:**
    Make sure your virtual environment is activated (see "Activate the Virtual Environment" above). Then, run the script:

    ```bash
    python main.py
    ```

2.  **Enter Credentials:**
    The script will prompt you to enter your Procare Connect email and password in the terminal.

3.  **Monitor Downloads:**
    A Chrome browser window will open, and the script will automate the login and download process. Photos will be saved to a newly created directory named `procare_downloads` in the same directory as the script.

## Important Notes

-   **Browser Automation:** This script uses Selenium to control a Chrome browser. Ensure you have Google Chrome installed on your system.
-   **XPath Selectors:** The script relies on specific XPath selectors to find elements on the Procare Connect website. If the website's structure changes, these selectors may need to be updated.
-   **Security:** Your email and password are input directly into the terminal and are not stored by the script. However, be mindful when running scripts that require sensitive information.
-   **Error Handling:** Basic error handling is included, but complex scenarios (e.g., network issues, unexpected pop-ups) might require further improvements.
-   **Respect Website Terms of Service:** Always ensure that any automated downloading complies with the terms of service of the website you are interacting with.
