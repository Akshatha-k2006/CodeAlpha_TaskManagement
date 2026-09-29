# Taskflow

A collaborative project management tool inspired by Trello and Asana, built with Django and Django Channels on the backend and vanilla HTML, CSS, and JavaScript on the frontend.

## Features

- **Authentication** — registration and login built on Django's auth system
- **Projects** — create projects and manage membership
- **Boards** — Trello-style columns (To Do, In Progress, Done) with native HTML5 drag-and-drop
- **Tasks** — assign tasks, set due dates, and track status
- **Comments** — threaded discussion per task, posted via `fetch()` with no page reload
- **Notifications** — in-app notification center with an unread badge, updated live over WebSockets
- **Roles** — project creators become admins automatically; a project can have multiple admins
  - **Admins** can add or remove members, assign tasks, edit project settings, and moderate comments
  - **Members** can view tasks, comment, and update tasks assigned to them

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django, Django Channels |
| Real-time | WebSockets (Channels, in-memory layer by default) |
| Frontend | HTML, CSS, JavaScript (no frontend framework) |
| Database | SQLite (development) |

## Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py makemigrations core
python manage.py migrate

# Create an admin account (optional)
python manage.py createsuperuser

# Run the development server
python manage.py runserver
```

The app runs on Daphne, which serves both standard HTTP requests and WebSocket connections.

### Trying out real-time notifications

Register two separate user accounts in two browser windows, add one user to the other's project, and comment on a task. Both users should see notifications update live without refreshing the page.

## Project Structure

```
taskflow/
├── config/          # Django project settings, URLs, ASGI config
├── core/            # Main app: models, views, templates, static files
│   ├── templates/   # HTML templates
│   ├── static/      # CSS and JavaScript
│   ├── models.py    # Project, Membership, Task, Comment, Notification
│   ├── views.py     # Page and API views
│   ├── consumers.py # WebSocket consumer for notifications
│   └── routing.py   # WebSocket URL routing
├── manage.py
└── requirements.txt
```

## Notes for Production

- Replace the in-memory Channels layer with `channels_redis` to support multiple processes or workers.
- Move `SECRET_KEY` and `DEBUG` out of `settings.py` and into environment variables.
- Switch from SQLite to PostgreSQL or another production-grade database.
- Set `ALLOWED_HOSTS` to your actual domain(s).

## Roadmap

- [ ] Password reset via email
- [ ] Comment editing
- [ ] Task due-date reminders
- [ ] Search and filtering on the board

## License

This project was built as part of the CodeAlpha internship program.
