The web app for Tactile Patterns project.

# Features
* Does not store any uploaded images.
* Languages supported:
  * Japanese
  * English
* File upload size is limited to 10MB.

# Development
```
FLASK_APP=main.py SECRET_KEY=xxxxx FLASK_DEBUG=1 flask run
```

# Internationalization
```
# Extract strings
pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot .

# Merge changes
pybabel update -i messages.pot -d translations

# Compile the translations (Required in production)
pybabel compile -d translations

# Start a new language translation (Optional)
pybabel init -i messages.pot -d translations -l <language code>

```

# Production
```
# Pre-requisites. Please use Python 3.
pip install wheel
pip install -r requirements.txt
pybabel compile -d translations

SECRET_KEY=xxxxx gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```