##  바이낸스 코인선물 트레이딩 호가창(Binance API Future Trading Program)

바이낸스 선물 거래와 증권사 파생상품 거래도 하면서 거래량의 큰 차이가 안나는 데, 바이낸스 선물의 체결속도는 상대적으로 느리다고 인지됐다. 더 좋은 체결속도를 위해 API를 사용한 매매프로그램을 만들어야 겠다고 인지했다.

### 1. Purpose
- 바이낸스 선물 UI에 답답함을 느껴 한국의 HTS 파생선물 호가창과 동일한 UI로 구현
- 자동매매를 원하지만 주요 메서드를 모르는 투자자들을 위해 제공
- coin-m, usd-m 바이낸스 객체생성시 변경가능


### 2. UI Interface
----
![KakaoTalk_20220209_235029338](https://user-images.githubusercontent.com/40832965/153558802-e102a735-e89e-4f79-bb4d-29ef26cee503.png)
----

### 3. Demo VIdeo
 - UI밑에 검은 창은 바이낸스 창

https://user-images.githubusercontent.com/40832965/157466507-d5f65489-a3d6-42a5-9f29-00caeca9eb17.mp4


### 4. Overview
- 코인선물 설정 바에서 코인이름 선택하면 해당 코인 호가창출력
- 매수 버튼클릭 시 코인 1개 LONG 포지션
- 매도 버튼 클릭 시 코인 1개 SHORT 포지션
- 주문일괄취소 누르면 모든 주문 취소
- 자동매매를 만들고 싶다면 위 메서드를 활용하면 가능


### 5. Requirements
- binance 사이트에서 Future API 등록("api.txt" 파일 생성 후 저장)
- Python3, PYQT , QTdesigner




