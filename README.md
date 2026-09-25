# College Campus Network - The College Underground

A full-stack college social network inspired by early Facebook — built with Flask, SQLite, Tailwind CSS, and vanilla JavaScript.

## Features

- **Instagram-style Profiles** — Editable student profiles with avatars, banners, bio, GPA, badges, and social links
- **The Wire (Feed)** — Post updates with images, likes, comments, and Instagram Story-style player
- **Campus Directory** — Browse and search all students, add new students
- **Friends & Following** — Send/accept/decline friend requests, follow/unfollow
- **Campus Polls** — Create, vote, edit, and delete polls with categories
- **Events & Hackathons** — Campus events with RSVP, edit, and delete
- **Campus Messenger** — 1-on-1 direct messaging with chat bubbles
- **Campus Confessions** — Anonymous confession board with upvotes
- **Leaderboards** — Overall Karma leaderboard + Department-wise rankings
- **Pokes** — Classic Facebook-style pokes
- **Dark Mode** — Toggle between light and dark themes
- **Everything is Editable** — Full CRUD for students, posts, polls, events, messages, confessions

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python Flask |
| Database | SQLite |
| Frontend | Jinja2 Templates + Tailwind CSS + Font Awesome |
| JavaScript | Vanilla JS (no frameworks) |

## Setup & Run

```bash
# Install dependencies
pip install flask

# Seed the database with sample data
python seed_data.py

# Start the server
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

## Project Structure

```
college-campus-network/
├── app.py              # Flask routes and API endpoints
├── models.py           # Database models and CRUD operations
├── seed_data.py        # Sample data seeder (16 students, posts, polls, etc.)
├── test_app.py         # 17 unit tests
├── static/
│   ├── css/style.css   # Custom styles + dark mode
│   ├── js/app.js       # Frontend interactivity (CRUD, modals, lightbox, stories)
│   └── uploads/        # Uploaded profile images
└── templates/
    ├── base.html        # Base layout (navbar, modals, dark mode toggle)
    ├── feed.html        # The Wire - campus feed with stories
    ├── profile.html     # Student profile with edit modal
    ├── directory.html   # Student directory with search
    ├── leaderboard.html # Karma & department leaderboards
    ├── polls.html       # Campus polls
    ├── events.html      # Events & hackathons
    ├── messages.html    # Direct messaging
    └── confessions.html # Anonymous confessions board
```

## Screenshots

Visit `http://127.0.0.1:5000` after running to explore the full app.

## License

MIT
