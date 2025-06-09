# Selenium and Selenium Grid Documentation
#### Environment
- Ubuntu 24.04.2 LTS x86_64
- Google Chrome 137.0.7151.68
- Python 3.12.3
- Openjdk 21.0.7
- Selenium Grid 4.33.0
#### Running a Test Selenium Code in Python
- `python -m venv venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`
```py
import time
from selenium import webdriver

driver = webdriver.Chrome()

try:
  driver.get("http://selenium.dev")
finally:
  time.sleep(10)
  driver.quit()
```
- This is a simple script that can be detected for bots by the browser
- To make it bit less detectable:
```py
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options)

try:
  driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
      Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
      })
    """
  })

  driver.get("http://selenium.dev")
finally:
  time.sleep(10)
  driver.quit()
```

#### Setting up Selenium Grid
- install java
  - `sudo apt update`
  - `sudo apt install openjdk-21-jdk`
  - `java -version` to verify
- Download selenium grid jar file from the official website
  - https://www.selenium.dev/downloads/
- Run `java -jar Downloads/selenium-server-4.33.0.jar standalone`
  - This command starts a grid server at http://localhost:4444 with default 1 node and 12 maxumum sessions all in the same machine

#### Automation through selenium grid
```py
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

grid_url = "http://localhost:4444/wd/hub"
options = Options()

driver = webdriver.Remote(
  options=options,
  command_executor=grid_url
)

try:
  driver.get("http://selenium.dev")
finally:
  time.sleep(10)
  driver.quit()
```
- less detectable:
```py
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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
finally:
  time.sleep(10)
  driver.quit()
```

## How Selenium Grid Works
**Selenium Grid** allows you to run **browser automation** across **multiple machines**. This architecture is made up of three main components:
- The **Client**
- The **Hub**
- One or more **Nodes**.

### What is a Client?
The Client is the machine or script that initiates the automation. It:

- Contains your Selenium or WebDriver test code (e.g., a Python script using Selenium)
- Sends requests to the Hub to start and control browser sessions
- Receives responses and data from the browser

### What is a Hub?
The Hub is the central coordinator in a Selenium Grid setup. Meaning where the Selenium Grid itself is setup. It:

- Listens for incoming session requests from Clients
- Matches these requests with available Nodes based on requested capabilities (e.g., Chrome, Firefox)
- Forwards WebDriver commands from Clients to the appropriate Node

The Hub runs an internal HTTP server, usually listening on port 4444.

### What is a Node?
A Node is a worker machine that actually launches and runs the browser sessions. It:

- Registers itself with the Hub when started
- Accepts sessions forwarded by the Hub
- Create an instance of a browser driver (e.g., ChromeDriver)
- Executes commands like clicking, navigating, or taking screenshots

Each Node can support one or more browsers and concurrent sessions.

### Local (Standalone) Setup
In a **standalone** setup, all components — **Client**, **Hub**, and **Node** — run on the **same machine**.

You can start the entire grid with:
```
java -jar selenium-server-<version>.jar standalone
```

This runs the Hub and Node as a single process:
- No external network communication is needed
- Useful for local testing and development

### Distributed (Remote) Setup
In a distributed setup, the Selenium Grid components are separated across multiple machines:

- The Client (your test script) runs on your development machine.
- The Hub runs on a central server.
  - `java -jar selenium-server-<version>.jar hub` to start the hub. Make sure port 4444 is exposed and reachable by the machines that the nodes will be set up on.
- One or more Nodes run on remote machines, each capable of launching browsers.
  - `java -jar selenium-server-<version>.jar node --detect-drivers true --hub http://<hub-ip>:4444` to start a node and connect it to a hub
  - or create a node-config.toml file and `java -jar selenium-server-<version>.jar node --config node-config.toml`

```toml
[network]
hub = "http://localhost:4444"

[server]
port = 5555

[node]
detect-drivers = false

[[node.driver-configuration]]
  display-name = "Chrome"
  max-sessions = 6
  stereotype = "{\"browserName\": \"chrome\"}"
  binary = "/usr/bin/google-chrome"
```

This architecture is ideal for scaling tests across different platforms, browsers, or operating systems.

### Communication Flow
- Once everything is connected, the following communication happens:

#### Client → Hub
- The client script sends an HTTP POST /session request to the Hub at http://<hub-ip>:4444/wd/hub
- The request includes the desired capabilities (e.g., "browserName": "chrome")

#### Hub → Node
- The Hub selects a Node that matches the capabilities
- It forwards the session creation request to that Node

#### Node
- The Node launches the appropriate WebDriver (e.g., ChromeDriver)
- It controls the actual browser instance (e.g., Google Chrome)
- It executes WebDriver commands (click, navigate, etc.)

#### Node → Hub → Client
- All command responses flow back from the Node through the Hub to the Client

## Using "undetected-chromedriver" to make it more undetectable
- Does **NOT** work with selenium grid and works only with python
- This package uses `distutils` which is a default module that comes with python and was removed from python in 3.12
- In order to use the package install it along with `setuptools`
  - `pip install setuptools undetected-chromedriver` and run without grid
```py
import time
import undetected_chromedriver as uc

options = uc.ChromeOptions()
options.add_argument("--start-maximized")

driver = uc.Chrome(options=options)

try:
  driver.get("http://selenium.dev")
finally:
  time.sleep(10)
  driver.quit()
```
- Sometimes, `undetected-chromedriver` may fail to detect the correct Google Chrome installation path especially if Chrome was installed in a non-standard location.
  - In such a case you can sepcify the path to your chrome binary files `options.binary_location = "/chrome-path"`
  - Or specify the version of chromedriver using `driver = uc.Chrome(version_main=137)`