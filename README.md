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
### 5. Set Desired City Name
Open the `.env` file and set the `CITY_NAME` variable to the desired city for which you want to fetch Namaz timings.

### 6. Run the Project
To run the project, execute the following command in your terminal:

```bash
python .\main_listing.py
```