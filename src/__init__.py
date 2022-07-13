import ccxt
import time
import datetime
import keyboard
import sys
from PyQt5 import uic
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtWidgets import QPushButton, QWidget, QComboBox,QTableWidgetItem, QProgressBar, QApplication, QHBoxLayout
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import timeit

# API키를 저장한 텍스트 파일 불러오기
with open("api.txt") as f:
    lines = f.readlines()
    api_key = lines[0].strip()
    secret = lines[1].strip()

# binance 객체 생성
binance = ccxt.binance(config={
    'apiKey': api_key,
    'secret': secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'delivery'
        # 'fetchMarkets' : 'inverse'
    }
})

#전역변수
global order
global order_num_list
global position
order_num_list = []
g_tick_data = 'ADA/USD' #현재 호가창 및 거래를 할 코인종류 전역변수

# 1 바이낸스 API 통신 세팅
markets = binance.load_markets()
binance.verbose = True

'''API메서드'''
class BinanceFunction():
    #현재가 조회
    def present_price(self):
        ticker = binance.fetch_ticker(g_tick_data)
        print(ticker['open'], ticker['high'], ticker['low'], ticker['close'])
        print('현재가 : ',ticker['close'])
        return ticker['close']

    #매수
    def buy_long(self):
        global position
        position = self.present_price()
        order = binance.create_order(g_tick_data, "limit", "buy", 1, price=position, params={})  #(코인 종류, 시장가or지정가, 포지션, 수량, 가격)
        order_num_list.append(order)
        print('매수전송', order)
       

    #매도
    def sell_short(self):
        global position
        position = self.present_price()
        order = binance.create_order(g_tick_data, "limit", "sell", 1, price=position, params={})  #(코인 종류, 시장가or지정가, 포지션, 수량, 가격)
        order_num_list.append(order)
        print('매도전송', order)

    #주문 취소
    def cancel_lifo_order(self):
        temp = order_num_list[(len(order_num_list))]
        order_id = temp['info']['orderId']
        order_cancel = binance.cancel_order(order_id, g_tick_data)
        order_num_list.pop()
        print('주문취소완료',order_cancel)

    def cancel_all_order(self):
        for i in range(len(order_num_list)):
            temp = order_num_list[i]
            order_id = temp['info']['orderId']
            order_cancel = binance.cancel_order(order_id, g_tick_data)
            print('주문 일괄취소 완료',order_cancel)
        order_num_list.clear()

    #잔고확인
    def balance(self):
        balance = binance.fetch_balance()
        return balance[g_tick_data.split('/')[0]]



''' 호가 쓰레드'''
class OrderbookWorker(QThread):
    dataSent = pyqtSignal(dict)

    def __init__(self, ticker):
        super().__init__()
        self.ticker = ticker
        self.alive = True

    def run(self):
        while self.alive:
            print('통신코인',g_tick_data)
            start_time = timeit.default_timer()
            data = binance.fetch_order_book(g_tick_data, limit=10)  #limit 변경시 2가지 변경, 1.pyqt사이즈 2.호가창 리셋for문
            terminate_time = timeit.default_timer()
            print("%f초 걸렸습니다." % (terminate_time - start_time))

            time.sleep(0.00001)
            self.dataSent.emit(data)

    def close(self):
        self.alive = False

# '''잔고 쓰레드'''
# class balanceWorker(QThread):
#     dataSent = pyqtSignal(dict)
#
#     def __init__(self):
#         super().__init__()
#
#     def run(self):
#         while self.alive:
#
#             time.sleep(0.05)
#             self.dataSent.emit(balance, ticker)
#
#     def close(self):
#         self.alive = False


''' 메인 프레임'''
class OrderbookWidget(QWidget,BinanceFunction):
    def __init__(self, parent=None, ticker="TRX/USD"):
        super().__init__(parent)
        uic.loadUi("mainUI.ui", self)
        self.ticker = ticker
        #item
        #코인 종류 고르는 매서드
        item_box = binance.symbols
        self.coin_box.addItems(item_box)

        #아이콘
        self.setWindowTitle("System Trading")
        self.setWindowIcon(QIcon("icon.png"))
        #배경색
        pal = QPalette()
        pal.setColor(QPalette.Background, QColor('#1C1C1C'))
        self.setAutoFillBackground(True)
        self.setPalette(pal)

        #테이블 배경색
          #매도테이블
        self.tableAsks.setStyleSheet("QTableWidget {\n"
                                       "color: #F7819F;"
                                       "background-color:rgb(28, 28, 28)\n"
                                       "  \n"
                                       "\n"
                                       "\n"
                                       "\n"
                                       "}")
          #매수테이블
        self.tableBids.setStyleSheet("QTableWidget {\n"
                                     "color: #58FA82;"
                                     "background-color:rgb(28, 28, 28)\n"
                                     "  \n"
                                     "\n"
                                     "\n"
                                     "\n"
                                     "}")

         '''매수, 매도 버튼 이벤트'''
        self.buy_present.setStyleSheet("background-color : #58FA82;") ##00FF00  "color: #FAFAFA;"
        self.buy_present.clicked.connect(self.buy_long)

        self.sell_present.setStyleSheet("background-color : #ff5522;")
        self.sell_present.clicked.connect(self.sell_short)

        '''취소 버튼 이벤트'''

        self.cancel_all.setStyleSheet("background-color : #ff7f50  ;")
        self.cancel_all.clicked.connect(self.cancel_all_order)

    # ----------------- 호가창 데이터 공간 세팅 ------------------
        for i in range(10):
            #  매도호가 : 2열데이터
            item_2 = QTableWidgetItem(str(""))
            item_2.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableAsks.setItem(i, 2, item_2)

            # 매도 물량 : 1열데이터
            item_1 = QTableWidgetItem(str(""))
            item_1.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tableAsks.setItem(i, 1, item_1)


            # 매수호가 : 2열데이터
            item_2 = QTableWidgetItem(str(""))
            item_2.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableBids.setItem(i, 2, item_2)
            # 매수물량 : 3열데이터
            item_3 = QTableWidgetItem(str(""))
            item_3.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.tableBids.setItem(i, 3, item_3)


        self.ow = OrderbookWorker(self.ticker)
        self.ow.dataSent.connect(self.updateData)
        self.ow.start()



    def updateData(self, data):

        global g_tick_data #전역변수로 설정하여 유동적으로 다른코인 호가창으로 변경가능
        g_tick_data = str(self.coin_box.currentText())

        for i, v in enumerate(data['asks'][::-1]): #매도 i= 0 매도 v= [2.13441, 311.0]
            item_2 = self.tableAsks.item(i, 2)
            item_2.setText(f"{v[0]:,}")
            item_1 = self.tableAsks.item(i, 1)
            item_1.setText(f"{v[1]:,}")

        for i, v in enumerate(data['bids']):
            item_2 = self.tableBids.item(i, 2)
            item_2.setText(f"{v[0]:,}")
            item_3 = self.tableBids.item(i, 3)
            item_3.setText(f"{v[1]:,}")


    def updataBalance(self, balance, ticker):
        free = str(balance[g_tick_data.split('/')[0]]['free'])
        used = str(balance[g_tick_data.split('/')[0]]['used'])
        total = str(balance[g_tick_data.split('/')[0]]['total'])
        coin_usd = str(int(balance[g_tick_data.split('/')[0]]['total']) * round(float(ticker['close']), 2))

        self.tableBalance.setItem(0, 0, QTableWidgetItem(free))
        self.tableBalance.setItem(0, 1, QTableWidgetItem(used))
        self.tableBalance.setItem(0, 2, QTableWidgetItem(total))
        self.tableBalance.setItem(0, 3, QTableWidgetItem(coin_usd))

    def closeEvent(self, event):
        self.ow.close()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    ow = OrderbookWidget()
    ow.show()
    exit(app.exec_())

