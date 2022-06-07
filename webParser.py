
from importlib.resources import contents
import logging
import random
from playwright.async_api import async_playwright 
from bs4 import BeautifulSoup as bs

class webParser:
        

    async def getsource(self, url, params_list, pass_user):
        """
        find the username and password params in the body
        """
        p = await async_playwright().start()
        browser = await p.firefox.launch()
            
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_load_state()
            
        body = await page.content()
        soup = bs(body, 'html.parser')
        buttons = soup.findAll(attrs={'type' : 'submit'})
        self.form = self.findForm(buttons, params_list["ButtonList"])
        
        self.user_param, self.password_param = self.findUserPass(self.form, params_list["password_param"], params_list["user_param"])
        self.contentLen = 0
        for i in range(0,2):
            username = pass_user['Usernames'][random.randint(0, len(pass_user['Usernames']) - 1)]
            password = self.pass_gen()
            logging.info('random password generated: ' + str(password))
            
            await self.getRequest(self.user_param, self.password_param, page, username, password)
            self.contentLen += self.contentLen
            
        self.contentLen = self.contentLen / 2
        await browser.close()
        await p.stop()

        self.req_body_type = self.get_req_type()
    
    def pass_gen(self):
        """
        generate strong password randomly
        """
        char_seq = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!#$%&'()*+,-./:;<=>?@[\]^_`{|}~"
        password = ''
        for len in range(10):
            random_char = random.choice(char_seq)
            password += random_char
            
        # print(password)
        list_pass = list(password)
        random.shuffle(list_pass)
        final_password = ''.join(list_pass)
        return final_password
    
    
    #identify the user and password params in the body
    def findUserPass(self, form, passwords, usernames):
        print('\n\n\n\n\n\n\n'+str(form))
        username = None
        password = None
        inputs = {}
        for input in form.findChildren('input'):
            if input['type'].lower() != 'submit':
                inputName = input['name']
                inputs[inputName] = ""
                if input['type'] == 'email':
                    username = inputName
                elif input['type'] == 'password':
                    password = inputName
        
        if not username:
            username = self.pick_param(inputs, usernames) 
            inputs.pop(username)
        if not password: 
            password = self.pick_param(inputs, passwords) 

        return username, password

    def jaccard_similarity(self, a, b):
        # convert to set
        a = set(a)
        b = set(b)
        # calucate jaccard similarity
        j = float(len(a.intersection(b))) / len(a.union(b))
        return j


    def similarity_value(self, param, usernames):
        if not param:
            return 0
        max = 0
        for uname in usernames:
            score = self.jaccard_similarity(param.lower(), uname)
            if score > max:
                max = score
        return max


    def pick_param(self, inputs, list):
        #param with max potetntial for being the username
        inputName = max(inputs, key=lambda x: self.similarity_value(x, list)) 
        return inputName

    def getRequestData(self, req):
        if req.method == 'POST': 
            self.post_data = req.post_data_json
            self.method = req.method
            self.action = req.url
            self.headers = {k.lower(): v for k, v in req.headers.items()}

            for param in self.headers:
                self.headers[param] = str(self.headers[param])
                
            # remove content length and cookies from headers
            if 'cookie' in self.headers:
                self.headers.pop('cookie')
                
            if 'content-length' in self.headers:
                self.headers.pop('content-length')

    
    def getResponse(self, response):
        self.status_code = response.status
        
        
    async def getRequest(self, username_element, password_element, page, username, password):

        await page.fill('input[name='+ username_element +']',  username)
        await page.fill('input[name='+ password_element +']', password)
        page.once("request", lambda req: self.getRequestData(req))
        page.once("response", lambda res: self.getResponse(res))
        await page.locator('[type="submit"]:near(input[name='+ password_element +'])').click()
        content = await page.content()
        self.contentLen = len(str(content))
        
        

    def formScore(self, form, button, buttonList):
        print('button list: '+ str(buttonList))
        buttonValueScore = 0
        if 'value' in button:   
            buttonValueScore = self.similarity_value(button['value'], buttonList)
        buttonTextScore = self.similarity_value(button.text, buttonList)
        score = max(buttonValueScore, buttonTextScore)
        if score == 1:
            return 10
        
        # check this later!
        for label in buttonList:
            if label in str(form.text).lower():
                score += 0.3

        inputs = []
        for inp in form.findChildren('input'):
            if inp['type'] == 'text' or inp['type'] == 'email' or inp['type'] == 'password' :
                inputs.append(inp)
                
        if len(inputs) < 2:
            return 0
        
        if len(form.findChildren('input', {'type' : 'password'})) == 1:
            score += 0.5
        if len(form.findChildren('input', {'type' : 'email'})) == 1:
            score += 0.3
        
    def findForm(self, buttons, buttonList):
        maxScore = 0
        for button in buttons:
            form = button.findParent('form')
            score = self.formScore(form, button, buttonList)
            if score > maxScore:
                maxScore = score
                pickedForm = form
                self.button = button
        
        return pickedForm


        
        # get content type from headers
    def get_req_type(self):
        type = self.headers["content-type"]

        if "json" in type:
            return "JSON"

        elif "xml" in type:
            import xmltodict
            
        elif "multipart" in type:
            return "multipart"

        else:
            import urllib

            return "URL_ENCODED"
