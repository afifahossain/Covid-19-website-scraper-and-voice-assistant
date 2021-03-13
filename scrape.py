import requests
import json
import pyttsx3
import speech_recognition as sr
import re
import threading
import time

API_KEY = "tD5tydfTyfq3"
PROJECT_TOKEN = "tvQXt4y_FkYW"
RUN_TOKEN = "t8vchK8e5ZTS"


class Data:
    def __init__(self, api_key, project_token):
        self.api_key = api_key
        self.project_token = project_token
        self.params = {
            "api_key": self.api_key
        }
        self.data = self.get_data()

    def get_data(self):
        response = requests.get(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/last_ready_run/data',
                                params=self.params)
        data = json.loads(response.text)
        return data

    def total_cases(self):
        data = self.data['Total']

        for content in data:
            if content['name'] == "Coronavirus Cases:":
                return content['Value']

    def total_deaths(self):
        data = self.data['Total']

        for content in data:
            if content['name'] == "Deaths:":
                return content['Value']

        return "0"

    def country_data(self, Country):
        data = self.data["Country"]

        for content in data:
            if content['name'].lower() == Country.lower():
                return content

        return "0"

    def list_of_countries(self):
        countries = []
        for Country in self.data['Country']:
            countries.append(Country['name'].lower())

        return countries

    def update_data(self):
        response = requests.post(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/run',
                                 params=self.params)

        def poll():
            time.sleep(0.1)
            old_data = self.data
            while True:
                new_data = self.get_data()
                if new_data != old_data:
                    self.data = new_data
                    print("Updated")
                    break
                time.sleep(5)

        t = threading.Thread(target=poll)
        t.start()


def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
        except Exception as e:
            print("Exception:", str(e))

    return said.lower()


def main():
    print("Start")
    data = Data(API_KEY, PROJECT_TOKEN)
    END_PHRASE = "Stop"
    country_list = data.list_of_countries()

    total_patterns = {
        re.compile("[\w\s]+ total [\w\s]+ cases"): data.total_cases,
        re.compile("[\w\s]+ total cases"): data.total_cases,
        re.compile("[\w\s]+ total [\w\s]+ deaths"): data.total_deaths,
        re.compile("[\w\s]+ total deaths"): data.total_deaths
    }

    country_patterns = {
        re.compile("[\w\s]+ cases [\w\s]+"): lambda country_name: data.get_country_data(country_name)['Total_Cases'],
        re.compile("[\w\s]+ deaths [\w\s]+"): lambda country_name: data.get_country_data(country)['Total_Deaths'],
    }

    update_command = "update"

    while True:
        print("Listening...")
        text = get_audio()
        print(text)
        res = None

        for pattern, func in country_patterns.items():
            if pattern.match(text):
                words = set(text.split(" "))
                for country in country_list:
                    if country in words:
                        res = func(country)
                        break

        for pattern, func in total_patterns.items():
            if pattern.match(text):
                res = func()
                break

        if text == update_command:
            res = "Please wait"
            data.update_data()

        if res:
            speak(res)

        if text.find(END_PHRASE) != -1:  
            print("Exit")
            break


main()
