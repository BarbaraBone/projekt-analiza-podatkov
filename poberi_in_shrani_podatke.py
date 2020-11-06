import orodja
import re
import requests
import json

STEVILO_STRANI = 30
STEVILO_KNJIG_NA_STRAN = 100 

count = 0
slovar_knjig = []

vzorec_knjiga=re.compile(r'<td width="100%".*?>(.*?)emsp;', re.DOTALL)

vzorec_naslov = re.compile(r'''<a class="bookTitle".*?>\n\s+<span.*?>(?P<naslov>.*?)</span>''', re.DOTALL)
vzorec_avtor = re.compile(r'<a class="authorName".*?><.*?>(?P<avtor>.*?)</span>', re.DOTALL)
vzorec_ocena = re.compile( r'></span></span>\s+(?P<ocena>.*?)\s+avg\srating', re.DOTALL)
vzorec_stevilo_ocen = re.compile(r'mdash; (?P<stevilo_ocen>.*?) ratings', re.DOTALL)
vzorec_stevilo_volilcev = re.compile(r'<a id=".+?" href="#" .*?>(?P<stevilo_volilcev>.*?) people voted', re.DOTALL)

skupina_naslov = 'naslov'
skupina_avtor = 'avtor'
skupina_ocena = 'ocena'
skupina_stevilo_ocen = 'stevilo_ocen'
skupina_stevilo_volilcev = 'stevilo_volilcev'

def zadetek(vzorec, ime_skupine, knjiga):
    zadetek = re.search(vzorec, knjiga).group(ime_skupine)
    return zadetek or None

def html_v_knjige(vsebina):
    """Funkcija poišče posamezne knjige, ki se nahajajo v spletni strani in jih vrne v seznamu"""

    knjige = [knjiga.group(1).strip() for knjiga in re.finditer(vzorec_knjiga, vsebina)]
    return knjige

def knjiga_v_slovar(knjiga):
    """Funkcija iz niza za posamezeno knjigo izlušči podatke o avtorju, naslovu dela, 
    število ljudi, ki si je shranilo knjigo na svojo polico, povprečno oceno
    in kolikokrat je bila kjniga ocenjena ter vrne slovar, ki vsebuje ustrezne podatke"""

    slovar = {
        skupina_naslov: zadetek(vzorec_naslov, skupina_naslov, knjiga),
        skupina_avtor: zadetek(vzorec_avtor, skupina_avtor, knjiga),
        skupina_ocena: float(zadetek(vzorec_ocena, skupina_ocena, knjiga)), 
        skupina_stevilo_ocen: int(zadetek(vzorec_stevilo_ocen, skupina_stevilo_ocen, knjiga).replace(",","")),
        skupina_stevilo_volilcev: int(zadetek(vzorec_stevilo_volilcev, skupina_stevilo_volilcev, knjiga).replace(",", ""))
    }
                
    return slovar

#koda za prebrat in shranit spletno stran in nato shranit urejene podatke v slovar
for stran in range(STEVILO_STRANI):
    prva_na_strani = count*STEVILO_KNJIG_NA_STRAN + 1
    zadnja_na_strani =  STEVILO_KNJIG_NA_STRAN*(count+1)
    url = f'https://www.goodreads.com/list/show/264.Books_That_Everyone_Should_Read_At_Least_Once?page={count+1}'
    count += 1
    datoteka = f'need-to-read/{prva_na_strani}-{zadnja_na_strani}.html'
    orodja.shrani_spletno_stran(url, datoteka)
    vsebina = orodja.vsebina_datoteke(datoteka)

    knjige = html_v_knjige(vsebina) 
    for knjiga in knjige:
        slovar_knjig.append(knjiga_v_slovar(knjiga))

orodja.zapisi_csv(slovar_knjig, slovar_knjig[0].keys(), 'knjige.csv')

with open('knjige.json', 'w') as f:
    json.dump(slovar_knjig, f, indent=2, ensure_ascii=True)

    
    