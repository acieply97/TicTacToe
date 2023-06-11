from flask import request
from flask_socketio import emit, join_room, leave_room
from random import choice

from .extensions import socketio
from .game_engine import GameEngine
from .models import GameStat, Player, engine, session

users = {}
players = {}
active_players = {}
players_in_game = {}
active_games = {}


@socketio.on('connect')
def handle_connect():
    """
        Połączenie ze stroną, wyświetla w logach sesje gracza
    """
    print('Client connected:', request.sid)


@socketio.on('login')
def handle_login(data):
    """
        Obsługa logowania gracza, nowy gracz nie znajdujący się w bazie będzie tworzony i dodawany do bazy
    """
    print('logowanie')
    username = data['username']

    player = session.query(Player).filter_by(username=username).first()

    if player is None:
        player = Player(credits=10, username=username)
        session.add(player)

    is_player_playing = check_player_in_session(player)

    if is_player_playing:
        emit('player_in_session')
    else:
        player.session_id = request.sid
        session.commit()

        print('Client connected:', player)
        emit('user_logged', {'username': username}, room=player.session_id)


@socketio.on('disconnect')
def handle_disconnect():
    """
        Obsługa podczas wychodzenia gracza ze strony. Sprawdzenie czy gracz nie miał już włączonej sesji
    """
    player = session.query(Player).filter_by(session_id=request.sid).first()
    print('Client disconnected:', request.sid)

    for room, players in players_in_game.items():
        if player in players:
            players.remove(player)
            active_players[room] -= 1

            if active_players[room] == 0:
                del players_in_game[room]
                del active_players[room]
                print('Usunięto pusty pokój:', room)
                break


def check_player_in_session(player):
    """
        Sprawdzenie czy gracz jest już zalogowany
    """
    if player.username not in players:
        players[player.username] = request.sid
    else:
        return True


def check_not_full_room():
    """
        Sprawdzenie czy dany pokój posiada maksymalną liczbę graczy
    """
    for room in players_in_game:
        print('Sprawdzany pokoj', room)
        if len(players_in_game[room]) < 2:
            return room


@socketio.on('join_room')
def handle_join_room():
    """
        Obsługa dołączania gracza do pokoju
    """

    check_room = check_not_full_room()

    player = session.query(Player).filter_by(session_id=request.sid).first()

    player_credits = chceck_start_game_credits(player)

    if not player_credits:
        emit('not_enough_credits', {'credits': player.credits}, room=request.sid)
    else:
        emit('hide_add_credits_button')
        if check_room is None:
            room = f'room-{request.sid}'
        else:
            room = check_room

        if room not in active_players:
            active_players[room] = 0

        if active_players[room] < 2:
            join_room(room)

            emit('joined_room', {'room': room, 'credits': player.credits})

            active_players[room] += 1
            players_in_game[room] = players_in_game.get(room, []) + [player]

            print(f'Dołączanie do pokoju {room} gracza: {player.session_id}')
            print('aktywne pokoje', players_in_game)
            print('active_players: ', active_players)

            if active_players[room] == 2:
                game = GameEngine()
                active_games[room] = game

                player_handle_game = players_in_game[room][0].session_id
                print('Jest dwóch graczy', players_in_game[room][0].session_id)
                socketio.emit('start-game',
                              {'room': room,
                               'player_handle_game': player_handle_game},
                              room=player_handle_game)

        else:
            socketio.emit('game_full', {'room': room})
        print(f'Player {player.session_id} joined room {room}')


def chceck_start_game_credits(player):
    """
        Sprawdzenie czy gracz posiada wystarczającą ilość kredytów do gry
    """
    if player.credits >= 3:
        player.credits -= 3
        session.commit()
        return True
    else:
        print(f'{player.session_id} - niewystarczająco kredytów')
        return False


@socketio.on('add_credits')
def add_credits():
    """
        Dodaje graczowi w bazie kredyty
    """
    player = session.query(Player).filter_by(session_id=request.sid).first()

    player.credits += 10
    session.commit()


@socketio.on('start_game')
def handle_start_game(data):
    """
        Tworzenie w bazie instancji gry, przypisanie graczy, rozpoczyna grę
    """

    room = data['room']
    p1, p2 = players_in_game[room]

    player_1 = session.query(Player).filter_by(session_id=p1.session_id).first()
    player_2 = session.query(Player).filter_by(session_id=p2.session_id).first()

    emit('update_credits', {'credits': player_1.credits}, room=player_1.session_id)
    emit('update_credits', {'credits': player_2.credits}, room=player_2.session_id)

    print('Kredyty: ', player_1.credits)
    emit('game_state', {'credits': player_1.credits}, room=player_1.session_id)
    emit('game_state', {'credits': player_2.credits}, room=player_2.session_id)

    if player_1 and player_2:
        game = GameStat(player_1_id=player_1.id, player_2_id=player_2.id)

        session.add(game)
        session.commit()

        first_player = choice(players_in_game[room])
        data['game'] = game.id
        data['player_to_move'] = first_player.session_id

        print('rozpoczyna gracz - ', first_player.username)
        emit('make_move', data, room=first_player.session_id)


@socketio.on('choose_player')
def handle_player_to_move(data):
    """
        Obsługa zmiany ruchu graczy
    """
    room = data['room']
    player_to_move = data['player_to_move']

    p1, p2 = players_in_game[room]

    player_1 = p1.session_id
    player_2 = p2.session_id

    data['player_to_move'] = player_1 if player_to_move == player_2 else player_2

    if player_1 == player_to_move:
        emit('your_turn', data, room=player_1)
        emit('opponent_move', data, room=player_2)
    else:
        emit('your_turn', data, room=player_2)
        emit('opponent_move', data, room=player_1)


@socketio.on('play_move')
def handle_play_move(data):
    """
        Obsługa ruchu po gracza, sprawdzenie czy gra została skończona
    """
    cell_id = data['cellId']
    data = data['data']
    room = data['room']
    game = active_games[room]
    game.write_symbol_on_board(int(cell_id))

    if game.check_win() is not None:
        output = game.check_win()

        game_session = session.query(GameStat).filter_by(id=data['game']).first()
        player_1 = game_session.player_1
        player_2 = game_session.player_2

        if not output:
            game_session.result_player_2 = 'draw'
            game_session.result_player_1 = 'draw'

            emit('game_draw', room=room)

        else:
            if player_1.session_id == data['player_to_move']:
                game_session.result_player_1 = 'loss'
                game_session.result_player_2 = 'win'
                win = player_2
                loss = player_1
            else:
                game_session.result_player_2 = 'loss'
                game_session.result_player_1 = 'win'
                win = player_1
                loss = player_2

            player_win = session.query(Player).filter_by(id=win.id).first()
            player_win.credits += 4

            try:
                session.commit()
                print('Zmiany zostały zapisane w bazie danych.')
            except Exception as e:
                print('Wystąpił błąd podczas zapisywania zmian w bazie danych:', str(e))

            emit('game_loss', {'result': 'loss'}, room=loss.session_id)
            emit('game_win', {'result': 'win'}, room=win.session_id)

            emit('update_credits', {'credits': player_win.credits}, room=win.session_id)

        game.clear_board_state()

        emit('leave_room', {'board_state': game.board_state}, room=room)

        leave_room(room)
        active_players[room] -= 2
        del players_in_game[room]

        print('Aktywne pokoje', active_players, 'Gracze: ', players_in_game)
        return

    emit('game_state', {'board_state': game.board_state}, room=room)
    emit('make_move', data, room=room)
