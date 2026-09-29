# Taskflow
Django + Channels project manager (HTML/CSS/JS front end).

    pip install -r requirements.txt
    python manage.py makemigrations core && python manage.py migrate
    python manage.py runserver     # Daphne serves HTTP + WebSockets

Register two users in separate browsers to see live notifications. The in-memory channel layer works for one process; use channels_redis in production.
