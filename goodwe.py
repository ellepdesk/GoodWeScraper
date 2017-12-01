import requests
import logging
import configparser


class ScraperSession(requests.Session):
    def __init__(self, configfile='goodwe.cfg'):
        super().__init__()
        config = configparser.ConfigParser()
        config.read(configfile)
        config = config['station']

        self.stationId = config['stationId']
        self.inverterSN = config['inverterSN']
        self.username = config['username']
        self.password = config['password']

        self.home()
        self.login()

    def home(self):
        logging.info("Opening main site")
        home_url = "http://www.goodwe-power.com/User/Index"
        result = self.get(home_url)

    def login(self):
        logging.info("Logging in")
        payload = {"username": self.username,
                   "password": self.password}
        login_url = "http://www.goodwe-power.com/User/Login"
        result = self.post(login_url, data=payload)

    def request_export(self, date):
        logging.info(f"Requesting export for {date}")
        payload = {"QueryType": 0,
                   "DateFrom": date,
                   "ID": self.stationId,
                   "InventerSN": self.inverterSN}
        export_url = "http://www.goodwe-power.com/PowerStationPlatform/PowerStationReport/ExportHistoryData"
        return self.post(export_url, json=payload).json()

    def download_export(self, result):
        if result["result"] != 'true':
            logger.error("Cannot download failed export")
            return

        downloadFilePath = result["downloadFilePath"]
        fileName = result["fileName"]
        logging.info(f"Downloading export {fileName}")

        url = "http://www.goodwe-power.com/PowerStationPlatform/PowerStationReport/DownloadFile"
        dl_url = f"{url}?ID={self.stationId}&downloadFilePath={downloadFilePath}&fileName={fileName}"
        response = self.get(dl_url)
        with open(fileName, mode='wb') as f:
            f.write(response.content)

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(name)s:%(levelname)s:%(message)s', level=logging.INFO)
    dates = [f"2016-{month:02}-01" for month in range(1, 2)]
    with ScraperSession() as s:
        for date in dates:
            export = s.request_export(date)
            s.download_export(export)
