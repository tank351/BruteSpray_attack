from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.firefox.launch()
    page = browser.new_page()
    page.on("request", lambda request: print(">>", 'body: ', request.post_data_json, "\n", "action: ", request.url,"\n", "headers: ", request.headers) if request.method == 'POST' else None)
    'suh)'

    page.goto("http://testphp.vulnweb.com/login.php")
    page.fill('input[name="uname"]', 'lmlmlklss@gmail.com')
    page.fill('input[name="pass"]', 'weponsd')
    page.locator('[type="submit"]:near(input[name="pass"])').click()
    #page.click('input[type="submit"]')

# Verify app is logged in