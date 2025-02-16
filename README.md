# Namaz Timings

## Project Setup

### 1. Install Python
Ensure you have Python installed on your system. You can download it from the [official Python website](https://www.python.org/downloads/).

### 2. Create a Virtual Environment
Create a virtual environment to manage dependencies for this project. Run the following command in your terminal:

```bash
python -m venv venv
```

Activate the virtual environment:

- On Windows:
    ```bash
    .\venv\Scripts\activate
    ```
- On macOS/Linux:
    ```bash
    source venv/bin/activate
    ```

### 3. Install Requirements
Install the required dependencies using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` File
Create a `.env` file in the root directory of the project. Use the values mentioned in the `.env.sample` file to populate your `.env` file.

```bash
cp .env.sample .env
```

Edit the `.env` file to include your specific environment values.

### 6. Run the Project
To run the project, execute the following command in your terminal:

```bash
python main.py --city "City Name"
```

### 5. Download and Store Adblocker Extension
1. Download the adblocker extension `.crx` file from a trusted source.

2. Move the downloaded `.crx` file to the `chrome_extensions` directory:

    ```bash
    mv /path/to/adblocker_extension.crx chrome_extensions/
    ```

3. Ensure the extension is loaded when running the project by updating your project configuration to include the path to the adblocker extension.

## Running the App Manually (Optional, but Recommended)

To get the chromedriver, we need to run the app manually for the first time. By running the following command, the code will be executed and chrome driver will be installed.

```sh
python main.py --city "City Name"
```

Now you'll have chromedriver file at:

- **Windows**: `C:\Users\<YourUsername>\.wdm\drivers\chromedriver\<version>`
- **Linux**: `/home/<YourUsername>/.wdm/drivers/chromedriver/<version>`
- **macOS**: `/Users/<YourUsername>/.wdm/drivers/chromedriver/<version>`

We can copy that file into the `/path/to/<PROJECT_NAME>/chrome_driver/`

```sh
cp /home/<YourUsername>/.wdm/drivers/chromedriver/<version> /path/to/<PROJECT_NAME>/chrome_driver/
```