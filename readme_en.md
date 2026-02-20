> **[Notice] This is an unofficial project created for learning purposes only. Commercial use is prohibited. The accuracy of the information provided is not guaranteed, and the developer assumes no legal responsibility.**

# 🚆 Train Status Notifier

This is an automated system that scrapes the train operation information of JR-Central, and sends a notification to Discord if there are delays or service suspensions.

## Key Features

-   **Real-time Status Check**: Scrapes the JR-Central website to check the current operational status.
-   **Delay Information Parsing**: When a delay occurs, it extracts detailed information (affected sections, time, etc.) and the location of each train.
-   **Multi-language Support**: Processes and provides the information in Korean, Japanese, and English.
-   **Discord Notifications**: Sends formatted operational information to a specified Discord channel via a webhook.
-   **Automated Execution**: Can be configured to run automatically at specific times (e.g., commute hours) using GitHub Actions or a server Cron job.
-   **Targeting Functionality**: Can filter and send notifications for relevant train information based on a specific station and direction (up/down).

## How It Works

1.  **Data Collection (Web Scraping)**:
    -   Fetches the HTML of the JR-Central train information page using `requests` and `BeautifulSoup4` (or `selenium`).
    -   (**`src/parse/rate_train_info.py`**)

2.  **Information Parsing and Analysis**:
    -   Parses the fetched HTML to check if the overall status is 'normal operation'.
    -   If a delay occurs, it extracts the full notice along with detailed information for each delayed train, such as type, destination, current location, and delay time.
    -   (**`src/parse/train_info.py`**, **`src/parse/rate_train_info.py`**)

3.  **Data Processing and Formatting**:
    -   Filters the extracted raw data (based on a specific station and direction) and converts it into a multi-language (ko, en, ja) message.
    -   (**`src/api.py`**, **`src/get_contents.py`**)

4.  **Notification-Delivery**:
    -   Sends a POST request with the formatted message to a Discord webhook URL to deliver the notification.
    -   (**`src/DiscordManager.py`**)

5.  **Automation**:
    -   **GitHub Actions**: `schedule_morning.yml` and `schedule_evening.yml` files in `.github/workflows/` trigger the workflow at scheduled times.
    -   **Server (Cron)**: Shell scripts in the `ubuntu/` directory (e.g., `schedule_morning.sh`) are used to register a Cron job on a server for periodic execution.

## Project Structure

-   `.github/workflows/`: Contains workflow files for GitHub Actions. Files like `schedule_morning.yml` are responsible for running scripts at specific times.
-   `src/`: The main directory containing the core source code of the application.
    -   `api.py`: Acts as the main entry point that orchestrates the entire process. It defines the API functions that can be called externally.
    -   `parse/`: Contains modules for parsing the website's HTML.
        -   `rate_train_info.py`: Parses the entire operation information page to extract delay status, notices, and individual train data.
        -   `train_info.py`: Parses the detailed information of an individual delayed train.
    -   `get_contents.py`: Formats the parsed data into a user-friendly, multi-language (ko, en, ja) message.
    -   `DiscordManager.py`: Responsible for sending the formatted message to a Discord webhook.
-   `ubuntu/`: Contains shell scripts for running the script as a Cron job in an Ubuntu server environment.
-   `config.py`: Manages major configuration values, such as the target URL for scraping and keywords needed for parsing.
-   `requirements.txt`: A list of the Python packages required to run the project.
-   `LICENSE`: Specifies the project's open-source license (MIT).

## Key Logic Flow

1.  **Trigger**: A scheduler from GitHub Actions or a server's Cron job calls an execution script (`reusable_check.yml` or `reusable_check.py`) at a specified time.
2.  **API Call**: The script calls a function like `get_train_status_range_api` defined in `src/api.py` to start the process, passing parameters such as the station to check, direction, and language.
3.  **HTML Fetching**: `src/parse/rate_train_info.py` accesses the JR-Central website and fetches the HTML page containing the latest operation information.
4.  **Status Check**: It analyzes the fetched HTML to first determine if the status is 'Normal Operation' or 'Delayed'. If trains are running normally, the process ends without a notification.
5.  **Detailed Parsing**: If a delay has occurred, it uses `BeautifulSoup4` to extract the content of the delay notice and information for each train.
6.  **Individual Train Data Extraction**: `src/parse/train_info.py` pulls specific details from each train's HTML snippet, such as train type, destination, current location, and delay time.
7.  **Data Filtering**: `src/api.py` filters all the extracted train information, keeping only the data that matches the user-configured station and direction (up/down).
8.  **Message Generation**: `src/get_contents.py` takes the filtered data and generates the final message to be sent to Discord, formatted in the specified language (ko, en, ja).
9.  **Notification Dispatch**: `src/DiscordManager.py` sends the generated message to the Discord webhook URL, delivering the notification to the user.

## Setup and Usage

### Prerequisites

-   Python 3.x
-   `pip`
-   `git`

### 1. Running in a Local Environment

1.  **Clone Project and Initialize Submodules**:
    ```bash
    git clone https://github.com/your-username/train_time_check.git
    cd train_time_check
    git submodule update --init --recursive
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set Environment Variables**:
    -   Create a `.env` file in the project root and add your Discord webhook URL.
      ```
      WEBHOOK_URL="https://discord.com/api/webhooks/your/webhook_url"
      ```

4.  **Run a Test**:
    -   You can check the results for specific conditions in the console by running the `src/api.py` file directly.
      ```python
      # Modify the test code at the bottom of src/api.py
      result = get_train_status_range_api("Kariya", range_n=6, language="en", direction="up")
      ...
      ```

### 2. Automating with GitHub Actions

1.  **Fork the Repository**: Fork this repository to your own GitHub account.
2.  **Set Secrets**:
    -   Go to `Settings` > `Secrets and variables` > `Actions` in your forked repository.
    -   Click `New repository secret` and add your Discord webhook URL with the name `WEBHOOK_URL`.
3.  **Enable and Modify Workflows**:
    -   Uncomment the cron schedule in the `schedule_*.yml` files under `.github/workflows/` and set your desired time.
    -   In the `with` section, modify parameters like `target_station` and `direction` to match your environment.
    -   Push the changes to your `main` or `dev` branch to activate the workflows.

### 3. Automating with Cron on a Server (Ubuntu)

1.  **Deploy Project to Server**: Clone and set up the project on your server as you would in a local environment.
2.  **Modify Execution Scripts**: In the `ubuntu/` directory, set variables like `TARGET_STATION` and `DIRECTION` in the `schedule_morning.sh` and `schedule_evening.sh` files.
3.  **Register Cron job**:
    ```bash
    crontab -e
    ```
    -   In the editor, add the schedule as follows (example runs at 7:30 AM every day).
      ```cron
      30 7 * * 1-5 /path/to/your/project/train_time_check/ubuntu/schedule_morning.sh
      ```

## Disclaimer and Copyright Notice

-   **Data Source and Copyright**: The copyright for the original data and content of all information provided by this project belongs to **JR-Central (Central Japan Railway Company)**. This project does not claim ownership of the data.
-   **Unofficial Project**: This is an **personal project for learning purposes** and is not affiliated with, endorsed by, or in any way officially connected with JR-Central.
-   **Non-Commercial Use**: This project should be used for non-commercial purposes only. Any form of for-profit use is strictly prohibited.
-   **Data Non-Storage**: This application does not save scraped data to any external server or file. Information is processed temporarily in memory only for the purpose of sending a notification and is immediately discarded when the process ends.
-   **Limitation and Responsibility of Information**: This project relies on web scraping, not an official API, and may stop functioning without notice if the source website's structure changes. It does not guarantee the complete accuracy or real-time status of the information. The developer assumes no legal responsibility for any direct or indirect damages resulting from its use.
-   **Responsibility for Scraping**: By using this project, the user is responsible for not overloading the JR-Central website and for respecting the website's Terms of Service. The user is solely responsible for any legal issues that arise from the use of this project, including but not limited to potential infringement of the data provider's rights.