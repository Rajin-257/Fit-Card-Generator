from flask import Flask, request, render_template_string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime
import calendar

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        customer_code = request.form.get("customer_code")

        driver = webdriver.Firefox()  
        
        extracted_data = {}
        
        try:
            driver.get("https://wafid.com/medical-status-search/")
            time.sleep(2)

            radio_button = driver.find_element(By.ID, "id_search_variant_1")
            radio_button.click()

            input_field = driver.find_element(By.ID, "id_gcc_slip_no")
            input_field.send_keys(customer_code)
            input_field.send_keys(Keys.ENTER)

            time.sleep(5) 

            extracted_data['name'] = driver.find_element(By.ID, "name").get_attribute("value")  
            extracted_data['marital_status'] = driver.find_element(By.ID, "marital_status").get_attribute("value")
            extracted_data['height'] = driver.find_element(By.ID, "height").get_attribute("value") 
            extracted_data['phone'] = driver.find_element(By.ID, "phone").get_attribute("value")  
            extracted_data['gender'] = driver.find_element(By.ID, "gender").get_attribute("value")
            extracted_data['passport'] = driver.find_element(By.ID, "passport").get_attribute("value")
            extracted_data['weight'] = driver.find_element(By.ID, "weight").get_attribute("value") 
            extracted_data['BMI'] = driver.find_element(By.ID, "BMI").get_attribute("value") 
            extracted_data['age'] = driver.find_element(By.ID, "age").get_attribute("value")
            extracted_data['traveled_country__name'] = driver.find_element(By.ID, "traveled_country__name").get_attribute("value")
            extracted_data['applied_position__name'] = driver.find_element(By.ID, "applied_position__name").get_attribute("value")
            extracted_data['passport_expiry_on'] = driver.find_element(By.ID, "passport_expiry_on").get_attribute("value")
            extracted_data['medical_examination_date'] = driver.find_element(By.ID, "medical_examination_date").get_attribute("value")
            extracted_data['medical_center'] = driver.find_element(By.ID, "medical_center").get_attribute("value")

            profile_picture_element = driver.find_element(By.CLASS_NAME, "profile-picture")
            extracted_data['profile_picture_url'] = profile_picture_element.get_attribute("src")

            print("Extracted Data:", extracted_data)

            medical_examination_date_str = extracted_data['medical_examination_date']
            medical_examination_date = datetime.strptime(medical_examination_date_str, '%d/%m/%Y')
            
            new_month = medical_examination_date.month + 2
            new_year = medical_examination_date.year

            if new_month > 12:
                new_month -= 12
                new_year += 1

            last_day_of_new_month = calendar.monthrange(new_year, new_month)[1]
            new_day = min(medical_examination_date.day, last_day_of_new_month)

            report_expiry_date = datetime(new_year, new_month, new_day)
            extracted_data['report_expiry_date'] = report_expiry_date.strftime('%d/%m/%Y')

        except Exception as e:
            return f"Error: {str(e)}"
        finally:
            driver.quit()

        hospital_name = extracted_data['medical_center']

        return render_template_string("""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Fit Card</title>
                <!-- Link to the CSS file in the static folder -->
                <link rel="stylesheet" href="{{ url_for('static', filename='css/bootstrap.min.css') }}">
                <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
            </head>
            <body>
                <button id="print">Print</button>
                <div class="container">
                    <div class="row">
                        <div class="col">
                            <img class="logo1" src="{{ url_for('static', filename='img/Untitled-1.png') }}" alt="">
                        </div>
                        <div class="col hos_info">
                            <p class="title"><strong>Detailed candidate report</strong></p>
                            <p class="tile_med">Medical center name</p>
                            <p class="hos_name"> <strong>{{ extracted_data['medical_center'] }}</strong></p>
                        </div>
                        <div class="col d-flex justify-content-end">
                            <img class="logo2" src="{{ url_for('static', filename='img/2.png') }}" alt="">
                        </div>
                    </div>
                    <div class="code">
                        <p>G.H.C. Code No. <br> 05/04/03</p>
                        <p>GCC Slip No. <br> {{ customer_code }}</p>
                        <p>Date examined <br> {{ extracted_data['medical_examination_date'] }}</p>
                        <p>Report expiry date<br> {{ extracted_data['report_expiry_date'] }}</p>
                    </div>
                    <div style="text-align: center;">
                        <p style="letter-spacing: 1.1px; font-weight: 600; font-size: 12.6524px;">CANDIDATE INFORMATION</p>
                    </div>
                    <div class="row per-info" style="position: relative; top: 15px;">
                        <div class="col">
                            <!-- Dynamically set the profile image URL -->
                            <img style="margin-right: 58px;" class="per-img" src="{{ extracted_data['profile_picture_url'] }}" alt="Profile Picture">
                            <div class="row">
                                <p style="line-height: 1.2; padding: 0; display: inline-block;">Name <br> <strong>{{ extracted_data['name'] }}</strong></p>
                                <div class="col">
                                    <p style="line-height: 1.2;">Marital status<br><strong>{{ extracted_data['marital_status'] }}</strong> <br> Height <br> <strong>{{ extracted_data['height'] }}</strong></p>
                                </div>
                                <div class="col">
                                    <p style="line-height: 1.2; position: relative; left: 12px;">Passport No. <br> <strong>{{ extracted_data['passport'] }}</strong> <br> Weight <br> <strong>{{ extracted_data['weight'] }}</strong></p>
                                </div>
                                <div class="col">
                                    <p style="line-height: 1.2; position: relative; left: 22px;">Age <br> <strong> {{ extracted_data['age'] }}</strong> <br> BMI <br> <strong>{{ extracted_data['BMI'] }}</strong></p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col">
                            <div class="row">
                                <div class="col">
                                    <p style="line-height: 1.2; position: relative; left: 23px;">Gender<br> <strong>{{ extracted_data['gender'] }}</strong> <br> Passport expiry date <br> <strong>{{ extracted_data['passport_expiry_on'] }}</strong></p>
                                </div>
                                <div class="col">
                                    <p style="line-height: 1.2; position: relative; left: 60px;">Nationality <br> <strong> Bangladeshi</strong> <br> phone <br> <strong>{{ extracted_data['phone'] }}</strong></p>
                                </div>
                                <div class="col">
                                    <p style="line-height: 1.2; position: relative; left: 90px;">Travelling to <br> <strong>{{ extracted_data['traveled_country__name'] }}</strong> <br> Profession <br> <strong>{{ extracted_data['applied_position__name'] }}</strong></p>
                                </div>
                            </div>
                        </div>
                    </div>
                     <div class="row">
                        <div class="col"></div>
                        <div class="col">
                            <p style="font-size: 11px; line-height: 1.3; position: relative ;top: 520px; left: 40px; letter-spacing: -0.1px; width: 90%;" >Mentioned above is the medical report for Mr./Ms. <strong>{{ extracted_data['name'] }}</strong> who is Fit for the above mentioned job according to the GCC criteria</p>
                        </div>
                    </div>
        
        <img style="position: relative; top: -10px;" class="static_pic"
                 src="{% if extracted_data['medical_center'] == 'Medi Health Medical Center' %}
                     {{ url_for('static', filename='img/medihelth.png') }}
                     
                     {% else %}
                     {{ url_for('static', filename='img/tabuk.png') }}
                     {% endif %}" alt="">

                </div>
            
                <script>
                    const printbtn = document.getElementById('print');
                    printbtn.addEventListener('click', function(){
                        window.print();
                    });
                </script>
            </body>
            </html>
        """, extracted_data=extracted_data, customer_code=customer_code)

    return '''
        <form method="post">
            <label for="customer_code">Enter Customer Code:</label>
            <input type="text" name="customer_code" id="customer_code" required>
            <input type="submit" value="Submit">
        </form>
    '''


if __name__ == "__main__":
    app.run(debug=True)
