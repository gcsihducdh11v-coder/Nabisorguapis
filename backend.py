# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, Response
import hashlib
import random
import json
from datetime import datetime, timedelta
import time

app = Flask(__name__)

# JSON yanıtlarında Türkçe karakter desteği
class UTF8JsonResponse(Response):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers['Content-Type'] = 'application/json; charset=utf-8'

def jsonify_utf8(*args, **kwargs):
    """Türkçe karakter desteği olan jsonify"""
    return app.response_class(
        json.dumps(dict(*args, **kwargs), ensure_ascii=False, indent=2),
        mimetype='application/json; charset=utf-8'
    )

# ========== TC DOĞRULAMA ALGORİTMASI ==========
def tc_dogrula(tc):
    """TC kimlik numarası doğrulama algoritması"""
    if not tc or len(tc) != 11 or not tc.isdigit() or tc[0] == '0':
        return False
    
    # Algoritma 1: 1,3,5,7,9. rakamların toplamı
    tekler = sum(int(tc[i]) for i in range(0, 9, 2))
    
    # Algoritma 2: 2,4,6,8. rakamların toplamı
    ciftler = sum(int(tc[i]) for i in range(1, 9, 2))
    
    # 10. rakam kontrolü
    if ((tekler * 7) - ciftler) % 10 != int(tc[9]):
        return False
    
    # 11. rakam kontrolü
    if (sum(int(tc[i]) for i in range(10)) % 10) != int(tc[10]):
        return False
    
    return True

# ========== TC'DEN KİŞİ BİLGİSİ ÜRETME ==========
def tcden_kisi_uret(tc):
    """TC'den deterministik ama benzersiz kişi bilgisi üretir"""
    
    # TC'yi seed olarak kullan
    seed = int(tc)
    random.seed(seed)
    
    # İsim listeleri (Türkçe karakterlerle)
    adlar = ["Ahmet", "Mehmet", "Ali", "Veli", "Mustafa", "Hasan", "Hüseyin", 
             "İbrahim", "Yusuf", "Murat", "Ömer", "Fatma", "Ayşe", "Zeynep", 
             "Emine", "Hatice", "Elif", "Merve", "Esra", "Selma", "Cem", "Can",
             "Burak", "Berke", "Deniz", "Eren", "Kaan", "Arda", "Emir", "Efe"]
    
    soyadlar = ["Yılmaz", "Kaya", "Demir", "Çelik", "Şahin", "Yıldız", "Arslan",
                "Koç", "Polat", "Kılıç", "Aksoy", "Erdoğan", "Öztürk", "Aydın",
                "Taş", "Kara", "Sarı", "Güneş", "Bulut", "Ateş", "Deniz", "Toprak"]
    
    sehirler = ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Adana", 
                "Konya", "Gaziantep", "Kayseri", "Mersin", "Eskişehir", "Trabzon",
                "Samsun", "Diyarbakır", "Erzurum", "Van", "Malatya", "Şanlıurfa"]
    
    ilceler = {
        "İstanbul": ["Kadıköy", "Beşiktaş", "Şişli", "Üsküdar", "Beyoğlu", "Fatih", "Bakırköy"],
        "Ankara": ["Çankaya", "Keçiören", "Yenimahalle", "Altındağ", "Mamak", "Etimesgut"],
        "İzmir": ["Karşıyaka", "Bornova", "Konak", "Buca", "Bayraklı", "Çiğli"],
        "Bursa": ["Osmangazi", "Yıldırım", "Nilüfer", "Gemlik", "İnegöl"],
        "Antalya": ["Muratpaşa", "Konyaaltı", "Kepez", "Alanya", "Manavgat"]
    }
    
    # TC'ye özel seçimler
    ad = adlar[seed % len(adlar)]
    soyad = soyadlar[(seed // 100) % len(soyadlar)]
    sehir = sehirler[(seed // 10000) % len(sehirler)]
    ilce = ilceler.get(sehir, ["Merkez"])[(seed // 1000) % len(ilceler.get(sehir, ["Merkez"]))]
    
    # Doğum yılı (1950-2005 arası)
    dogum_yili = 1950 + (seed % 56)
    
    # Doğum ayı ve günü
    dogum_ayi = (seed % 12) + 1
    dogum_gunu = (seed % 28) + 1
    
    # Cinsiyet (TC'nin son rakamı tek ise erkek, çift ise kadın)
    cinsiyet = "Erkek" if int(tc[-1]) % 2 == 1 else "Kadın"
    
    # Telefon numarası üret
    telefon = f"05{((seed % 90) + 10):02d}{seed % 10000:04d}{seed % 10000:04d}"
    
    # Anne adı
    anne_adlari = ["Fatma", "Ayşe", "Zeynep", "Emine", "Hatice", "Havva", "Meryem", "Şükran", "Gülşah"]
    anne_adi = anne_adlari[seed % len(anne_adlari)]
    
    # Baba adı
    baba_adlari = ["Mehmet", "Ali", "Mustafa", "Hasan", "Hüseyin", "İbrahim", "Osman", "Ramazan", "Yusuf"]
    baba_adi = baba_adlari[(seed // 100) % len(baba_adlari)]
    
    # Mahalle isimleri
    mahalleler = ["Atatürk", "Cumhuriyet", "İstiklal", "Zafer", "Barış", "Şehitler", "Bahçelievler",
                 "Yenişehir", "Çarşı", "Merkez", "Kültür", "Güzeltepe", "Çamlık", "Orhangazi"]
    
    mahalle = f"{mahalleler[seed % len(mahalleler)]} Mahallesi"
    
    random.seed()  # Seed'i sıfırla
    
    return {
        "tc": tc,
        "ad": ad,
        "soyad": soyad,
        "dogumTarihi": f"{dogum_gunu:02d}.{dogum_ayi:02d}.{dogum_yili}",
        "dogumYeri": sehir,
        "babaAdi": baba_adi,
        "anneAdi": anne_adi,
        "cinsiyet": cinsiyet,
        "il": sehir,
        "ilce": ilce,
        "mahalle": mahalle,
        "sokak": f"{['Atatürk', 'Cumhuriyet', 'İnönü', 'Fevzi Çakmak'][seed % 4]} Sokak",
        "kapiNo": str((seed % 99) + 1),
        "daireNo": str((seed % 20) + 1),
        "telefon": telefon,
        "_seed": seed  # Debug için
    }

# ========== ORTAK FONKSİYONLAR ==========
def kayit_bulunamadi():
    return jsonify_utf8({
        "status": "error",
        "message": "Kayıt bulunamadı veya geçersiz TC kimlik numarası.",
        "timestamp": datetime.now().isoformat()
    }), 404

def tarih_uret(tc, gun_fark=0):
    """TC'ye özel tarih üret"""
    seed = int(tc)
    tarih = datetime(2023, (seed % 12) + 1, (seed % 28) + 1)
    if gun_fark:
        tarih = tarih - timedelta(days=gun_fark)
    return tarih.strftime("%Y-%m-%d")

def tarih_saat_uret(tc):
    """TC'ye özel tarih-saat üret"""
    seed = int(tc)
    tarih = datetime(2023, (seed % 12) + 1, (seed % 28) + 1, 
                    (seed % 24), (seed % 60), (seed % 60))
    return tarih.strftime("%Y-%m-%dT%H:%M:%SZ")

# ========== API ENDPOINT'LERİ ==========

@app.route('/api/v1/nufus/sorgu', methods=['GET'])
def nufus_sorgu():
    tc = request.args.get('tc', '')
    
    if not tc_dogrula(tc):
        return kayit_bulunamadi()
    
    kisi = tcden_kisi_uret(tc)
    seed = int(tc)
    
    medeni_haller = ["Bekar", "Evli", "Dul", "Boşanmış"]
    
    response = {
        **kisi,
        "medeniHal": medeni_haller[seed % len(medeni_haller)],
        "postaKodu": f"34{(int(tc) % 900) + 100}",
        "kayitTarihi": tarih_uret(tc, 2000),
        "verildigiYer": f"{kisi['ilce']} Nüfus Müdürlüğü",
        "seriNo": f"A{int(tc) % 100000:05d}",
        "cuzdanNo": f"{int(tc) % 1000000:06d}",
        "sonGuncelleme": tarih_saat_uret(tc),
        "kayitDurumu": "Aktif",
        "verilisNedeni": "İlk Nüfus Cüzdanı",
        "kutukIl": kisi['il'],
        "kutukIlce": kisi['ilce'],
        "kutukMahalle": kisi['mahalle'],
        "ulus": "T.C. Vatandaşı",
        "dini": "İslam" if seed % 10 != 0 else "Belirtmek İstemiyor",
        "kanGrubu": ["A Rh+", "A Rh-", "B Rh+", "B Rh-", "0 Rh+", "0 Rh-", "AB Rh+", "AB Rh-"][seed % 8]
    }
    return jsonify_utf8(response)

@app.route('/api/v1/saglik/asi-kayitlari', methods=['GET'])
def asi_kayitlari():
    tc = request.args.get('tc', '')
    
    if not tc_dogrula(tc):
        return kayit_bulunamadi()
    
    kisi = tcden_kisi_uret(tc)
    seed = int(tc)
    
    asi_turleri = [
        "COVID-19 (BioNTech)", "COVID-19 (Sinovac)", "Tetanoz", 
        "Hepatit B", "Grip Aşısı", "Kızamık-Kabakulak-Kızamıkçık",
        "Suçiçeği", "Zatürre (Pnömokok)", "HPV Aşısı", "Menenjit Aşısı",
        "Kuduz Aşısı", "Tüberküloz Aşısı (BCG)"
    ]
    
    # TC'ye özel aşı kayıtları
    asi_sayisi = (seed % 5) + 3  # 3-7 arası aşı
    asi_kayitlari = []
    
    for i in range(asi_sayisi):
        asi_adi = asi_turleri[(seed + i*7) % len(asi_turleri)]
        asi_kayitlari.append({
            "asiAdi": asi_adi,
            "doz": (i % 3) + 1,
            "tarih": tarih_uret(tc, (i+1)*45),
            "saglikMerkezi": f"{kisi['il']} Aile Sağlığı Merkezi",
            "lotNo": f"LOT{(seed + i) % 10000:04d}",
            "uygulayan": f"Dr. {['Ahmet', 'Mehmet', 'Ayşe', 'Fatma'][(seed+i) % 4]} {['Yılmaz', 'Kaya', 'Demir', 'Çelik'][(seed+i) % 4]}",
            "uygulamaYeri": ["Sol Kol", "Sağ Kol", "Kalçadan"][(seed+i) % 3],
            "saglikPersonelNo": f"SH{(seed + i) % 10000:05d}"
        })
    
    response = {
        **kisi,
        "asiKayitlari": asi_kayitlari,
        "toplamAsiSayisi": asi_sayisi,
        "sonAsiTarihi": asi_kayitlari[-1]["tarih"] if asi_kayitlari else None,
        "asiKartNo": f"AS{seed % 100000:06d}",
        "sorguTarihi": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "saglikGuvencesi": "Genel Sağlık Sigortası",
        "aileHekimi": f"Dr. {['Ali', 'Veli', 'Zeynep', 'Elif'][seed % 4]} {['Yıldız', 'Şahin', 'Arslan'][seed % 3]}",
        "aileHekimiTel": f"0{((seed % 90) + 10):02d} {((seed % 900) + 100):03d} {seed % 10000:04d}",
        "asiTakipSistemi": "Merkezi Aşı Takip Sistemi (MATS)",
        "uyari": "Bir sonraki aşı tarihiniz için aile hekiminize başvurunuz."
    }
    return jsonify_utf8(response)

@app.route('/api/v1/saglik/rontgen-listesi', methods=['GET'])
def rontgen_listesi():
    tc = request.args.get('tc', '')
    
    if not tc_dogrula(tc):
        return kayit_bulunamadi()
    
    # Gerçekçi gecikme
    time.sleep(random.uniform(0.2, 0.7))
    
    kisi = tcden_kisi_uret(tc)
    seed = int(tc)
    
    tetkik_turleri = [
        "Akciğer Röntgeni (PA)", "Akciğer Röntgeni (Lateral)",
        "Batın Grafisi", "El Bileği Röntgeni", "Ayak Bileği Röntgeni",
        "Beyin MR", "Bel MR", "Diz MR", "Boyun MR", "Kalp EKO",
        "Karın USG", "Tiroid USG", "Mamografi", "Diş Panoramik Röntgen"
    ]
    
    sonuclar = [
        "Normal sınırlarda", "Minimal patoloji", "Hafif dejeneratif değişiklikler",
        "Akciğer parankim alanlarında minimal fibrotik değişiklikler",
        "Kemik yapılarda osteoporotik değişiklikler",
        "Patoloji saptanmadı", "Hafif osteoartrit bulguları",
        "Minimal plevral kalınlaşma", "Normal anatomik yapı"
    ]
    
    hastaneler = [
        f"{kisi['il']} Eğitim ve Araştırma Hastanesi",
        f"Özel {kisi['il']} Medicalpark Hastanesi",
        f"{kisi['il']} Devlet Hastanesi",
        f"{kisi['il']} Üniversitesi Hastanesi",
        f"{kisi['il']} Şehir Hastanesi",
        f"Özel {kisi['il']} Anadolu Hastanesi"
    ]
    
    tetkik_sayisi = (seed % 4) + 2  # 2-5 tetkik
    tetkikler = []
    
    for i in range(tetkik_sayisi):
        tetkik_turu = tetkik_turleri[(seed + i*11) % len(tetkik_turleri)]
        doktor_adi = ['Ali', 'Veli', 'Ayşe', 'Fatma', 'Zeynep', 'Mehmet'][(seed+i) % 6]
        doktor_soyadi = ['Yıldız', 'Şahin', 'Demir', 'Çelik', 'Arslan', 'Koç'][(seed+i) % 6]
        
        tetkikler.append({
            "tetkikId": f"TET-2023-{seed % 10000:04d}{i}",
            "tetkikTuru": tetkik_turu,
            "tarih": tarih_uret(tc, (i+1)*60),
            "saat": f"{(seed % 12) + 8:02d}:{seed % 60:02d}",
            "sonuc": sonuclar[(seed + i*13) % len(sonuclar)],
            "aciklama": f"{kisi['ad']} {kisi['soyad']} için yapılan {tetkik_turu.lower()} tetkiki normal sınırlardadır.",
            "kurum": hastaneler[(seed + i*17) % len(hastaneler)],
            "doktor": f"Dr. {doktor_adi} {doktor_soyadi}",
            "doktorBrans": ["Radyoloji", "Nöroradyoloji", "Ortopedi", "Kardiyoloji", "Genel Cerrahi"][(seed+i) % 5],
            "bolum": ["Radyoloji", "Görüntüleme Merkezi", "MR Ünitesi", "Tomografi Ünitesi"][(seed+i) % 4],
            "goruntuNo": f"IMG-{(seed + i) % 1000000:06d}",
            "raporNo": f"RAP-2023-{(seed + i) % 10000:04d}",
            "isteyenDoktor": f"Dr. {['Ahmet', 'Mehmet', 'Ayşe'][(seed+i) % 3]} {['Yılmaz', 'Kaya'][(seed+i) % 2]}",
            "tetkikNotu": "Tetkik hastanın onamı alınarak yapılmıştır."
        })
    
    response = {
        **kisi,
        "hastaNo": f"HST-{seed % 10000:04d}",
        "tetkikler": tetkikler,
        "toplamTetkik": tetkik_sayisi,
        "sonTetkikTarihi": tetkikler[-1]["tarih"] if tetkikler else None,
        "raporDurumu": "Tüm raporlar tamamlandı",
        "saglikKurumu": hastaneler[seed % len(hastaneler)],
        "sorguZamani": datetime.now().isoformat(),
        "saglikBilgiSistemi": "Merkezi Hastane Randevu Sistemi (MHRS)",
        "uyari": "Raporlarınızı saklayınız, kontrol için yanınızda bulundurunuz."
    }
    return jsonify_utf8(response)

@app.route('/api/v1/eczane/recete-gecmisi', methods=['GET'])
def recete_gecmisi():
    tc = request.args.get('tc', '')
    
    if not tc_dogrula(tc):
        return kayit_bulunamadi()
    
    kisi = tcden_kisi_uret(tc)
    seed = int(tc)
    
    ilaclar = [
        {"ad": "PAROL 500 mg", "kutu": "20 tablet", "kullanim": "Günde 3x1", "etkenMadde": "Parasetamol"},
        {"ad": "MAJEZİK", "kutu": "12 tablet", "kullanim": "Gerektiğinde 1", "etkenMadde": "Tiyoprofenik asit"},
        {"ad": "VENTOLİN 100 mcg", "kutu": "200 doz", "kullanim": "Günde 2x2", "etkenMadde": "Salbutamol"},
        {"ad": "CORASPİN 100 mg", "kutu": "30 tablet", "kullanim": "Günde 1x1", "etkenMadde": "Asetilsalisilik asit"},
        {"ad": "ATECOR 10 mg", "kutu": "28 tablet", "kullanim": "Günde 1x1", "etkenMadde": "Atorvastatin"},
        {"ad": "CRESTOR 20 mg", "kutu": "28 tablet", "kullanim": "Günde 1x1", "etkenMadde": "Rosuvastatin"},
        {"ad": "ARVELES 25 mg", "kutu": "20 tablet", "kullanim": "Gerektiğinde 1", "etkenMadde": "Dexketoprofen"},
        {"ad": "AUGMENTİN 1g", "kutu": "14 tablet", "kullanim": "Günde 2x1", "etkenMadde": "Amoksisilin/Klavulanat"},
        {"ad": "ZİNCO 15 mg", "kutu": "30 kapsül", "kullanim": "Günde 1x1", "etkenMadde": "Çinko"},
        {"ad": "BEREKET VİTAMİN", "kutu": "30 tablet", "kullanim": "Günde 1x1", "etkenMadde": "Multivitamin"}
    ]
    
    eczaneler = [
        f"{kisi['ilce']} Merkez Eczanesi",
        f"{kisi['ilce']} Sağlık Eczanesi",
        f"{kisi['ilce']} 24 Saat Eczanesi",
        f"{kisi['il']} Eczanesi",
        f"{kisi['mahalle']} Eczanesi",
        f"Özel {kisi['ilce']} Eczanesi"
    ]
    
    recete_sayisi = (seed % 4) + 2  # 2-5 reçete
    receteler = []
    toplam_tutar = 0
    
    for i in range(recete_sayisi):
        ilac_sayisi = (seed % 3) + 2  # 2-4 ilaç
        secilen_ilaclar = [ilaclar[(seed + i*7 + j) % len(ilaclar)] for j in range(ilac_sayisi)]
        
        recete_tutar = sum([((seed + i + j) % 50) + 20 for j in range(ilac_sayisi)])
        toplam_tutar += recete_tutar
        
        doktor_brans = ["Dahiliye", "Kardiyoloji", "Genel Cerrahi", "Aile Hekimliği", "Kulak Burun Boğaz", "Göz Hastalıkları"][(seed+i) % 6]
        
        receteler.append({
            "receteNo": f"2023-{seed % 1000000:06d}{i}",
            "tarih": tarih_uret(tc, (i+1)*45),
            "durum": "Kullanıldı",
            "doktor": {
                "adi": f"Dr. {['Ahmet', 'Mehmet', 'Ayşe', 'Fatma', 'Zeynep'][(seed+i) % 5]}",
                "soyadi": ["Yılmaz", "Kaya", "Demir", "Çelik", "Şahin"][(seed+i) % 5],
                "uzmanlik": doktor_brans,
                "hastane": f"{kisi['il']} {doktor_brans} Hastanesi",
                "sicilNo": f"DR-{(seed + i) % 10000:05d}"
            },
            "ilaclar": secilen_ilaclar,
            "eczane": {
                "adi": eczaneler[(seed + i*11) % len(eczaneler)],
                "telefon": f"0{((seed % 90) + 10):02d} {((seed % 900) + 100):03d} {(seed + i) % 10000:04d}",
                "adres": f"{kisi['ilce']} {kisi['mahalle']} Sokak No:{((seed + i) % 50) + 1}",
                "eczaci": f"Ecz. {['Ali', 'Veli', 'Ayşe'][(seed+i) % 3]} {['Yıldız', 'Kaya'][(seed+i) % 2]}",
                "eczaciSicilNo": f"ECZ-{(seed + i) % 10000:05d}"
            },
            "toplamTutar": f"{recete_tutar:.2f} TL",
            "sgkKatki": f"{(recete_tutar * 0.7):.2f} TL",
            "hastaKatki": f"{(recete_tutar * 0.3):.2f} TL",
            "receteTipi": ["Normal", "Yeşil", "Kırmızı", "Turuncu"][(seed+i) % 4],
            "teslimTarihi": tarih_uret(tc, (i+1)*45 - 1),
            "receteBarkod": f"RB{(seed + i) % 100000000000:012d}"
        })
    
    response = {
        **kisi,
        "receteler": receteler,
        "sonUcAyReceteSayisi": recete_sayisi,
        "toplamHarcama": f"{toplam_tutar:.2f} TL",
        "sgkToplamKatki": f"{(toplam_tutar * 0.7):.2f} TL",
        "hastaToplamKatki": f"{(toplam_tutar * 0.3):.2f} TL",
        "sonSorgulama": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "saglikGuvencesi": "SGK (Genel Sağlık Sigortası)",
        "receteTakipNo": f"RT{seed % 100000000:09d}",
        "uyari": "Reçetelerinizi saklayınız, ilaçlarınızı doktorunuzun önerdiği şekilde kullanınız."
    }
    return jsonify_utf8(response)

@app.route('/api/v1/adli-sicil/kayit', methods=['GET'])
def adli_sicil():
    tc = request.args.get('tc', '')
    
    if not tc_dogrula(tc):
        return kayit_bulunamadi()
    
    time.sleep(random.uniform(0.4, 1.0))
    
    kisi = tcden_kisi_uret(tc)
    seed = int(tc)
    
    # TC son rakamına göre sicil durumu
    if int(tc[-1]) % 3 == 0:
        durum = "TEMİZ"
        aciklama = "Herhangi bir mahkumiyet kaydı bulunmamaktadır."
        kayitlar = []
    elif int(tc[-1]) % 3 == 1:
        durum = "KAYITLI (Hafif)"
        aciklama = "Küçük trafik cezaları mevcuttur."
        kayitlar = [{
            "tip": "Trafik Cezası",
            "tarih": tarih_uret(tc, 180),
            "aciklama": "Hız sınırı ihlali - 25 km/h fazla",
            "ceza": "350 TL",
            "durum": "Ödendi",
            "mahkeme": f"{kisi['il']} Trafik Mahkemesi",
            "dosyaNo": f"2023/TF-{seed % 1000:04d}"
        }]
    else:
        durum = "KAYITLI (Orta)"
        aciklama = "Trafik ve küçük kabahatler mevcuttur."
        kayitlar = [
            {
                "tip": "Trafik Cezası",
                "tarih": tarih_uret(tc, 120),
                "aciklama": "Park yasağı ihlali",
                "ceza": "150 TL",
                "durum": "Ödendi",
                "mahkeme": f"{kisi['il']} Trafik Mahkemesi",
                "dosyaNo": f"2023/TF-{(seed + 1) % 1000:04d}"
            },
            {
                "tip": "Kabahat",
                "tarih": tarih_uret(tc, 300),
                "aciklama": "Gürültü yapma",
                "ceza": "250 TL",
                "durum": "Ödendi",
                "mahkeme": f"{kisi['ilce']} Sulh Ceza Mahkemesi",
                "dosyaNo": f"2022/KB-{seed % 1000:04d}"
            }
        ]
    
    sorgu_gecmisi = []
    if seed % 2 == 0:
        sorgu_gecmisi.append({
            "tarih": tarih_uret(tc, 90),
            "amac": "İş başvurusu",
            "sorgulayan": f"{['ABC', 'XYZ', 'TECH', 'GLOBAL'][seed % 4]} Şirketi",
            "sonuc": "Olumlu",
            "sorguKodu": f"SORG-2023-{seed % 1000:03d}"
        })
    
    if seed % 3 == 0:
        sorgu_gecmisi.append({
            "tarih": tarih_uret(tc, 180),
            "amac": "Vize başvurusu",
            "sorgulayan": "Almanya Konsolosluğu",
            "sonuc": "Olumlu",
            "sorguKodu": f"VİZE-2023-{seed % 1000:03d}"
        })
    
    response = {
        **kisi,
        "sicilNo": f"ADS-{kisi['il'][:3].upper()}-2023-{seed % 1000:03d}",
        "kayitDurumu": durum,
        "aciklama": aciklama,
        "kayitlar": kayitlar,
        "sorguGecmisi": sorgu_gecmisi,
        "sonSorguTarihi": tarih_uret(tc, seed % 30),
        "sorguMercii": f"{kisi['il']} Adli Sicil ve İstatistik Müdürlüğü",
        "belgeNo": f"2023/BS-{seed % 10000:04d}",
        "gecerlilikSuresi": "90 gün",
        "verilisTarihi": datetime.now().strftime("%d.%m.%Y"),
        "sistemMesaji": "Bu belge elektronik imza ile onaylanmıştır.",
        "guvenlikKodu": f"GKO-{hashlib.md5(tc.encode()).hexdigest()[:8].upper()}",
        "uyari": "Bu belge resmi kurumlarca 90 gün süreyle geçerlidir."
    }
    return jsonify_utf8(response)

@app.route('/api/v1/pasaport/sorgu', methods=['GET'])
def pasaport_sorgu():
    tc = request.args.get('tc', '')
    
    if not tc_dogrula(tc):
        return kayit_bulunamadi()
    
    kisi = tcden_kisi_uret(tc)
    seed = int(tc)
    
    # Pasaport tipi belirleme
    pasaport_tipleri = [
        {"tip": "Umuma Mahsus (Bordo)", "kod": "P"},
        {"tip": "Hususi (Yeşil)", "kod": "G"},
        {"tip": "Hizmet (Gri)", "kod": "S"},
        {"tip": "Diplomatik (Siyah)", "kod": "D"}
    ]
    
    secilen_tip = pasaport_tipleri[seed % len(pasaport_tipleri)]
    
    # Seyahat geçmişi
    ulkeler = ["Almanya", "Fransa", "Hollanda", "İtalya", "İspanya", "Yunanistan", "ABD", "İngiltere", "Japonya"]
    sehirler = ["Berlin", "Paris", "Amsterdam", "Roma", "Barcelona", "Atina", "New York", "Londra", "Tokyo"]
    
    seyahat_sayisi = (seed % 4) + 1  # 1-4 seyahat
    seyahat_kayitlari = []
    
    for i in range(seyahat_sayisi):
        ulke = ulkeler[(seed + i*5) % len(ulkeler)]
        seyahat_kayitlari.append({
            "ulke": ulke,
            "giris": tarih_uret(tc, (i+1)*90),
            "cikis": tarih_uret(tc, (i+1)*90 - 7),
            "sehir": sehirler[(seed + i*5) % len(sehirler)],
            "amac": ["Turizm", "İş", "Eğitim", "Aile Ziyareti"][(seed+i) % 4],
            "sure": "7 gün"
        })
    
    # Vize bilgileri
    vize_bilgileri = []
    if seed % 3 != 0:  # %66 ihtimal vize
        vize_ulkeler = ["ABD", "İngiltere", "Kanada", "Avustralya", "Japonya", "Çin"]
        vize_bilgileri.append({
            "ulke": vize_ulkeler[seed % len(vize_ulkeler)],
            "tip": ["B1/B2", "Turist", "Öğrenci", "İş"][seed % 4],
            "baslangic": tarih_uret(tc, 200),
            "bitis": tarih_uret(tc, -365*5),  # 5 yıl sonra
            "durum": "Aktif",
            "vizeNo": f"VZ{seed % 100000000:09d}",
            "girisHakki": "Çoklu giriş"
        })
    
    response = {
        **kisi,
        "pasaportNo": f"{secilen_tip['kod']}{seed % 100000000:08d}",
        "tip": secilen_tip["tip"],
        "verilisTarihi": tarih_uret(tc, 300),
        "sonGecerlilikTarihi": tarih_uret(tc, -365*5),  # 5 yıl ileri
        "verilenYer": f"{kisi['il']} İl Göç İdaresi Müdürlüğü",
        "verenAmir": f"Şube Müdürü {['Ahmet', 'Mehmet', 'Ayşe'][seed % 3]} {['Yılmaz', 'Kaya'][seed % 2]}",
        "durum": "AKTİF",
        "seyahatKayitlari": seyahat_kayitlari,
        "vizeBilgileri": vize_bilgileri,
        "toplamSeyahat": seyahat_sayisi,
        "kayipCaldirmaDurumu": "Yok",
        "kayipCaldirmaTarihi": None,
        "sonGuncelleme": tarih_saat_uret(tc),
        "pasaportSeriNo": f"PS{seed % 100000:06d}",
        "uyruk": "T.C.",
        "davetliUlke": None,
        "pasaportResimNo": f"PR{(seed % 1000000):06d}",
        "uyari": "Pasaportunuzun geçerlilik süresini takip ediniz."
    }
    return jsonify_utf8(response)

@app.route('/api/v1/ehliyet/sorgu', methods=['GET'])
def ehliyet_sorgu():
    tc = request.args.get('tc', '')
    
    if not tc_dogrula(tc):
        return kayit_bulunamadi()
    
    kisi = tcden_kisi_uret(tc)
    seed = int(tc)
    
    siniflar = [
        {"kod": "A1", "aciklama": "Motor (125 cc'ye kadar)"},
        {"kod": "A2", "aciklama": "Motor (35 kW'ya kadar)"},
        {"kod": "B", "aciklama": "Otomobil, Kamyonet"},
        {"kod": "C", "aciklama": "Kamyon"},
        {"kod": "D", "aciklama": "Otobüs"},
        {"kod": "E", "aciklama": "Römorklu Araçlar"},
        {"kod": "F", "aciklama": "Traktör"}
    ]
    
    # TC'ye özel sınıflar seç
    secilen_sinif_sayisi = (seed % 3) + 1  # 1-3 sınıf
    secilen_siniflar = [sinifler[(seed + i) % len(siniflar)] for i in range(secilen_sinif_sayisi)]
    
    kan_gruplari = ["A Rh+", "A Rh-", "B Rh+", "B Rh-", "0 Rh+", "0 Rh-", "AB Rh+", "AB Rh-"]
    
    ceza_puani = seed % 20  # 0-19 arası
    if ceza_puani > 10:
        durum = "ASKIDA"
        durum_aciklama = "Ceza puanı sınırı aşıldı"
    else:
        durum = "AKTİF"
        durum_aciklama = "Ehliyet kullanılabilir"
    
    cezalar = []
    if seed % 4 != 0:  # %75 ihtimal ceza
        ceza_tipleri = ["Hız İhlali", "Park İhlali", "Emniyet Kemeri", "Kırmızı Işık", "Alkollü Araç Kullanma"]
        for i in range((seed % 3) + 1):  # 1-3 ceza
            cezalar.append({
                "tip": ceza_tipleri[(seed + i) % len(ceza_tipleri)],
                "tarih": tarih_uret(tc, (i+1)*30),
                "puan": (i+1)*5,
                "tutar": f"{(seed % 500) + 100} TL",
                "durum": "Ödendi" if (seed + i) % 2 == 0 else "Ödenmedi",
                "plaka": f"34{chr(65 + (seed % 26))}{chr(65 + ((seed//26) % 26))} {seed % 1000:03d}"
            })
    
    response = {
        **kisi,
        "ehliyetNo": f"E{seed % 10000000000:011d}",
        "sinif": secilen_siniflar,
        "verilisTarihi": tarih_uret(tc, 365*3),  # 3 yıl önce
        "ilkVerilisTarihi": tarih_uret(tc, 365*8),  # 8 yıl önce
        "sonGecerlilikTarihi": tarih_uret(tc, -365*5),  # 5 yıl sonra
        "verildigiYer": f"{kisi['il']} İl Emniyet Müdürlüğü Trafik Şubesi",
        "kanGrubu": kan_gruplari[seed % len(kan_gruplari)],
        "cezaPuani": ceza_puani,
        "cezalar": cezalar,
        "durum": durum,
        "durumAciklama": durum_aciklama,
        "kayipCaldirma": "Yok",
        "kayipCaldirmaTarihi": None,
        "saglikRaporuGecerlilik": tarih_uret(tc, -365*2),  # 2 yıl sonra
        "saglikRaporuNo": f"SR{seed % 100000:06d}",
        "fotoGuncellemeTarihi": tarih_uret(tc, 180),
        "ehliyetTeslimTarihi": tarih_uret(tc, 365*3 - 7),
        "dogrulamaKodu": f"EHL-{hashlib.md5(tc.encode()).hexdigest()[:6].upper()}",
        "uyari": f"Ceza puanınız: {ceza_puani}/20. 20 puana ulaşıldığında ehliyetiniz askıya alınacaktır."
    }
    return jsonify_utf8(response)

# ========== DİĞER API'LER (KISA VERSİYONLAR) ==========

@app.route('/api/v1/saglik/kronik-hastalik', methods=['GET'])
def kronik_hastalik():
    tc = request.args.get('tc', '')
    if not tc_dogrula(tc): return kayit_bulunamadi()
    
    kisi = tcden_kisi_uret(tc)
    seed = int(tc)
    
    hastaliklar = [
        {"ad": "Hipertansiyon", "teshisTarihi": "2021-03-15", "durum": "Kontrollü", "ilac": "Concor 5 mg"},
        {"ad": "Tip 2 Diyabet", "teshisTarihi": "2020-08-20", "durum": "Diyet ile kontrol", "ilac": "Metformin 850 mg"},
        {"ad": "Astım", "teshisTarihi": "2019-05-10", "durum": "Ara sıra", "ilac": "Ventolin"},
        {"ad": "Migren", "teshisTarihi": "2018-11-30", "durum": "İlaçlı kontrol", "ilac": "Maxalt"},
        {"ad": "Kolesterol Yüksekliği", "teshisTarihi": "2022-01-15", "durum": "İzlemde", "ilac": "Crestor 10 mg"}
    ]
    
    secilen_hastaliklar = [hastaliklar[i % len(hastaliklar)] for i in range(seed % 3)]  # 0-2 hastalık
    
    return jsonify_utf8({
        **kisi,
        "hastaliklar": secilen_hastaliklar,
        "sonKontrol": tarih_uret(tc, seed % 100),
        "birSonrakiKontrol": tarih_uret(tc, -30),
        "kronikHastalikKartNo": f"KH{seed % 100000:06d}",
        "takipMerkezi": f"{kisi['il']} Endokrinoloji Merkezi"
    })

@app.route('/api/v1/vergi/borc-sorgu', methods=['GET'])
def vergi_borc():
    tc = request.args.get('tc', '')
    if not tc_dogrula(tc): return kayit_bulunamadi()
    
    kisi = tcden_kisi_uret(tc)
    seed = int(tc)
    
    borc = (seed % 5000) + 100  # 100-5100 TL arası
    
    return jsonify_utf8({
        **kisi,
        "vergiNo": f"{seed % 1000000000:010d}",
        "toplamBorc": f"{borc:,} TL".replace(",", "."),
        "borcDetay": [
            {"tur": "Gelir Vergisi", "tutar": f"{borc * 0.7:,.2f} TL".replace(",", "."), "sonOdeme": tarih_uret(tc, -30)},
            {"tur": "MTV", "tutar": f"{borc * 0.3:,.2f} TL".replace(",", "."), "sonOdeme": tarih_uret(tc, -60)},
            {"tur": "KDV", "tutar": f"{borc * 0.2:,.2f} TL".replace(",", "."), "sonOdeme": tarih_uret(tc, -15)}
        ],
        "odenen": f"{(seed % borc):,} TL".replace(",", ".") if seed % 3 != 0 else "0,00 TL",
        "faiz": f"{(borc * 0.1):.2f} TL" if seed % 2 == 1 else "0,00 TL",
        "faizDurumu": "Faiz işlemi başlamadı" if seed % 2 == 0 else f"{(borc * 0.1):.2f} TL faiz işledi",
        "vergiDairesi": f"{kisi['il']} Vergi Dairesi Müdürlüğü",
        "hesapNo": f"VH{seed % 1000000:07d}"
    })

@app.route('/api/v1/tapu/gayrimenkul', methods=['GET'])
def gayrimenkul():
    tc = request.args.get('tc', '')
    if not tc_dogrula(tc): return kayit_bulunamadi()
    
    kisi = tcden_kisi_uret(tc)
    seed = int(tc)
    
    gayrimenkul_tipleri = ["Daire", "Arsa", "Tarla", "Dükkan", "Depo", "Ofis", "Villa"]
    tip = gayrimenkul_tipleri[seed % len(gayrimenkul_tipleri)]
    
    return jsonify_utf8({
        **kisi,
        "gayrimenkulListe": [{
            "tip": tip,
            "ada": str((seed % 100) + 1),
            "parsel": str((seed % 1000) + 1),
            "pafta": f"{(seed % 50) + 1}",
            "alan": f"{(seed % 500) + 50} m²",
            "il": kisi['il'],
            "ilce": kisi['ilce'],
            "mahalle": kisi['mahalle'],
            "tapuTarihi": tarih_uret(tc, seed % 1000),
            "tapuBedeli": f"{(seed % 1000000) + 50000:,} TL".replace(",", "."),
            "ipotek": "Yok" if seed % 3 == 0 else "Var",
            "ipotekTutari": f"{(seed % 500000) + 10000:,} TL".replace(",", ".") if seed % 3 != 0 else None,
            "tapuNo": f"TP{seed % 1000000:07d}",
            "ciltNo": f"{(seed % 100) + 1}",
            "sayfaNo": f"{(seed % 500) + 1}"
        }] if seed % 5 != 0 else [],  # %80 ihtimal gayrimenkul
        "toplamGayrimenkul": 1 if seed % 5 != 0 else 0,
        "tapuGenelMudurluk": f"{kisi['il']} Tapu ve Kadastro Müdürlüğü"
    })

@app.route('/api/v1/askerlik/durum', methods=['GET'])
def askerlik():
    tc = request.args.get('tc', '')
    if not tc_dogrula(tc): return kayit_bulunamadi()
    
    kisi = tcden_kisi_uret(tc)
    seed = int(tc)
    
    yas = 2023 - int(kisi['dogumTarihi'].split('.')[-1])
    
    if kisi['cinsiyet'] == 'Kadın':
        durum = "Muaf"
        aciklama = "Kadın askerlik yükümlülüğü bulunmamaktadır."
    elif yas < 20:
        durum = "Tecil"
        aciklama = "Yaş sebebiyle tecilli"
    elif yas > 41:
        durum = "Muaf"
        aciklama = "Yaş haddinden muaf"
    elif seed % 4 == 0:
        durum = "Yapıldı"
        aciklama = "Askerlik görevini tamamladı"
    elif seed % 4 == 1:
        durum = "Tecil"
        aciklama = "Yüksek öğrenim sebebiyle tecilli"
    elif seed % 4 == 2:
        durum = "Yapılmadı"
        aciklama = "Askerlik görevi bekliyor"
    else:
        durum = "Muaf"
        aciklama = "Sağlık sebebiyle muaf"
    
    return jsonify_utf8({
        **kisi,
        "durum": durum,
        "aciklama": aciklama,
        "tecilBitis": tarih_uret(tc, -365) if durum == "Tecil" else None,
        "birlik": ["2. Kolordu", "3. Kolordu", "Eğitim Tugayı", "Piyade Alayı"][seed % 4] if durum == "Yapıldı" else None,
        "sicilNo": f"ASK-{seed % 10000:05d}" if durum == "Yapıldı" else None,
        "terhisTarihi": tarih_uret(tc, 365*2) if durum == "Yapıldı" else None,
        "askerlikSube": f"{kisi['il']} Askerlik Şubesi Başkanlığı",
        "saglikDurumu": ["Elverişli", "Geçici Elverişsiz", "Elverişsiz"][seed % 3],
        "sinif": ["Yok", "1. Sınıf", "2. Sınıf"][seed % 3],
        "kayitNo": f"AK{seed % 100000:06d}"
    })

@app.route('/api/v1/ibb/su-fatura', methods=['GET'])
def su_fatura():
    tc = request.args.get('tc', '')
    if not tc_dogrula(tc): return kayit_bulunamadi()
    
    kisi = tcden_kisi_uret(tc)
    seed = int(tc)
    
    tutar = (seed % 300) + 50  # 50-350 TL
    
    return jsonify_utf8({
        **kisi,
        "aboneNo": f"SU-IST-{seed % 100000:06d}",
        "aboneTipi": "Mesken",
        "sonFatura": {
            "donem": "Kasım 2023",
            "tutar": f"{tutar:.2f} TL",
            "sonOdeme": tarih_uret(tc, -15),
            "durum": "ÖDENDİ" if seed % 2 == 0 else "BEKLİYOR",
            "odemeTarihi": tarih_uret(tc, -20) if seed % 2 == 0 else None,
            "faturaNo": f"FT{seed % 1000000:07d}"
        },
        "tuketim": f"{(seed % 20) + 5} m³",
        "birimFiyat": "8.50 TL/m³",
        "oncekiBorc": "0,00 TL",
        "toplamBorc": "0,00 TL" if seed % 2 == 0 else f"{tutar:.2f} TL",
        "sayaçNo": f"SY{seed % 1000000:07d}",
        "sayaçDurumu": "Aktif",
        "sonOkuma": tarih_uret(tc, -5),
        "suIdaresi": "İstanbul Su ve Kanalizasyon İdaresi (İSKİ)"
    })

# ========== 15 TANE DAHA API ==========

@app.route('/api/v1/elektrik/fatura', methods=['GET'])
def elektrik():
    tc = request.args.get('tc', '')
    if not tc_dogrula(tc): return kayit_bulunamadi()
    kisi = tcden_kisi_uret(tc)
    seed = int(tc)
    tutar = (seed % 500) + 100
    return jsonify_utf8({
        **kisi,
        "aboneNo": f"ELEK-{seed % 100000:06d}",
        "santral": f"{kisi['il']} Anadolu Dağıtım",
        "sonFatura": {
            "donem": "Kasım 2023",
            "tutar": f"{tutar:.2f} TL",
            "tuketim": f"{(seed % 300) + 100} kWh",
            "durum": "ÖDENDİ" if seed % 3 != 0 else "BEKLİYOR"
        }
    })

@app.route('/api/v1/turizm/otel-rezervasyon', methods=['GET'])
def otel_rezervasyon():
    tc = request.args.get('tc', '')
    if not tc_dogrula(tc): return kayit_bulunamadi()
    kisi = tcden_kisi_uret(tc)
    seed = int(tc)
    return jsonify_utf8({
        **kisi,
        "rezervasyonNo": f"RSV-{seed % 100000:06d}",
        "otel": ["Rixos", "Hilton", "Sheraton", "Martı", "Divan"][seed % 5],
        "lokasyon": ["Antalya", "Bodrum", "İzmir", "Muğla", "Çeşme"][seed % 5],
        "giris": tarih_uret(tc, -seed % 30),
        "cikis": tarih_uret(tc, -(seed % 30) + 7),
        "durum": "ONAYLI"
    })

@app.route('/api/v1/ulasim/istanbulkart-bakiye', methods=['GET'])
def istanbulkart():
    tc = request.args.get('tc', '')
    if not tc_dogrula(tc): return kayit_bulunamadi()
    kisi = tcden_kisi_uret(tc)
    seed = int(tc)
    return jsonify_utf8({
        **kisi,
        "kartNo": f"ISTK-{seed % 10000:04d}-{seed % 10000:04d}",
        "kartTipi": ["Anonim", "Kişiye Özel", "Öğrenci"][seed % 3],
        "bakiye": f"{(seed % 100) + 5:.2f} TL",
        "sonYukleme": tarih_uret(tc, seed % 10),
        "sonKullanim": tarih_uret(tc, seed % 3),
        "sonKullanimYeri": ["Metrobüs", "Metro", "Otobüs", "Tramvay"][seed % 4]
    })

@app.route('/api/v1/spor/federasyon/kayit', methods=['GET'])
def spor_federasyon():
    tc = request.args.get('tc', '')
    if not tc_dogrula(tc): return kayit_bulunamadi()
    kisi = tcden_kisi_uret(tc)
    seed = int(tc)
    return jsonify_utf8({
        **kisi,
        "lisansNo": f"SPR-{seed % 10000:04d}",
        "sporDali": ["Futbol", "Basketbol", "Voleybol", "Yüzme", "Atletizm"][seed % 5],
        "kulup": f"{kisi['il']} Spor Kulübü",
        "baslamaTarihi": tarih_uret(tc, seed % 1000),
        "lisansYili": 2023
    })

@app.route('/api/v1/kutuphane/uye-durum', methods=['GET'])
def kutuphane():
    tc = request.args.get('tc', '')
    if not tc_dogrula(tc): return kayit_bulunamadi()
    kisi = tcden_kisi_uret(tc)
    seed = int(tc)
    return jsonify_utf8({
        **kisi,
        "uyeNo": f"KUT-{seed % 10000:04d}",
        "kutuphane": f"{kisi['il']} Halk Kütüphanesi",
        "oduncKitap": [
            {"kitap": "Suç ve Ceza", "yazar": "Dostoyevski", "iade": tarih_uret(tc, -10)},
            {"kitap": "İnce Memed", "yazar": "Yaşar Kemal", "iade": tarih_uret(tc, -5)}
        ] if seed % 2 == 0 else [],
        "uyelikBaslangic": tarih_uret(tc, seed % 1000)
    })

@app.route('/api/v1/saglik/hasta-yatis-gecmisi', methods=['GET'])
def hasta_yatis():
    tc = request.args.get('tc', '')
    if not tc_dogrula(tc): return kayit_bulunamadi()
    kisi = tcden_kisi_uret(tc)
    seed = int(tc)
    return jsonify_utf8({
        **kisi,
        "yatislar": [{
            "hastane": f"{kisi['il']} Hastanesi",
            "bolum": ["Dahiliye", "Cerrahi", "Kardiyoloji", "Nöroloji"][seed % 4],
            "giris": tarih_uret(tc, seed % 100),
            "cikis": tarih_uret(tc, (seed % 100) - 5),
            "tanilar": ["Akut Bronşit", "Hipertansiyon", "Gastrit"][:((seed % 2)+1)],
            "hastaNo": f"HST-{(seed + 1) % 10000:04d}"
        }] if seed % 4 != 0 else []
    })

@app.route('/api/v1/dijital/banka-musteri', methods=['GET'])
def banka_musteri():
    tc = request.args.get('tc', '')
    if not tc_dogrula(tc): return kayit_bulunamadi()
    kisi = tcden_kisi_uret(tc)
    seed = int(tc)
    return jsonify_utf8({
        **kisi,
        "banka": ["Ziraat Bankası", "İş Bankası", "Garanti BBVA", "Yapı Kredi", "Akbank"][seed % 5],
        "musteriNo": f"BNK-{seed % 100000:06d}",
        "musteriSince": tarih_uret(tc, seed % 2000),
        "hesaplar": [{
            "iban": f"TR{seed % 100:02d} 0001 0002 {seed % 10000000000:011d}",
            "tip": "Vadesiz TL",
            "bakiye": f"{(seed % 10000) + 500:.2f} TL"
        }]
    })

@app.route('/api/v1/kredi/risk-raporu', methods=['GET'])
def kredi_risk():
    tc = request.args.get('tc', '')
    if not tc_dogrula(tc): return kayit_bulunamadi()
    kisi = tcden_kisi_uret(tc)
    seed = int(tc)
    kredi_notu = (seed % 500) + 1000
    risk = "Düşük Risk" if kredi_notu > 1400 else "Orta Risk" if kredi_notu > 1200 else "Yüksek Risk"
    return jsonify_utf8({
        **kisi,
        "krediNotu": kredi_notu,
        "riskSeviyesi": risk,
        "sorguTarihi": datetime.now().strftime("%Y-%m-%d"),
        "aciklama": f"Findeks skoru: {kredi_notu}"
    })

@app.route('/api/v1/meb/mezuniyet', methods=['GET'])
def meb_mezuniyet():
    tc = request.args.get('tc', '')
    if not tc_dogrula(tc): return kayit_bulunamadi()
    kisi = tcden_kisi_uret(tc)
    seed = int(tc)
    return jsonify_utf8({
        **kisi,
        "okul": f"{kisi['il']} Lisesi",
        "mezuniyetYili": 2010 + (seed % 10),
        "alan": ["Fen", "Matematik", "Türkçe-Matematik", "Sosyal"][seed % 4],
        "diplomaNo": f"DPL-{seed % 100000:06d}"
    })

@app.route('/api/v1/ticaret/sikayet-kaydi', methods=['GET'])
def ticaret_sikayet():
    tc = request.args.get('tc', '')
    if not tc_dogrula(tc): return kayit_bulunamadi()
    kisi = tcden_kisi_uret(tc)
    seed = int(tc)
    return jsonify_utf8({
        **kisi,
        "sikayetler": [{
            "sirket": f"XYZ {['Elektronik', 'Giyim', 'Market', 'Turizm'][seed % 4]}",
            "tarih": tarih_uret(tc, seed % 100),
            "durum": "Çözüldü" if seed % 2 == 0 else "Beklemede",
            "konu": ["Ürün hatası", "Hizmet kalitesi", "Teslimat gecikmesi"][seed % 3]
        }] if seed % 3 != 0 else []
    })

@app.route('/api/v1/cevre/sehirlerarasi-ceza', methods=['GET'])
def trafik_ceza():
    tc = request.args.get('tc', '')
    if not tc_dogrula(tc): return kayit_bulunamadi()
    kisi = tcden_kisi_uret(tc)
    seed = int(tc)
    return jsonify_utf8({
        **kisi,
        "cezalar": [{
            "plaka": f"34{chr(65 + (seed % 26))}{chr(65 + ((seed//26) % 26))} {seed % 1000:03d}",
            "tarih": tarih_uret(tc, seed % 100),
            "sebep": ["Hız İhlali", "Park İhlali", "Emniyet Kemeri", "Kırmızı Işık"][seed % 4],
            "tutar": f"{(seed % 500) + 100} TL",
            "durum": "Ödendi" if seed % 2 == 0 else "Ödenmedi"
        } for _ in range(seed % 4)]
    })

@app.route('/api/v1/noter/gereceklesen-islem', methods=['GET'])
def noter_islem():
    tc = request.args.get('tc', '')
    if not tc_dogrula(tc): return kayit_bulunamadi()
    kisi = tcden_kisi_uret(tc)
    seed = int(tc)
    return jsonify_utf8({
        **kisi,
        "islemler": [{
            "tip": ["Vekalet", "Miras", "Satış", "Kira", "İpotek"][seed % 5],
            "tarih": tarih_uret(tc, seed % 100),
            "noter": f"{kisi['il']} {seed % 10}. Noterliği",
            "islemNo": f"NT{seed % 100000:06d}"
        }] if seed % 2 == 0 else []
    })

@app.route('/api/v1/ormancilik/avci-lisans', methods=['GET'])
def avci_lisans():
    tc = request.args.get('tc', '')
    if not tc_dogrula(tc): return kayit_bulunamadi()
    kisi = tcden_kisi_uret(tc)
    seed = int(tc)
    return jsonify_utf8({
        **kisi,
        "lisans": "Yok" if seed % 3 == 0 else "Var",
        "lisansNo": f"AVC-{seed % 10000:04d}" if seed % 3 != 0 else None,
        "gecerlilik": tarih_uret(tc, -365) if seed % 3 != 0 else None,
        "avcilikKursu": "Tamamlandı" if seed % 3 != 0 else "Yok"
    })

@app.route('/api/v1/udhb/ucak-bilet', methods=['GET'])
def ucak_bilet():
    tc = request.args.get('tc', '')
    if not tc_dogrula(tc): return kayit_bulunamadi()
    kisi = tcden_kisi_uret(tc)
    seed = int(tc)
    return jsonify_utf8({
        **kisi,
        "biletNo": f"TK{seed % 10000:04d}",
        "ucus": f"TK{seed % 1000:03d}",
        "kalkis": ["İstanbul", "Ankara", "İzmir"][seed % 3],
        "varis": ["Antalya", "Trabzon", "Adana"][seed % 3],
        "tarih": tarih_uret(tc, -seed % 30),
        "durum": "Onaylı"
    })

@app.route('/api/v1/mzk/seyahat-hareket', methods=['GET'])
def mzk_seyahat():
    tc = request.args.get('tc', '')
    if not tc_dogrula(tc): return kayit_bulunamadi()
    kisi = tcden_kisi_uret(tc)
    seed = int(tc)
    return jsonify_utf8({
        **kisi,
        "seyahatler": [{
            "nereden": ["İstanbul", "Ankara", "İzmir"][seed % 3],
            "nereye": ["Antalya", "Bursa", "Konya"][seed % 3],
            "tarih": tarih_uret(tc, seed % 100),
            "numara": f"MK{seed % 10000:04d}"
        }] if seed % 2 == 0 else []
    })

# ========== ÇALIŞTIRMA ==========
if __name__ == '__main__':
    print("""
    ====================================================
    GELİŞMİŞ API SİSTEMİ BAŞLATILIYOR...
    
    ÖZELLİKLER:
    1. Sadece gerçek TC algoritmasına uyan TC'ler için veri döner
    2. Her TC için benzersiz kişi bilgisi üretir
    3. Türkçe karakter desteği tam
    4. Tüm endpoint'ler aynı TC için tutarlı bilgi döner
    5. 2023 yılına ait veriler
    6. 25+ farklı API endpoint
    
    TEST İÇİN:
    Gerçek TC: 10000000146 (test TC'si)
    Sahte TC: 12345678901
    
    Örnek sorgular:
    http://127.0.0.1:5000/api/v1/nufus/sorgu?tc=10000000146
    http://127.0.0.1:5000/api/v1/saglik/asi-kayitlari?tc=10000000146
    http://127.0.0.1:5000/api/v1/eczane/recete-gecmisi?tc=10000000146
    
    TÜRKÇE KARAKTER PROBLEMİ ÇÖZÜLDÜ!
    ====================================================
    """)
    app.run(debug=True, host='0.0.0.0', port=5000)
