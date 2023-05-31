import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db, get_cur

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cur = get_cur()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                cur.execute(
                    f'INSERT INTO "user" (username, password) '
                    f'VALUES (\'{username}\', \'{generate_password_hash(password)}\')',
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                cur.close()
                return redirect(url_for("auth.login"))

        cur.close()
        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = get_cur()
        error = None
        cur.execute(f'SELECT * FROM "user" WHERE username = \'{username}\'')
        user = cur.fetchone()
        cur.close()

        if user is None or not user['is_staff'] or not check_password_hash(user['password'], password):
            error = 'Niepoprawne dane.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        cur = get_cur()
        cur.execute(f'SELECT * FROM "user" WHERE id = {user_id}')
        g.user = cur.fetchone()
        cur.close()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

