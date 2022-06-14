from parser_promportal import ParserPromportal
from parser_metaprom import ParserMetaprom
from parser_etp_aktiv import ParserEtpActiv
from parser_b2b_center import ParserCenter
from parser_fabrikant import ParserFabrikant
from parser_etpgpb import ParserEtpgpb
from parser_nelikvidy import ParserNelikvidy
from parser_prostanki import ProstankiParser
from parser_tenderpro import ParserTender
from parser_roseltorg import RoseltorgParser
from parser_isource import ParserSource
from parser_tektorg import ParserTektorg
from parser_onlinecontract import ParserOnlineContract
from threading import Thread
import time
import urllib3
import argparse
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


arg = argparse.ArgumentParser()
arg.add_argument("--m", default='long', help="full(long) parsing process or short parsing")
args = arg.parse_args()
mode = args.m
print(mode)


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
    if mode == 'short':
        print('server listener: Start.. Parsing mode - short')
        nelikvidy_obj = ParserNelikvidy(False, 300)
        tender_obj = ParserTender(12)
        roseltorg_obj = RoseltorgParser(10)
        prostanki_obj = ProstankiParser(5)
        isource_obj = ParserSource(10)
        tectorg_obj = ParserTektorg()
        onlinecontract_obj = ParserOnlineContract(125)
        etpgpb_obj = ParserEtpgpb(10)
        fabrikant_obj = ParserFabrikant(True, 10)
#        b2b_center_obj = ParserCenter(True, 10)
        etp_activ_obj = ParserEtpActiv(True, 120)
        metaprom_obj = ParserMetaprom(False, 3)
        promportal_obj = ParserPromportal(False, 2)

    else:
        print('server listener: Start.. Parsing mode - long')
        nelikvidy_obj = ParserNelikvidy(False, False)
        tender_obj = ParserTender(False)
        roseltorg_obj = RoseltorgParser(False)
        prostanki_obj = ProstankiParser(False)
        isource_obj = ParserSource(False)
        tectorg_obj = ParserTektorg()
        onlinecontract_obj = ParserOnlineContract(False)
        etpgpb_obj = ParserEtpgpb(False)
        fabrikant_obj = ParserFabrikant(True, False)
#        b2b_center_obj = ParserCenter(True, False)
        etp_activ_obj = ParserEtpActiv(True, False)
        metaprom_obj = ParserMetaprom(False, False)
        promportal_obj = ParserPromportal(False, False)

    parser_roseltorg = ParserThread("parser_roseltorg", roseltorg_obj)
    parser_tender = ParserThread("parser_tender", tender_obj)
    parser_nelikvidy = ParserThread("parser_nelikvidi", nelikvidy_obj)
    parser_isource = ParserThread("parser_isource", isource_obj)
    parser_tectorg = ParserThread("parser_tectorg", tectorg_obj)
    parser_onlinecontract = ParserThread("parser_onlinecontract", onlinecontract_obj)
    parser_etpgpb = ParserThread("parser_etpgpb", etpgpb_obj)
    parser_fabrikant = ParserThread("parser_fabrikant", fabrikant_obj)
#    parser_b2b_center = ParserThread("parser_b2b_cetner", b2b_center_obj)
    parser_etp_aktiv = ParserThread("parser_etp_aktiv", etp_activ_obj)
    parser_prostanki = ParserThread("parser_prostanki", prostanki_obj)
    parser_metaprom = ParserThread("parser_metaprom", metaprom_obj)
    parser_promportal = ParserThread("parser_promportal", promportal_obj)

    #DEBUG OPTIONS
    #check_thread_1 = CheckThread('parser_roseltorg')
    #check_thread_1.start()

    parser_roseltorg.start()
    parser_prostanki.start()
    parser_nelikvidy.start()
    parser_tender.start()
    parser_isource.start()
    # parser_tectorg.start()
    parser_onlinecontract.start()
    parser_etpgpb.start()
    parser_fabrikant.start()
#    parser_b2b_center.start()
    parser_etp_aktiv.start()
    parser_metaprom.start()
    parser_promportal.start()


if __name__ == '__main__':
    server_listener()
