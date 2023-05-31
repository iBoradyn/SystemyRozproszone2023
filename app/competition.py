from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from app.auth import login_required
from app.db import get_cur, get_db

bp = Blueprint('competition', __name__)


@bp.route('/')
def index():
    return render_template('competition/index.html')


@bp.route('/apply', methods=('GET', 'POST'))
def apply():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        db = get_db()
        cur = get_cur()
        error = None

        if not first_name:
            error = 'Imię jest wymagane.'
        elif not last_name:
            error = 'Nazwisko jest wymagane.'
        elif not email:
            error = 'Email jest wymagany.'

        if error is None:
            try:
                cur.execute(f'INSERT INTO participant (first_name, last_name, email) '
                            f'VALUES (\'{first_name}\', \'{last_name}\', \'{email}\')')
                db.commit()
            except db.IntegrityError:
                error = f"Osoba z podanym adresem email jest już zapisana."
            else:
                cur.close()
                return redirect(url_for("competition.index"))

        cur.close()
        flash(error)

    return render_template('competition/form.html')


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    if g.user['is_admin']:
        db = get_db()
        cur = get_cur()
        cur.execute(f'DELETE FROM participant WHERE id = {id}')
        db.commit()
    return redirect(url_for('competition.participants_list'))


@bp.route('/participants')
@login_required
def participants_list():
    cur = get_cur()
    cur.execute('SELECT * FROM participant')
    participants = cur.fetchall()
    cur.close()

    return render_template('competition/participants_list.html', participants=participants)
