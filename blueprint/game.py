from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from database import GameProposal, ApprovedGame
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField

game_bp = Blueprint('game', __name__, url_prefix='/game')


class ProposeGameForm(FlaskForm):
    name = StringField('Nom du jeu')
    description = TextAreaField('Description du jeu')


@game_bp.route('/list')
@login_required
def list_games():
    games = ApprovedGame.select()
    return render_template('game/list.html', games=games)


@game_bp.route('/propose', methods=['GET', 'POST'])
@login_required
def propose_game():
    form = ProposeGameForm()
    if form.validate_on_submit():
        if ApprovedGame.select().where(ApprovedGame.name == form.name.data).exists():
            form.name.errors.append('Un jeu avec ce nom existe déjà.')
        else:
            # Logique pour enregistrer la proposition de jeu
            GameProposal.create(
                name=form.name.data,
                description=form.description.data,
                proposer=current_user.id
            )
            return redirect(url_for('game.list_games'))
    return render_template('game/propose.html', form=form)
