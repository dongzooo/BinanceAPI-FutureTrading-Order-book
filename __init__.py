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

# 1 세팅
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
        # binance.create_order(코인 종류, 시장가or지정가, 포지션, 수량, 가격)
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
        # print(order['info']['orderId'])
        # order_id = order['info']['orderId']
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
        # print(balance.keys())
        # tmp = g_tick_data.split('/')[0]
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
            # balance = binance.fetch_balance()
            # ticker = binance.fetch_ticker(g_tick_data)
            data = binance.fetch_order_book(g_tick_data, limit=10)  #limit 변경시 2가지 변경, 1.pyqt사이즈 2.호가창 리셋for문
            # print('123',data)
            terminate_time = timeit.default_timer()
            print("%f초 걸렸습니다." % (terminate_time - start_time))

            # data  = pybithumb.get_orderbook(self.ticker, limit=10)
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
        uic.loadUi("untitled20.ui", self) #C:\ProgramData\Anaconda3\Lib\site-packages\PySide2
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





    # ----------------- 호가창 데이터 ------------------
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
        # tradingValues = []
        # for v in data['bids']:
        #     tradingValues.append(int(v[0] * v[1]))
        # maxTradingValue = max(tradingValues)
        global g_tick_data
        g_tick_data = str(self.coin_box.currentText())

        for i, v in enumerate(data['asks'][::-1]): #매도 i= 0 매도 v= [2.13441, 311.0]
            # print('매도 i=',i,'매도 v=',v)
            item_2 = self.tableAsks.item(i, 2)
            item_2.setText(f"{v[0]:,}")
            item_1 = self.tableAsks.item(i, 1)
            item_1.setText(f"{v[1]:,}")
            # item_2 = self.tableAsks.cellWidget(i, 2)
            # item_2.setRange(0, maxTradingValue)
            # item_2.setFormat(f"{tradingValues[i]:,}")
            # item_2.setValue(tradingValues[i])
            # if i ==49:
            #     print('통신끝')
            #     break

        for i, v in enumerate(data['bids']):
            # print('매수 i=', i, '매수 v=', v)
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

