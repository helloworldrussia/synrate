import requests
from parser_nelikvidy import ParserNelikvidy
from parser_tenderpro import ParserTender
from parser_roseltorg import RoseltorgParser
from parser_isource import ParserSource
from parser_tektorg import ParserTektorg
from parser_onlinecontract import ParserOnlineContract
from threading import Thread
import time
import sys
import urllib3
from json.decoder import JSONDecodeError
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ParserThread(Thread):
    def __init__(self, name, parser):
        Thread.__init__(self)
        self.daemon = False
        self.status = True
        self.name = name
        self.active = True
        self.parser = parser

    def run(self):
        """
            Status - статус движка, при изменении на false извне после завершении парсинга завершает поток.
            Active - для самого парсера, пока включён - парсит. Пока не включён - не парсит ^.^
        :return:
        """
        while self.status:
            while self.active:
                if self.active:
                    self.parser.parse()
                    time.sleep(1500)


class CheckThread(Thread):
    def __init__(self, name):
        Thread.__init__(self)
        self.daemon = False
        self.status = True
        self.name = name
        self.active = True

    def run(self):
        """
            Status - статус движка, при изменении на false извне после завершении парсинга завершает поток.
            Active - для самого парсера, пока включён - парсит. Пока не включён - не парсит ^.^
        :return:
        """
        while self.status:
            while self.active:
                if self.active:
                    print("Parsing")
                    time.sleep(1)


def server_listener():
    nelikvidy_obj = ParserNelikvidy(False)
    tender_obj = ParserTender()
    roseltorg_obj = RoseltorgParser()
    isource_obj = ParserSource()
    tectorg_obj = ParserTektorg()
    onlinecontract_obj = ParserOnlineContract()

    parser_roseltorg = ParserThread("parser_roseltorg", roseltorg_obj)
    parser_tender = ParserThread("parser_tender", tender_obj)
    parser_nelikvidy = ParserThread("parser_nelikvidi", nelikvidy_obj)
    parser_isource = ParserThread("parser_isource", isource_obj)
    parser_tectorg = ParserThread("parser_tectorg", tectorg_obj)
    parser_onlinecontract = ParserThread("parser_onlinecontract", onlinecontract_obj)


    #DEBUG OPTIONS
    #check_thread_1 = CheckThread('parser_roseltorg')
    #check_thread_1.start()

    parser_roseltorg.start()
    parser_nelikvidy.start()
    parser_tender.start()
    parser_isource.start()
    parser_tectorg.start()
    parser_onlinecontract.start()

    status = True

    while status:
        while True:
            try:
                request = requests.get("https://synrate.ru/api/ENGINE/list")

                json = (request.json()[0])
                status = json["status"]
                break
            except JSONDecodeError:
                print("Server restarting")
        if status:
            while True:
                try:
                    parser_list_request = requests.get("https://synrate.ru/api/parser/list")
                    parser_json = parser_list_request.json()
                    break
                except JSONDecodeError:
                    print("Sercer restarting")

            for json in parser_json:
                unique_code = json["unique_code"]
                p_status = json["status"]
                if unique_code == "parser_nelikvidy":
                    if p_status:
                        parser_nelikvidy.active = True
                    else:
                        parser_nelikvidy.active = False
                if unique_code == "parser_tender":
                    if p_status:
                        parser_tender.active = True
                    else:
                        #if parser_tender.active != False:
                        parser_tender.active = False
                if unique_code == "parser_roseltorg":
                    if p_status:
                        parser_roseltorg.active = True
                    else:
                        parser_roseltorg.active = False
                if unique_code == "parser_onlinecontract":
                    if p_status:
                        parser_onlinecontract.active = True
                    else:
                        parser_onlinecontract.active = False
                if unique_code == "parser_tectorg":
                    if p_status:
                        parser_tectorg.active = True
                    else:
                        parser_tectorg.active = False
                if unique_code == "parser_isource":
                    if p_status:
                        parser_isource.active = True
                    else:
                        parser_isource.active = False
        else:
            #check_thread_1.status = False
            parser_nelikvidy.status = False
            parser_tender.status = False
            parser_roseltorg.status = False
            parser_isource.status = False
            parser_tectorg.status = False
            parser_onlinecontract.status = False

    else:
        sys.exit()


if __name__ == '__main__':
    server_listener()
