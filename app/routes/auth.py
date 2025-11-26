from flask import Blueprint, url_for, redirect, session, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import oauth
from app.models import User, Account, db
import uuid

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    redirect_uri = url_for('auth.authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/authorize')
def authorize():
    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')
        if not user_info:
            user_info = oauth.google.userinfo()
            
        if not user_info:
            flash("Failed to fetch user info", "error")
            return redirect(url_for('main.index'))

        # Check if user exists by email
        email = user_info.get('email')
        user = User.query.filter_by(email=email).first()

        if not user:
            # Create new user
            user = User(
                id=str(uuid.uuid4()),
                name=user_info.get('name'),
                email=email,
                image=user_info.get('picture')
            )
            db.session.add(user)
            db.session.commit()
            
            # Create account link (simplified)
            account = Account(
                user_id=user.id,
                provider='google',
                provider_account_id=user_info.get('sub'),
                access_token=token.get('access_token'),
                refresh_token=token.get('refresh_token'),
                expires_at=token.get('expires_at')
            )
            db.session.add(account)
            db.session.commit()
        
        login_user(user)
        return redirect(url_for('main.index'))
        
    except Exception as e:
        flash(f"Authentication failed: {str(e)}", "error")
        return redirect(url_for('main.index'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
