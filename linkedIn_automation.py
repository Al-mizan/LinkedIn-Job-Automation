from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv
from linkedIn_verification_code import LinkedInVerification

class LinkedInAutomation:
    def __init__(self):
        load_dotenv()
        self.linkedin_password = os.getenv("linkedin_password")
        self.gmail_user = os.getenv("GMAIL_USER")
        chrome_driver_path = "/media/almizan/Personal/selenium/chromedriver-linux64/chromedriver"
        service = Service(executable_path=chrome_driver_path)
        self.driver = webdriver.Chrome(service=service)
        self.verification = LinkedInVerification()


    def login(self):
        try:
            WebDriverWait(self.driver, 20).until(
                EC.any_of(
                    EC.presence_of_element_located((By.ID, "username")),
                    EC.presence_of_element_located((By.ID, "session_key"))
                )
            )

            email_field = self.driver.find_elements(By.ID, "username") or self.driver.find_elements(By.ID, "session_key")
            if email_field:
                email_field[0].send_keys(self.gmail_user)

            password_field = self.driver.find_elements(By.ID, "password") or self.driver.find_elements(By.ID, "session_password")
            if password_field:
                password_field[0].send_keys(self.linkedin_password)

            sign_in_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Sign in')]")
            if not sign_in_buttons:
                sign_in_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[type='submit']")

            if sign_in_buttons:
                sign_in_buttons[0].click()
            else:
                print("Could not find sign in button")

            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.scaffold-finite-scroll__content")))
            print("Login successful!")

        except Exception as e:
            print(f"Login failed: {str(e)}")
            self.driver.save_screenshot("login_error.png")


    def linkedin_verify(self, code):
        verify_field = self.driver.find_elements(By.ID, "input__email_verification_pin")
        if verify_field:
            verify_field[0].send_keys(code)
        submit = self.driver.find_elements(By.ID, "email-pin-submit-button")
        if submit:
            submit[0].click()


    def job_save(self):
        try:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located(("css selector", "a.job-card-container__link"))
            )
            elements = self.driver.find_elements(By.CSS_SELECTOR, "a.job-card-container__link")

            for element in elements:
                job = element.get_attribute("aria-label")
                if ("AI" or "ai" or "ML" or "ml" or "Python" or "python") in job:
                    element.click()
                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "button.jobs-save-button"))
                    )
                    self.driver.find_element(By.CSS_SELECTOR, "button.jobs-save-button").click()

        except Exception as e:
            print(f"Job save failed: {str(e)}")
            self.driver.save_screenshot("job_save.png")

    def run(self):
        try:
            self.driver.get("https://www.linkedin.com/login")
            self.login()
            sleep(2)

            code = self.verification.get_verification_code()
            self.linkedin_verify(code)

            self.driver.get("https://www.linkedin.com/jobs/search/?currentJobId=4223666381&distance=25&geoId=106215326&keywords=python%20developer&origin=JOBS_HOME_KEYWORD_HISTORY&refresh=true")
            self.job_save()

        except Exception as e:
            print(e)
            self.driver.save_screenshot("login_error.png")
        finally:
            self.driver.quit()

if __name__ == "__main__":
    automation = LinkedInAutomation()
    automation.run()