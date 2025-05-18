import sys
import json
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox
from PyQt5.uic import loadUi
from datetime import datetime

URUNLER_DOSYASI = "urunler.json"
SIPARISLER_DOSYASI = "siparisler.json"

class Urun:
    def __init__(self, urun_id, urun_adi, fiyat, stok_adedi):
        self.urun_id = urun_id
        self.urun_adi = urun_adi
        self.fiyat = fiyat
        self.stok_adedi = stok_adedi

    def stok_guncelle(self, adet):
        if adet <= self.stok_adedi:
            self.stok_adedi -= adet
            return True
        return False

    def urun_bilgilerini_getir(self):
        return f"Urun ID: {self.urun_id}\nUrun Adi: {self.urun_adi}\nFiyat: {self.fiyat}\nStok Adedi: {self.stok_adedi}"

    def to_dict(self):
        return {
            "urun_id": self.urun_id,
            "urun_adi": self.urun_adi,
            "fiyat": self.fiyat,
            "stok_adedi": self.stok_adedi
        }

class Siparis:
    def __init__(self, siparis_id, urun, adet):
        self.siparis_id = siparis_id
        self.urun = urun
        self.adet = adet
        self.tarih = datetime.now()

    def toplam_fiyat(self):
        return self.urun.fiyat * self.adet

    def to_dict(self):
        return {
            "siparis_id": self.siparis_id,
            "urun_id": self.urun.urun_id,
            "adet": self.adet,
            "toplam_fiyat": self.toplam_fiyat(),
            "Siparis Tarih": self.tarih.strftime('%d %B %Y, %H:%M')
        }

class StokYonetimi(QDialog):
    def __init__(self):
        super().__init__()
        loadUi('stok.ui', self)
        self.urunler = self.urunleri_yukle()

        self.urun_bilgi.clicked.connect(self.urun_bilgisi_goster)
        self.islem_tam.clicked.connect(self.stok_guncelleme)
        self.sip_olustur.clicked.connect(self.siparis_olustur)
        self.fiyat_hesap.clicked.connect(self.fiyat_hesapla)

    def urunleri_yukle(self):
        try:
            with open(URUNLER_DOSYASI, "r") as f:
                urun_listesi = json.load(f)
                return [Urun(**urun) for urun in urun_listesi]
        except FileNotFoundError:
            QMessageBox.critical(self, "Hata", "Urunler dosyasi bulunamadi.")
            return []

    def urunleri_kaydet(self):
        with open(URUNLER_DOSYASI, "w") as f:
            json.dump([u.to_dict() for u in self.urunler], f, indent=4)

    def get_urun_by_id(self, urun_id):
        for urun in self.urunler:
            if urun.urun_id == urun_id:
                return urun
        return None

    def urun_bilgisi_goster(self):
        radio_button_urun_ids = {
            self.radio_televizyon: 101,
            self.radio_bilgisayar: 102,
            self.radio_tablet: 103,
            self.radio_telefon: 104,
            self.radio_saat: 105,
            self.radio_kulaklik: 106,
            self.radio_powerbank: 107,
            self.radio_playstation: 108,
            self.radio_mouse: 109
        }

        for radio, urun_id in radio_button_urun_ids.items():
            if radio.isChecked():
                urun = self.get_urun_by_id(urun_id)
                if urun:
                    QMessageBox.information(self, "Urun Bilgisi", urun.urun_bilgilerini_getir())
                    return

        QMessageBox.warning(self, "Uyari", "Lutfen bir urun seciniz.")

    def siparis_olustur(self):
        siparis_id = self.sip_bos.text()
        urun_id = self.urun_bos.text()
        adet = self.adet_bos.text()

        if siparis_id and urun_id and adet:
            if siparis_id.isdigit() and urun_id.isdigit() and adet.isdigit():
                siparis_id = int(siparis_id)
                urun_id = int(urun_id)
                adet = int(adet)

                urun = self.get_urun_by_id(urun_id)
                if urun:
                    if urun.stok_adedi >= adet:
                        try:
                            with open(SIPARISLER_DOSYASI, "r") as f:
                                siparisler = json.load(f)
                        except FileNotFoundError:
                            siparisler = []

                        if any(s["siparis_id"] == siparis_id for s in siparisler):
                            QMessageBox.warning(self, "Hata", f"{siparis_id} ID'li siparis zaten mevcut.")
                            return

                        siparis = Siparis(siparis_id, urun, adet)
                        urun.stok_adedi -= adet
                        self.urunleri_kaydet()

                        siparisler.append(siparis.to_dict())
                        with open(SIPARISLER_DOSYASI, "w") as f:
                            json.dump(siparisler, f, indent=4)

                        QMessageBox.information(self, "Siparis basarili",
                                                f"Siparisiniz basariyla olusturuldu.\nToplam Fiyat: {siparis.toplam_fiyat()} TL")
                    else:
                        QMessageBox.warning(self, "Hata", "Yeterli stok miktari yoktur.")
                else:
                    QMessageBox.warning(self, "Hata", "Girdiginiz ID'ye sahip urun yoktur.")
            else:
                QMessageBox.warning(self, "Hata", "Girdiginiz bilgilerin sadece rakamlardan olusması gerekmektedir.")
        else:
            QMessageBox.warning(self, "Hata", "Lutfen tum bilgileri eksiksiz giriniz.")

    def fiyat_hesapla(self):
        urun_id = self.urun_bos.text()
        adet = self.adet_bos.text()
        if urun_id.isdigit() and adet.isdigit():
            urun_id = int(urun_id)
            adet = int(adet)
            urun = self.get_urun_by_id(urun_id)
            if urun:
                toplam_fiyat = urun.fiyat * adet
                QMessageBox.information(self, "Toplam Fiyat", f"Toplam Fiyat: {toplam_fiyat} TL")
            else:
                QMessageBox.warning(self, "Hata", "Girdiginiz ID'ye sahip urun yoktur.")
        else:
            QMessageBox.warning(self, "Hata", "Girdiginiz bilgilerin sadece rakamlardan olusması gerekmektedir.")

    def stok_guncelleme(self):
        urun_id_text = self.urun_id.text()
        yeni_adet_text = self.stok_guncelle.text()

        if not urun_id_text or not yeni_adet_text:
            QMessageBox.warning(self, "Hata", "Lutfen urun ID ve yeni stok adetini giriniz.")
            return

        if not urun_id_text.isdigit() or not yeni_adet_text.isdigit():
            QMessageBox.warning(self, "Hata", "Urun ID ve stok adedi sadece rakamlardan olusmalidir.")
            return

        urun_id = int(urun_id_text)
        yeni_adet = int(yeni_adet_text)

        urun = self.get_urun_by_id(urun_id)
        if urun:
            urun.stok_adedi = yeni_adet
            self.urunleri_kaydet()
            QMessageBox.information(self, "Stok Guncelleme", f"Stok basariyla guncellendi.\nYeni stok: {urun.stok_adedi}")
        else:
            QMessageBox.warning(self, "Hata", "Girdiginiz ID'ye sahip urun bulunamadi.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StokYonetimi()
    window.setWindowTitle("Stok Takip Sistemi")
    window.show()
    sys.exit(app.exec_())
