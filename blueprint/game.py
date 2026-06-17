from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from database import GameProposal, ApprovedGame, Game, GamePropertyType
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField
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


@game_bp.route('/proposals')
@login_required
def view_proposals():
    if current_user.is_admin:
        proposals = GameProposal.select()
    else:
        proposals = GameProposal.select().where(GameProposal.proposer == current_user.id)
    return render_template('game/proposals.html', proposals=proposals)


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
            approved_game=approved_game,
            approved=True,
            approved_by=current_user.id,
            approved_at=datetime.datetime.now()
        )
        proposal.delete_instance()  # Supprimer la proposition après approbation
        return redirect(url_for('game.list_games'))
    else:
        return "Proposition non trouvée", 404


@game_bp.route('/reject/<int:proposal_id>', methods=['POST'])
@login_required
def reject_game(proposal_id):
    if not current_user.is_admin:
        return "Accès refusé", 403

    proposal = GameProposal.get_or_none(GameProposal.id == proposal_id)
    if proposal:
        # Supprimer la proposition de jeu
        proposal.delete_instance()
        return redirect(url_for('game.list_games'))
    else:
        return "Proposition non trouvée", 404

# route pour la gestion des types de propriétés des jeux


class ProposePropertyTypeForm(FlaskForm):
    name = StringField('Nom du type de propriété')
    description = TextAreaField('Description du type de propriété')
    multiple_values_allowed = BooleanField('Autoriser plusieurs valeurs pour ce type de propriété')
    only_default_values_allowed = BooleanField('Autoriser uniquement les valeurs par défaut pour ce type de propriété')


@game_bp.route('/property_types/')
@login_required
def list_property_types():
    property_types = GamePropertyType.select()
    return render_template('game/property_types.html', property_types=property_types)


@game_bp.route('/property_types/add', methods=['GET', 'POST'])
@login_required
def add_property_type():
    if not current_user.is_admin:
        return "Accès refusé", 403

    form = ProposePropertyTypeForm()  # Réutilisation du formulaire pour la simplicité
    if form.validate_on_submit():
        GamePropertyType.create(
            name=form.name.data,
            description=form.description.data,
            multiple_values_allowed=form.multiple_values_allowed.data,
            only_default_values_allowed=form.only_default_values_allowed.data
        )
        return redirect(url_for('game.list_property_types'))
    return render_template('game/add_property_type.html', form=form)
