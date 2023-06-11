# TicTacToe
## Prosta gra w kółko i krzyżyk z użyciem flask, socketio, docker, sqlalchemy
## Table of contents
* [Informacje główne](#general-info)
* [Technologie](#technologie)
* [Setup](#setup)
* [Zasady gry](#rules)
* [Uwagi](#comments)

## Informacje główne
Prosta gra przeglądarkowa "kółko i krzyżyk", w której mogą zmierzyć się gracze. 
	
## Technologie
Projekt był tworzony z:
* Python: 3.10
* SocketIO: 2.33
* Flask: 2.3.2
* SQLAlchemy: 2.0.15
* eventlet: 0.33.3
	
## Setup
By włączyć projekt należy:

```
$ pip install -r requirements.txt
$ python run.py
```
Włączony jest tryb debugowania w pliku `game_logic\__init__.py` w miejscu `app.config["DEBUG"] = True` - Można go zmienić ustawiając wartość na `False`
Aby wejść na stronę - http://127.0.0.1:5000

By stworzyć obraz Docker:
`docker build -t tictactoe-image:numer_wersji .  ` - gdzie numer wersji można samemu wybrać

## Zasady gry
Gracz po wpisaniu nazwy użytkownika posiada 10 kredytów. W trakcie przyłączania do pokoju pobierane ma 3 kredyty. Gracz za zwycięstwo dostaje 4 kredyty. Zakończenie partii wyrzuca gracza z pokoju. W przypadku braku kredytów na nową grę, użytkownik może dodać 10 kredytów.
Użytkownik może sprawdzić swoje statystyki za dany dzień wpisując adres **/stats/RRRR-MM-DD/Username** gdzie **RRRR-MM-DD** - data, w kótrej mają być pokazane statystyki, **Username** - nazwa gracza.

## Uwagi
Nie zdążono zabezpieczyć projektu, użyć dotenv. Problem z włączeniem aplikacji w dokerze
