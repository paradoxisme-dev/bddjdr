from flask import Blueprint, render_template
from database import Game

game_bp = Blueprint('game', __name__, url_prefix='/game')

@game_bp.route('/list')
def list_games():
    games = Game.select()
    return render_template('game/list.html', games=games)

@game_bp.route('/propose')
def propose_game():
    return render_template('game/propose.html')
