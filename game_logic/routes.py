from flask import Blueprint
from flask import render_template
from sqlalchemy import func
from datetime import datetime

from .models import GameStat, Player, session

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("game.html")


@main.route('/stats/<date>/<username>')
def player_stats(date, username):
    player = session.query(Player).filter_by(username=username).first()
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return 'Invalid date format. Please use YYYY-MM-DD.', 400

    player = session.query(Player).filter_by(id=player.id).first()
    total_wins = session.query(func.count(GameStat.id)) \
        .filter((GameStat.player_1_id == player.id) & (GameStat.result_player_1 == 'win') | \
                (GameStat.player_2_id == player.id) & (GameStat.result_player_2 == 'win')) \
        .scalar()

    total_losses = session.query(func.count(GameStat.id)) \
        .filter((GameStat.player_1_id == player.id) & (GameStat.result_player_1 == 'loss') | \
                (GameStat.player_2_id == player.id) & (GameStat.result_player_2 == 'loss')) \
        .scalar()

    total_draws = session.query(func.count(GameStat.id)) \
        .filter((GameStat.player_1_id == player.id) & (GameStat.result_player_1 == 'draw') | \
                (GameStat.player_2_id == player.id) & (GameStat.result_player_2 == 'draw')) \
        .scalar()

    return render_template('player_stats.html', date=date_obj,
                           stats={'username': player.username, 'wins': total_wins, 'losses': total_losses,
                                  'draws': total_draws})
