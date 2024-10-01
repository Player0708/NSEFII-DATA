import mysql.connector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from datetime import datetime


# MySQL Database Configuration
db_config = {
    'user': 'root',      # Replace with your MySQL username
    'password': 'An8169445460@',   # Replace with your MySQL password
    'host': 'localhost',           # Replace with your host
    'database': 'fiidataapi',   # Replace with your database name
}

# Setup WebDriver with headless options
options = webdriver.FirefoxOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Initialize the WebDriver
browser = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

# Load the webpage
browser.get("https://www.moneycontrol.com/stocks/marketstats/fii_dii_activity/index.php")

# Wait for the table element to load
table_element = WebDriverWait(browser, 30).until(
    EC.presence_of_element_located((By.XPATH, '//*[@id="fidicash"]/div/div/table/tbody/tr[1]'))
)

# Extract the text from the table element
table_text = table_element.text
print("Raw table text:", table_text)

# Split the text by whitespace to extract the individual data points
split_data = table_text.split()

# Assigning the data to variables
date_str = split_data[0]             # Date
buy_value_fii = float(split_data[1].replace(',', ''))  # FII Buy Value
sell_value_fii = float(split_data[2].replace(',', ''))  # FII Sell Value
net_value_fii = float(split_data[3].replace(',', ''))  # FII Net Value

# Close the browser
browser.quit()

date_object = datetime.strptime(date_str, '%d-%b-%Y')
formatted_date = date_object.strftime('%Y-%m-%d')


# Connecting to MySQL database
try:
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Insert query
    insert_query = """
    INSERT INTO appfii_fii_fpi_data (category, date, buy_value, sell_value, net_value)
    VALUES (%s, %s, %s, %s, %s)
    """
    
    # Execute the insert
    cursor.execute(insert_query, ('FII/FPI**', formatted_date, buy_value_fii, sell_value_fii, net_value_fii))
    connection.commit()

    print(f"FII data inserted for date: {date_str}")

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    # Close the database connection
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed.")
