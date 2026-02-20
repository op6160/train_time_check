# Train Operation Information Notifier

This project is a system that checks for train delays and service suspensions on the JR Central website and sends notifications to a designated Discord channel. <br>
It was developed to solve the commuting inconvenience of having to manually check the website each time or only noticing a train delay upon arriving at the station, due to the absence of an official push notification service.

This project supports two automation methods.<br>
1. Cron Automation: This is the recommended method for stable, regular/periodic execution. It can be configured using the scripts in the `ubuntu/` directory.<br>
A server or device is required.
> Verified OS: `mac 26.2`, `ubuntu 22.04`
2. GitHub Actions: An alternative for users without a separate server environment. It can be activated by uncommenting the `cron` section in the `schedule_*.yml` files within `.github/workflows/`, and is also used for automatic debugging when the repository code is updated.

## Key Features

-   **Real-time Operation Information Check**: Scrapes the JR Central line website to check the current operational status.
-   **Delay Information Parsing**: When a train delay occurs, it extracts detailed delay information (affected sections, time, etc.) and the location of each train.
-   **Multilingual Support**: Processes and provides the confirmed information in Korean, Japanese, and English.
-   **Discord Notifications**: Sends formatted operational information to a specified Discord channel via a webhook.
-   **Automated Execution**: Can be set to run automatically at specific times (e.g., commute times) through GitHub Actions or a server Cron job.
-   **Targeting Feature**: Can filter and send notifications for only relevant train information based on a specific station and direction of travel (inbound/outbound).
-   **Error Reporting**: Automatically registers a new issue on GitHub when a new error occurs.

## How It Works

1.  **Data Collection (Web Scraping)**:
    -   Fetches the HTML of the JR Central line's operation information page using `requests` or `selenium`.
    -   (**`src/parse/rate_train_info.py`**)

2.  **Information Parsing and Analysis**:
    -   Parses the fetched HTML using `BeautifulSoup` to check if the overall operational status is 'Normal Operation'.
    -   If a delay has occurred, it extracts the full text of the announcement along with detailed information for each delayed train, such as type, destination, current location, and delay time.
    -   (**`src/parse/train_info.py`**, **`src/parse/rate_train_info.py`**)

3.  **Data Processing and Formatting**:
    -   Filters the extracted raw data (based on specific stations, directions) and converts it into multilingual (ko, en, ja) messages.
    -   (**`src/api.py`**, **`src/get_contents.py`**)

4.  **Notification Sending**:
    -   Sends a POST request with the processed message to a Discord webhook URL to notify users.
    -   (**`src/DiscordManager.py`**)

5.  **Automation**:
    -   **GitHub Actions**: `schedule_morning.yml` and `schedule_evening.yml` files in `.github/workflows/` trigger the workflow at scheduled times.
    -   **Server (Cron)**: Shell scripts (`schedule_morning.sh`, etc.) in the `ubuntu/` directory are registered as Cron jobs on the server for periodic execution.

## Project Structure

-   `.github/workflows/`: Contains workflow files for GitHub Actions.
-   `src/`: The main directory containing the core source code of the application.
    -   `api.py`: Defines API functions to be called from external sources.
    -   `parse/`: Modules for parsing website data.
        -   `rate_train_info.py`: Parses the entire operation information page to extract delay status, announcements, and information for each train.
        -   `train_info.py`: Parses detailed information for individual delayed trains.
    -   `get_contents.py`: Processes and formats parsed data into user-friendly multilingual (ko, en, ja) messages.
    -   `DiscordManager.py`: A manager for sending messages to a Discord webhook.
-   `ubuntu/`: A directory containing shell scripts for automating tasks in a Ubuntu server environment.
-   `config.py`: Manages key configuration values required for operation, such as target URLs for scraping and keywords for parsing.
-   `requirements.txt`: A list of Python packages required to run the project.
-   `LICENSE`

## Main Logic Flow

1.  **Execution**: A scheduler in GitHub Actions or a Cron job on a server calls the execution script (`reusable_check.yml` or `reusable_check.py`) at a specified time.
2.  **API Call**: The script initiates the process by calling a function like `get_train_status_range_api` defined in `src/api.py`. It passes parameters such as the station to check, direction, and language.
3.  **HTML Collection**: `src/parse/rate_train_info.py` connects to the JR Central website to fetch the HTML page containing the latest operation information.
4.  **Operation Status Check**: It analyzes the fetched HTML to first determine if the status is 'Normal Operation' or 'Delayed'. If normal, the process terminates without sending a notification.
5.  **Detailed Information Parsing**: If a delay has occurred, it uses `BeautifulSoup4` to extract the content of the delay announcement and information for each train.
6.  **Individual Train Information Extraction**: `src/parse/train_info.py` extracts specific details from the HTML snippet of each train, such as train type, destination, current location, and delay time.
7.  **Data Filtering**: `src/api.py` filters all the extracted train information to find only what corresponds to the user-configured station and direction (inbound/outbound).
8.  **Message Generation**: Based on the filtered data, `src/get_contents.py` creates the final message to be sent to Discord in the specified language (ko, en, ja).
9.  **Notification Dispatch**: `src/DiscordManager.py` sends the generated message to the Discord webhook URL to notify the user.

## Installation and Usage

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

4.  **Test Run**:
    -   You can directly run the `src/api.py` file to see the results for specific conditions in the console.
      ```python
      # Modify the test code at the bottom of src/api.py
      result = get_train_status_range_api("Kariya", range_n=6, language="en", direction="up")
      ...
      ```

### 2. Automation with GitHub Actions

1.  **Fork the Repository**: Fork this repository to your own GitHub account.
2.  **Configure Secrets**:
    -   Go to your forked repository's `Settings` > `Secrets and variables` > `Actions`.
    -   Click `New repository secret` and add your Discord webhook URL with the name `WEBHOOK_URL`.
3.  **Enable and Modify Workflow**:
    -   In `.github/workflows/`, uncomment the cron schedule in the `schedule_*.yml` files and set your desired time.
    -   In the `with` section, modify parameters like `target_station`, `direction`, etc., to fit your environment.
    -   Push the changes to your `main` or `dev` branch to activate the workflow.

### 3. Automation with Cron on a Server (Ubuntu)

1.  **Deploy Project to Server**: Clone and set up the project on your server, same as in the local environment.
2.  **Modify Execution Scripts**: In the `ubuntu/` directory, set variables like `TARGET_STATION`, `DIRECTION` in the `schedule_morning.sh` and `schedule_evening.sh` files.
3.  **Register Cron job**:
    ```bash
    crontab -e
    ```
    -   In the editor, add a schedule like the one below (e.g., to run at 7:30 AM every weekday):
      ```cron
      30 7 * * 1-5 /path/to/your/project/train_time_check/ubuntu/schedule_morning.sh
      ```

## Disclaimer
* This project is an unofficial open-source project created for personal learning and convenience. Commercial use is prohibited.

* Data Source and Rights: The original copyright for all provided train operation information belongs to JR Central (Central Japan Railway Company). This project does not claim ownership of the original data and does not store data separately after sending notifications.

* Load Prevention: Please set an appropriate execution interval (e.g., via Cron) to avoid overloading the target website's server. The user is responsible for any issues, such as IP bans, caused by indiscriminate, short-interval executions.
  
* As this utilizes web scraping and not an official API, it may cease to function correctly without notice if the target website's structure changes. The 100% accuracy or real-time nature of the provided information is not guaranteed.
