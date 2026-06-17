from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from database import GameProposal, ApprovedGame, Game
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
import datetime

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


@game_bp.route('/approve/<int:proposal_id>', methods=['POST'])
@login_required
def approve_game(proposal_id):
    if not current_user.is_admin:
        return "Accès refusé", 403

    proposal = GameProposal.get_or_none(GameProposal.id == proposal_id)
    if proposal:
        # Créer un jeu approuvé à partir de la proposition
        approved_game = ApprovedGame.create(
            name=proposal.name,
            description=proposal.description
        )
        # Créer une entrée dans la table Game pour lier la proposition et le jeu approuvé
        Game.create(
            proposal=proposal,
            approved_game=approved_game,
            approved=True,
            approved_by=current_user.id,
            approved_at=datetime.datetime.now()
        )
        return redirect(url_for('game.list_games'))
    else:
        return "Proposition non trouvée", 404
