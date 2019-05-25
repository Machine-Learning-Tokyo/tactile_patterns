import os
import logging
from base64 import b64encode

from flask import Flask, render_template, request, session, redirect
from flask_babel import Babel, lazy_gettext
from flask_wtf import FlaskForm, CSRFProtect
from flask_wtf.file import FileField, FileRequired, FileAllowed

from ml.utils import Utils


app = Flask(__name__)
csrf = CSRFProtect(app)
babel = Babel(app)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10MB max for file upload
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)


@babel.localeselector
def get_locale():
    if "lang" not in session or not session["lang"]:
        session["lang"] = request.accept_languages.best_match(["ja", "en"])
    return session["lang"]


class UploadForm(FlaskForm):
    """
    TODO: Display validation error messages clearly
    """
    photo = FileField(lazy_gettext("photo"), validators=[
        FileRequired(),
        FileAllowed(['jpeg', 'jpg', 'png'], lazy_gettext("Please upload image file"))
    ])


@app.route('/', methods=["GET", "POST"])
def main_page():
    form = UploadForm()
    output = None
    file_ext = None
    filename = None
    if form.validate_on_submit():
        image_binary = form.photo.data.read()
        file_ext = Utils.mimetype2ext(form.photo.data.mimetype)
        tactile_image_binary = Utils.photo2tactile(image_binary, file_ext)
        filename = "{}_converted".format(Utils.remove_file_ext(form.photo.data.filename))
        b64_binary = b64encode(tactile_image_binary)
        # Convert to string
        output = b64_binary.decode('utf8')
    return render_template(
        "index.html",
        form=form,
        output=output,
        file_ext=file_ext,
        filename=filename
    )


@app.route("/lang/<locale>", methods=["GET"])
def language(locale):
    session["lang"] = locale
    redirect_url = '/'
    if request.headers["Referer"]:
        redirect_url = request.headers["Referer"]
    return redirect(redirect_url)


if __name__ == "__main__":
    app.run()
