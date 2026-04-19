from flask import Blueprint, redirect, url_for, session, request, render_template
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.models.vendedor import Vendedor
from app.models.loja import Loja
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from config import Config
import json

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    # Build Google OAuth URL
    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={Config.GOOGLE_CLIENT_ID}&redirect_uri={url_for('auth.callback', _external=True)}&response_type=code&scope=openid email profile"
    print(url_for('auth.callback', _external=True))
    return render_template("auth/login.html", google_auth_url=google_auth_url)


@auth_bp.route("/login/callback")
def callback():
    code = request.args.get("code")

    if not code:
        return redirect(url_for("auth.login"))

    # Exchange code for token
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": Config.GOOGLE_CLIENT_ID,
        "client_secret": Config.GOOGLE_CLIENT_SECRET,
        "redirect_uri": url_for("auth.callback", _external=True),
        "grant_type": "authorization_code",
    }

    response = requests.post(token_url, data=data)
    token_data = response.json()

    if "id_token" not in token_data:
        return redirect(url_for("auth.login"))

    # Verify and decode ID token
    try:
        idinfo = id_token.verify_oauth2_token(
            token_data["id_token"], google_requests.Request(), Config.GOOGLE_CLIENT_ID
        )

        google_id = idinfo["sub"]
        email = idinfo["email"]
        name = idinfo["name"]

        # Check if user exists
        user = User.query.filter_by(google_id=google_id).first()

        if not user:
            # Create new user
            user = User(
                google_id=google_id,
                email=email,
                name=name,
                is_admin=True,  # First user can be made admin manually in database
            )

            db.session.add(user)
            db.session.flush()  # Flush to get user ID
            db.session.commit()

        login_user(user)

        # Clear previous store selection
        session.pop("loja_id", None)

        return redirect(url_for("vendas.nova"))

    except ValueError:
        return redirect(url_for("auth.login"))


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("auth.login"))
