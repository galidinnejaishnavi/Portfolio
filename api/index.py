import os
import ssl
from datetime import datetime
import resend
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy


base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
template_dir = os.path.join(base_dir, "templates")
static_dir = os.path.join(base_dir, "static")

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "portfolio-secret-key-12345")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db_url = (
    os.environ.get("DATABASE_URL_POSTGRES_URL")
    or os.environ.get("DATABASE_URL_POSTGRES_PRISMA_URL")
    or os.environ.get("DATABASE_URL")
    or os.environ.get("POSTGRES_URL")
    or os.environ.get("SUPABASE_DB_URL")
)

if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+pg8000://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+pg8000://", 1)

    if "?" in db_url:
        db_url = db_url.split("?")[0]

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "connect_args": {
            "ssl_context": ssl.create_default_context()
        }
    }
else:
    # If running on Vercel without a Postgres database attached yet, use writable /tmp folder
    if os.environ.get("VERCEL"):
        sqlite_db_path = "/tmp/portfolio.db"
    else:
        sqlite_db_path = os.path.join(base_dir, "portfolio.db")
    
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{sqlite_db_path}"


db = SQLAlchemy(app)


def is_mail_configured() -> bool:
    return bool(os.environ.get("RESEND_API_KEY"))


def send_contact_email(message: 'ContactMessage') -> None:
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        raise RuntimeError("RESEND_API_KEY environment variable is missing")

    resend.api_key = api_key
    mail_from = os.environ.get("MAIL_FROM", "onboarding@resend.dev")
    mail_to = os.environ.get("MAIL_TO", "galidinnejaishnavi@gmail.com")

    text_body = (
        f"Name: {message.name}\n"
        f"Email: {message.email}\n"
        f"Phone: {message.phone or 'N/A'}\n"
        f"Subject: {message.subject}\n\n"
        f"Message:\n{message.message}\n\n"
        f"Received: {message.created_at}"
    )

    params: resend.Emails.SendParams = {
        "from": mail_from,
        "to": [mail_to],
        "reply_to": message.email,
        "subject": f"Portfolio Contact: {message.subject}",
        "text": text_body,
    }

    resend.Emails.send(params)


class ContactMessage(db.Model):
    __tablename__ = "contact_messages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    subject = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ContactMessage {self.email} - {self.subject}>"


with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Database setup warning/error: {e}")


@app.route("/favicon.ico")
@app.route("/favicon.png")
def favicon():
    from flask import send_from_directory
    return send_from_directory(static_dir, "logo.png", mimetype="image/png")


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/skills")
def skills():
    return render_template("skills.html")


@app.route("/projects")
def projects():
    return render_template("projects.html")


@app.route("/education")
def education():
    return render_template("education.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        subject = request.form.get("subject")
        message = request.form.get("message")

        if not name or not email or not subject or not message:
            flash("Please fill in all required fields.", "danger")
            return render_template("contact.html")

        try:
            new_msg = ContactMessage(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message,
            )

            db.session.add(new_msg)
            db.session.commit()

            email_error = None
            try:
                send_contact_email(new_msg)
            except Exception as e:
                email_error = e
                print(f"Email error: {e}")

            if email_error:
                if isinstance(email_error, RuntimeError) and "Mail configuration" in str(email_error):
                    flash(
                        "Your message was saved, but email notifications are not configured.",
                        "warning",
                    )
                else:
                    flash(
                        "Your message was saved, but email notification could not be delivered.",
                        "danger",
                    )
            else:
                flash(
                    "Your message has been sent successfully! Thank you for reaching out.",
                    "success",
                )

        except Exception as e:
            db.session.rollback()
            print(f"Database error: {e}")
            flash('There was an error saving your message. Please try again later or email directly.', 'danger')

        return redirect(url_for('contact'))

    return render_template('contact.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)