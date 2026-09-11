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

## Playground

The script can also download from [Playground](https://app.tryplayground.com) instead of Procare. Set these in `.env`:

```
PROVIDER=playground        # or "procare" (the default)
PLAYGROUND_EMAIL=...
PLAYGROUND_PASSWORD=...
PLAYGROUND_FIREBASE_API_KEY=...
```

`PLAYGROUND_FIREBASE_API_KEY` is Playground's public Firebase web API key, which isn't secret but is kept out of this repo: open https://app.tryplayground.com, and in its JavaScript find `productionConfig={apiKey:...}` (the key starts with `AIza`).

Playground doesn't need a browser: the script signs in through the same Firebase Auth and JSON API as the Playground web app, then uploads the photos and videos posted to your child's feed on the target day (or month, with `PROCARE_MODE=monthly`) to the same NextCloud folder as Procare. The `PROCARE_YEAR`/`PROCARE_MONTH`/`PROCARE_DAY`/`PROCARE_MODE` settings apply to both providers, and `TZ` sets the time zone that decides which day a post belongs to (default `America/New_York`).

Files are named `<posting time>_<Playground file name>`, and anything already in the NextCloud folder is skipped, so re-running a day only downloads what's new. Run `python main.py --dry-run` to see what would be uploaded without downloading anything.

## Important Notes

-   **Browser Automation:** This script uses Selenium to control a Chrome browser. Ensure you have Google Chrome installed on your system.
-   **XPath Selectors:** The script relies on specific XPath selectors to find elements on the Procare Connect website. If the website's structure changes, these selectors may need to be updated.
-   **Security:** Your email and password are input directly into the terminal and are not stored by the script. However, be mindful when running scripts that require sensitive information.
-   **Error Handling:** Basic error handling is included, but complex scenarios (e.g., network issues, unexpected pop-ups) might require further improvements.
-   **Respect Website Terms of Service:** Always ensure that any automated downloading complies with the terms of service of the website you are interacting with.
