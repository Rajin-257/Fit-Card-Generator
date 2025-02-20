from flask import Flask, request, render_template
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import time
from datetime import datetime
import calendar

app = Flask(__name__)

def extract_medical_data(customer_code):
    """Extracts medical data using Selenium WebDriver."""
    options = Options()
    options.headless = True  # Run browser in headless mode

    driver = webdriver.Firefox(options=options)
    extracted_data = {}

    try:
        driver.get("https://wafid.com/medical-status-search/")
        time.sleep(2)

        driver.find_element(By.ID, "id_search_variant_1").click()
        input_field = driver.find_element(By.ID, "id_gcc_slip_no")
        input_field.send_keys(customer_code, Keys.ENTER)
        time.sleep(2)

        # Wait for modal
        attempts = 0
        modal_present = False
        while not modal_present and attempts < 100:
            try:
                driver.find_element(By.CLASS_NAME, "medical-status-modal-acceptance")
                modal_present = True
            except:
                attempts += 1
                time.sleep(2)

        if not modal_present:
            return {"error": "Error: Modal not found after multiple attempts."}

        # Extract data
        fields = [
            "name", "marital_status", "height", "phone", "gender", "passport",
            "weight", "BMI", "age", "traveled_country__name", "applied_position__name",
            "passport_expiry_on", "medical_examination_date", "medical_center"
        ]

        for field in fields:
            extracted_data[field] = driver.find_element(By.ID, field).get_attribute("value")

        extracted_data['profile_picture_url'] = driver.find_element(By.CLASS_NAME, "profile-picture").get_attribute("src")

        # Calculate report expiry date
        medical_examination_date = datetime.strptime(extracted_data['medical_examination_date'], '%d/%m/%Y')
        new_month = (medical_examination_date.month + 2) % 12 or 12
        new_year = medical_examination_date.year + (1 if new_month < medical_examination_date.month else 0)

        last_day_of_new_month = calendar.monthrange(new_year, new_month)[1]
        new_day = min(medical_examination_date.day, last_day_of_new_month)
        extracted_data['report_expiry_date'] = datetime(new_year, new_month, new_day).strftime('%d/%m/%Y')

    except Exception as e:
        return {"error": str(e)}
    finally:
        driver.quit()

    return extracted_data


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        customer_code = request.form.get("customer_code")
        extracted_data = extract_medical_data(customer_code)

        if "error" in extracted_data:
            return extracted_data["error"]

        return render_template("report.html", extracted_data=extracted_data, customer_code=customer_code)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
