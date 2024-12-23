# Rocky

See on meie programmeerimisaine projekt. Oleme Tartu Ülikooli tudengid Evelina Kortel ja Marta Laine. Lõime 2D mängu nimega *Rocky*.

---

## Kuidas mängu käivitada?
Mängu saab käivitada kahel viisil:
1. Laadige alla ja pakkige lahti fail **rocky.zip**, kus asub `.exe` fail. Seda saab käivitada topeltklõpsuga.
2. Kopeerige see repostitoorium, avage kaust ja käivitage terminalis käsk:
   ```bash
   python start.py

---

## Mängu juhtimine ja kontseptsioon

Mängija juhib tegelast, kelle eesmärk on koguda kõik kolm smaragdi koopas, jõuda järgmisele tasemele, hävitada vaenlaseid ja vältida punaseid kristalle.
Vaenlased võivad käituda ootamatult, mis tähendab, et neil on erivõime teleporteeruda või mõnikord väsida ja lihtsalt ise surra.

---

## Juhtimine

- Liikumine: **WASD**
- Tulistamine: **SPACE**
- Mängust väljumine: **ESC** või akna sulgemisnupp.

---

## Struktuur

- Peamine kood asub failis **start.py.**
- Kaust **rocky** sisaldab animatsioonide ja disaini jaoks kasutatud pilte.
- **insperatsioon** kaustas on pildid, millest me inspiratsiooni saime või mida projektis kasutasime.
- **levelid** kaust sisaldab `.csv` faile, mis esindavad mängu tasemekaarte.
- Kaust **scripts** sisaldab eraldi koodi nuppude jaoks ning leveli ehitajat, mida kasutasime tasemete kujundamiseks.
- Fail ico on mõeldud .exe failile ikooniks.
- **pycache** on vajalik kiiremaks mängu tööks

---

## Tööprotsess
Evelina kirjutas koodi, kujundas tasemed, otsis sobivaid ressursse ja pilte.
Marta aitas selles kõiges kaasa.
Projekti kallal töötamine võttis kokku umbes 50 tundi või rohkem, arvestades ka piltide otsimist ja õppimist, kuna see on meie esimene mäng.

---

## Kasutatud ressursid
- **Programmeerimise juhend** YouTube , mille abil õppisime selle koodi kirjutamist. Kasutasime ka tasemete loomiseks mõeldud konstruktorit, kohandades seda oma vajadustele.

[Youtube channel](https://www.youtube.com/watch?v=DHgj5jhMJKg&t=1s)

[Github repositoorium tema prijektiga](https://github.com/russs123/Shooter)

[Github repositoorium LevelEditoriga](https://github.com/russs123/LevelEditor)


- **Graafilised ressursid** Disaini ja mänguelementide loomiseks kasutatud ressursid.

[Asset from Icho.io](https://szadiart.itch.io/rocky-world-platformer-set)

