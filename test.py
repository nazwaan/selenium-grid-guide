import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

grid_url = "http://localhost:4444/wd/hub"

options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Remote(
  options=options,
  command_executor=grid_url
)

try:
  driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
      Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
      })
    """
  })
  
  driver.get("http://selenium.dev")

  downloads_link = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//span[text()='Downloads']"))
  )

  downloads_link.click()
finally:
  time.sleep(10)
  driver.quit()