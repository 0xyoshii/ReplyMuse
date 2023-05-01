import requests 
import re
from bs4 import BeautifulSoup
import logging

logging.basicConfig(
    filename = 'file.log',
    level = logging.DEBUG,
    format = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
)

class AskMuse:
    def __init__(self, question):
        self.uri = "https://www.statmuse.com/ask"
        self.conversation_token = ""
        self.csrf = ""
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        self.question = question.replace(" ", "+")
        self.delay = 1
        pass

    def getTokens(self):
        while True:
            try:
                print(self.uri + '/' + self.question)
                r = self.session.get(self.uri + '/' + self.question, headers=self.headers)
                if r.status_code == 200:
                    text = r.text
                    #matchConv = re.search(r'conversation-token="([^"]+)"', text)
                    matchCsrf = re.search(r'csrf-token="([^"]+)"', text)
                    if matchCsrf:
                        return matchCsrf.group(1)
                    else:
                        logging.error("Error getting CSRF")
                        return
                elif r.status_code == 422:
                    logging.error("Data not found")
                    return
                else:
                    logging.error("Error getting request, retrying - status code " + f"[{r.status_code}]")
                    return
            except Exception as e:
                logging.error("Error getting CSRF, retrying - " + e)
                return
            

    def ask(self):
        try:
            self.csrf = self.getTokens()
        except: 
            return

        #data = f"question%5Bquery%5D={self.question.replace('+', ' ')}&question%5Bpreferred_domain%5D=&question%5Bconversation_token%5D={self.conversation_token}&_csrf_token={self.csrf}"
        data = f"question%5Bquery%5D={self.question.replace('+', ' ')}&question%5Bpreferred_domain%5D=&question%5Bconversation_token%5D=&_csrf_token={self.csrf}"

        while True:
            try:         
                send = self.session.post(self.uri, headers=self.headers, data = data)
                if send.status_code == 200:
                    logging.info("Ask successful")

                    soup = BeautifulSoup(send.text, 'html.parser')
                    name = soup.select_one('body > div.main-layout.mb-5.bg-team-primary.text-team-secondary > div > div.flex-1.flex.flex-col.justify-between.text-center.md\:text-left > h1 > p > a').text
                    stats = soup.select_one('body > div.main-layout.mb-5.bg-team-primary.text-team-secondary > div > div.flex-1.flex.flex-col.justify-between.text-center.md\:text-left > h1 > p').text

                    if name in stats:
                        return stats 
                    else:
                        return name + stats

                else:
                    logging.error(f"Ask failed - [{send.status_code}]")
                    return
            except Exception as e:
                logging.error("Error asking - " + e)
                return



