class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()

        self._create_kiwoom_instance()

        self._set_signal_slots()

    def _create_kiwoom_instance(self):
        self.setControl(“KFOPENAPI.KFOpenAPICtrl.1”)

    def _set_signal_slots(self):
            self.OnEventConnect.connect(self._event_connect)

            self.OnReceiveTrData.connect(self._receive_tr_data)

    def comm_connect(self):
            self.dynamicCall(“CommConnect(int)”, 1)