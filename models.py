import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'campus.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        handle TEXT UNIQUE NOT NULL,
        avatar TEXT NOT NULL,
        banner TEXT NOT NULL,
        department TEXT NOT NULL,
        batch_year INTEGER NOT NULL,
        batch_title TEXT NOT NULL,
        gpa REAL NOT NULL,
        dorm TEXT NOT NULL,
        hometown TEXT NOT NULL,
        relationship_status TEXT NOT NULL,
        bio TEXT NOT NULL,
        quote TEXT NOT NULL,
        canteen_fav TEXT NOT NULL,
        karma INTEGER DEFAULT 100,
        projects_count INTEGER DEFAULT 0,
        badges TEXT NOT NULL,
        socials TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS friendships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id_1 INTEGER NOT NULL,
        student_id_2 INTEGER NOT NULL,
        status TEXT NOT NULL, -- 'friends', 'pending'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(student_id_1, student_id_2),
        FOREIGN KEY(student_id_1) REFERENCES students(id),
        FOREIGN KEY(student_id_2) REFERENCES students(id)
    );

    CREATE TABLE IF NOT EXISTS follows (
        follower_id INTEGER NOT NULL,
        following_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (follower_id, following_id),
        FOREIGN KEY(follower_id) REFERENCES students(id),
        FOREIGN KEY(following_id) REFERENCES students(id)
    );

    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        image_url TEXT,
        tags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(student_id) REFERENCES students(id)
    );

    CREATE TABLE IF NOT EXISTS post_likes (
        post_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        PRIMARY KEY (post_id, student_id),
        FOREIGN KEY(post_id) REFERENCES posts(id),
        FOREIGN KEY(student_id) REFERENCES students(id)
    );

    CREATE TABLE IF NOT EXISTS post_comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(post_id) REFERENCES posts(id),
        FOREIGN KEY(student_id) REFERENCES students(id)
    );

    CREATE TABLE IF NOT EXISTS polls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        category TEXT NOT NULL,
        creator_id INTEGER NOT NULL,
        options_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(creator_id) REFERENCES students(id)
    );

    CREATE TABLE IF NOT EXISTS poll_votes (
        poll_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        option_index INTEGER NOT NULL,
        PRIMARY KEY (poll_id, student_id),
        FOREIGN KEY(poll_id) REFERENCES polls(id),
        FOREIGN KEY(student_id) REFERENCES students(id)
    );

    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        category TEXT NOT NULL,
        date_str TEXT NOT NULL,
        location TEXT NOT NULL,
        image_url TEXT NOT NULL,
        host_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(host_id) REFERENCES students(id)
    );

    CREATE TABLE IF NOT EXISTS event_rsvps (
        event_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        status TEXT NOT NULL, -- 'going', 'interested', 'cant_go'
        PRIMARY KEY (event_id, student_id),
        FOREIGN KEY(event_id) REFERENCES events(id),
        FOREIGN KEY(student_id) REFERENCES students(id)
    );

    CREATE TABLE IF NOT EXISTS pokes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        count INTEGER DEFAULT 1,
        last_poked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(sender_id, receiver_id),
        FOREIGN KEY(sender_id) REFERENCES students(id),
        FOREIGN KEY(receiver_id) REFERENCES students(id)
    );

    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_read INTEGER DEFAULT 0,
        FOREIGN KEY(sender_id) REFERENCES students(id),
        FOREIGN KEY(receiver_id) REFERENCES students(id)
    );

    CREATE TABLE IF NOT EXISTS confessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        category TEXT NOT NULL,
        upvotes INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    conn.commit()
    conn.close()

# ==================== STUDENT CRUD ====================

def get_all_students(search=None, department=None, batch=None):
    conn = get_db()
    query = "SELECT * FROM students WHERE 1=1"
    params = []

    if search:
        query += " AND (name LIKE ? OR handle LIKE ? OR roll_no LIKE ? OR dorm LIKE ? OR bio LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term, term, term])

    if department and department != 'All':
        query += " AND department = ?"
        params.append(department)

    if batch and batch != 'All':
        query += " AND (batch_year = ? OR batch_title = ?)"
        params.extend([batch, batch])

    query += " ORDER BY karma DESC, name ASC"
    rows = conn.execute(query, params).fetchall()
    students = [dict(r) for r in rows]
    for s in students:
        try:
            s['badges'] = json.loads(s['badges'])
        except Exception:
            s['badges'] = [b.strip() for b in s['badges'].split(',') if b.strip()]
        try:
            s['socials'] = json.loads(s['socials'])
        except Exception:
            s['socials'] = {}
    conn.close()
    return students

def get_student_by_id(student_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    if not row:
        conn.close()
        return None
    student = dict(row)
    try:
        student['badges'] = json.loads(student['badges'])
    except Exception:
        student['badges'] = [b.strip() for b in student['badges'].split(',') if b.strip()]
    try:
        student['socials'] = json.loads(student['socials'])
    except Exception:
        student['socials'] = {}
    
    student['followers_count'] = conn.execute("SELECT COUNT(*) FROM follows WHERE following_id = ?", (student_id,)).fetchone()[0]
    student['following_count'] = conn.execute("SELECT COUNT(*) FROM follows WHERE follower_id = ?", (student_id,)).fetchone()[0]
    student['friends_count'] = conn.execute('''
        SELECT COUNT(*) FROM friendships 
        WHERE (student_id_1 = ? OR student_id_2 = ?) AND status = 'friends'
    ''', (student_id, student_id)).fetchone()[0]
    student['posts_count'] = conn.execute("SELECT COUNT(*) FROM posts WHERE student_id = ?", (student_id,)).fetchone()[0]
    
    pokes_row = conn.execute("SELECT SUM(count) FROM pokes WHERE receiver_id = ?", (student_id,)).fetchone()
    student['total_pokes'] = pokes_row[0] if pokes_row and pokes_row[0] else 0

    conn.close()
    return student

def update_student(student_id, data):
    conn = get_db()
    cursor = conn.cursor()
    
    # Handle badges list or json string
    badges = data.get('badges', [])
    if isinstance(badges, str):
        try:
            badges = json.loads(badges)
        except Exception:
            badges = [b.strip() for b in badges.split(',') if b.strip()]
            
    socials = data.get('socials', {})
    if isinstance(socials, str):
        try:
            socials = json.loads(socials)
        except Exception:
            socials = {}

    cursor.execute('''
        UPDATE students SET
            name = COALESCE(?, name),
            handle = COALESCE(?, handle),
            roll_no = COALESCE(?, roll_no),
            department = COALESCE(?, department),
            batch_year = COALESCE(?, batch_year),
            batch_title = COALESCE(?, batch_title),
            gpa = COALESCE(?, gpa),
            dorm = COALESCE(?, dorm),
            hometown = COALESCE(?, hometown),
            relationship_status = COALESCE(?, relationship_status),
            bio = COALESCE(?, bio),
            quote = COALESCE(?, quote),
            canteen_fav = COALESCE(?, canteen_fav),
            karma = COALESCE(?, karma),
            projects_count = COALESCE(?, projects_count),
            avatar = COALESCE(?, avatar),
            banner = COALESCE(?, banner),
            badges = ?,
            socials = ?
        WHERE id = ?
    ''', (
        data.get('name'), data.get('handle'), data.get('roll_no'),
        data.get('department'), data.get('batch_year'), data.get('batch_title'),
        data.get('gpa'), data.get('dorm'), data.get('hometown'),
        data.get('relationship_status'), data.get('bio'), data.get('quote'),
        data.get('canteen_fav'), data.get('karma'), data.get('projects_count'),
        data.get('avatar'), data.get('banner'),
        json.dumps(badges), json.dumps(socials),
        student_id
    ))
    conn.commit()
    conn.close()
    return get_student_by_id(student_id)

def create_student(data):
    conn = get_db()
    cursor = conn.cursor()
    badges = data.get('badges', ["Dean's List", "Active Student"])
    if isinstance(badges, str):
        badges = [b.strip() for b in badges.split(',') if b.strip()]
    socials = data.get('socials', {})
    if isinstance(socials, str):
        try: socials = json.loads(socials)
        except Exception: socials = {}

    cursor.execute('''
        INSERT INTO students (
            roll_no, name, handle, avatar, banner, department, batch_year, batch_title,
            gpa, dorm, hometown, relationship_status, bio, quote, canteen_fav,
            karma, projects_count, badges, socials
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('roll_no'), data.get('name'), data.get('handle'),
        data.get('avatar', 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=400&auto=format&fit=crop&q=80'),
        data.get('banner', 'https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=1200&auto=format&fit=crop&q=80'),
        data.get('department', 'Computer Science'),
        data.get('batch_year', 2027),
        data.get('batch_title', 'Junior'),
        data.get('gpa', 3.80),
        data.get('dorm', 'Kirkland Hall #101'),
        data.get('hometown', 'Campus'),
        data.get('relationship_status', 'Single'),
        data.get('bio', 'New student on campus!'),
        data.get('quote', 'Excited to be here.'),
        data.get('canteen_fav', 'Filter Coffee'),
        data.get('karma', 100),
        data.get('projects_count', 0),
        json.dumps(badges),
        json.dumps(socials)
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def delete_student(student_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE sender_id = ? OR receiver_id = ?", (student_id, student_id))
    cursor.execute("DELETE FROM pokes WHERE sender_id = ? OR receiver_id = ?", (student_id, student_id))
    cursor.execute("DELETE FROM follows WHERE follower_id = ? OR following_id = ?", (student_id, student_id))
    cursor.execute("DELETE FROM friendships WHERE student_id_1 = ? OR student_id_2 = ?", (student_id, student_id))
    cursor.execute("DELETE FROM poll_votes WHERE student_id = ?", (student_id,))
    cursor.execute("DELETE FROM event_rsvps WHERE student_id = ?", (student_id,))
    cursor.execute("DELETE FROM post_likes WHERE student_id = ?", (student_id,))
    cursor.execute("DELETE FROM post_comments WHERE student_id = ?", (student_id,))
    cursor.execute("DELETE FROM posts WHERE student_id = ?", (student_id,))
    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()
    return True

# ==================== FRIENDS & FOLLOWS ====================

def get_student_friends(student_id):
    conn = get_db()
    rows = conn.execute('''
        SELECT s.* FROM students s
        JOIN friendships f ON (
            (f.student_id_1 = ? AND f.student_id_2 = s.id) OR 
            (f.student_id_2 = ? AND f.student_id_1 = s.id)
        )
        WHERE f.status = 'friends'
        ORDER BY s.karma DESC
    ''', (student_id, student_id)).fetchall()
    friends = [dict(r) for r in rows]
    for f in friends:
        try: f['badges'] = json.loads(f['badges'])
        except Exception: f['badges'] = []
    conn.close()
    return friends

def get_student_followers(student_id):
    conn = get_db()
    rows = conn.execute('''
        SELECT s.* FROM students s
        JOIN follows fol ON fol.follower_id = s.id
        WHERE fol.following_id = ?
        ORDER BY s.karma DESC
    ''', (student_id,)).fetchall()
    followers = [dict(r) for r in rows]
    for f in followers:
        try: f['badges'] = json.loads(f['badges'])
        except Exception: f['badges'] = []
    conn.close()
    return followers

def get_student_following(student_id):
    conn = get_db()
    rows = conn.execute('''
        SELECT s.* FROM students s
        JOIN follows fol ON fol.following_id = s.id
        WHERE fol.follower_id = ?
        ORDER BY s.karma DESC
    ''', (student_id,)).fetchall()
    following = [dict(r) for r in rows]
    for f in following:
        try: f['badges'] = json.loads(f['badges'])
        except Exception: f['badges'] = []
    conn.close()
    return following

def get_relationship_status(current_user_id, target_user_id):
    if current_user_id == target_user_id:
        return {'is_self': True}
    
    conn = get_db()
    f_row = conn.execute('''
        SELECT * FROM friendships 
        WHERE (student_id_1 = ? AND student_id_2 = ?) OR (student_id_1 = ? AND student_id_2 = ?)
    ''', (current_user_id, target_user_id, target_user_id, current_user_id)).fetchone()
    
    friend_status = None
    if f_row:
        if f_row['status'] == 'friends':
            friend_status = 'friends'
        elif f_row['student_id_1'] == current_user_id:
            friend_status = 'requested'
        else:
            friend_status = 'received_request'

    follow_row = conn.execute('''
        SELECT 1 FROM follows WHERE follower_id = ? AND following_id = ?
    ''', (current_user_id, target_user_id)).fetchone()
    is_following = bool(follow_row)

    mutuals = conn.execute('''
        SELECT s.name, s.avatar FROM students s
        WHERE s.id IN (
            SELECT CASE WHEN student_id_1 = ? THEN student_id_2 ELSE student_id_1 END
            FROM friendships WHERE (student_id_1 = ? OR student_id_2 = ?) AND status = 'friends'
        ) AND s.id IN (
            SELECT CASE WHEN student_id_1 = ? THEN student_id_2 ELSE student_id_1 END
            FROM friendships WHERE (student_id_1 = ? OR student_id_2 = ?) AND status = 'friends'
        )
    ''', (current_user_id, current_user_id, current_user_id, target_user_id, target_user_id, target_user_id)).fetchall()
    
    conn.close()
    return {
        'is_self': False,
        'friend_status': friend_status,
        'is_following': is_following,
        'mutual_friends_count': len(mutuals),
        'mutual_friends_preview': [dict(m) for m in mutuals[:3]]
    }

# ==================== POSTS & COMMENTS CRUD ====================

def get_feed_posts(current_user_id=None, student_id=None):
    conn = get_db()
    query = '''
        SELECT p.*, s.name as author_name, s.handle as author_handle, s.avatar as author_avatar,
               s.department as author_dept, s.batch_title as author_batch
        FROM posts p
        JOIN students s ON p.student_id = s.id
    '''
    params = []
    if student_id:
        query += " WHERE p.student_id = ?"
        params.append(student_id)
    
    query += " ORDER BY p.created_at DESC"
    rows = conn.execute(query, params).fetchall()
    posts = []
    for r in rows:
        p = dict(r)
        p['likes_count'] = conn.execute("SELECT COUNT(*) FROM post_likes WHERE post_id = ?", (p['id'],)).fetchone()[0]
        p['is_liked'] = False
        if current_user_id:
            p['is_liked'] = bool(conn.execute("SELECT 1 FROM post_likes WHERE post_id = ? AND student_id = ?", (p['id'], current_user_id)).fetchone())
        
        c_rows = conn.execute('''
            SELECT c.*, s.name as author_name, s.avatar as author_avatar, s.handle as author_handle
            FROM post_comments c
            JOIN students s ON c.student_id = s.id
            WHERE c.post_id = ?
            ORDER BY c.created_at ASC
        ''', (p['id'],)).fetchall()
        p['comments'] = [dict(c) for c in c_rows]
        posts.append(p)

    conn.close()
    return posts

def update_post(post_id, content, image_url=None, tags=None):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE posts SET
            content = ?,
            image_url = ?,
            tags = ?
        WHERE id = ?
    ''', (content, image_url, tags, post_id))
    conn.commit()
    conn.close()
    return True

def delete_post(post_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM post_likes WHERE post_id = ?", (post_id,))
    cursor.execute("DELETE FROM post_comments WHERE post_id = ?", (post_id,))
    cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
    return True

def delete_comment(comment_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM post_comments WHERE id = ?", (comment_id,))
    conn.commit()
    conn.close()
    return True

# ==================== POLLS CRUD ====================

def get_all_polls(current_user_id=None):
    conn = get_db()
    rows = conn.execute('''
        SELECT p.*, s.name as creator_name, s.avatar as creator_avatar
        FROM polls p
        JOIN students s ON p.creator_id = s.id
        ORDER BY p.created_at DESC
    ''').fetchall()
    
    polls = []
    for r in rows:
        p = dict(r)
        options = json.loads(p['options_json'])
        vote_counts = {idx: 0 for idx in range(len(options))}

        v_rows = conn.execute("SELECT option_index, COUNT(*) as cnt FROM poll_votes WHERE poll_id = ? GROUP BY option_index", (p['id'],)).fetchall()
        total_votes = 0
        for vr in v_rows:
            vote_counts[vr['option_index']] = vr['cnt']
            total_votes += vr['cnt']

        p['total_votes'] = total_votes
        p['options_data'] = []
        for idx, opt in enumerate(options):
            cnt = vote_counts.get(idx, 0)
            pct = round((cnt / total_votes * 100), 1) if total_votes > 0 else 0
            p['options_data'].append({
                'index': idx,
                'text': opt,
                'votes': cnt,
                'percentage': pct
            })

        user_voted_idx = None
        if current_user_id:
            uv = conn.execute("SELECT option_index FROM poll_votes WHERE poll_id = ? AND student_id = ?", (p['id'], current_user_id)).fetchone()
            if uv:
                user_voted_idx = uv['option_index']
        p['user_voted_idx'] = user_voted_idx
        polls.append(p)

    conn.close()
    return polls

def update_poll(poll_id, question, category):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE polls SET question = ?, category = ? WHERE id = ?", (question, category, poll_id))
    conn.commit()
    conn.close()
    return True

def delete_poll(poll_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM poll_votes WHERE poll_id = ?", (poll_id,))
    cursor.execute("DELETE FROM polls WHERE id = ?", (poll_id,))
    conn.commit()
    conn.close()
    return True

# ==================== EVENTS CRUD ====================

def get_all_events(current_user_id=None):
    conn = get_db()
    rows = conn.execute('''
        SELECT e.*, s.name as host_name, s.avatar as host_avatar, s.department as host_dept
        FROM events e
        JOIN students s ON e.host_id = s.id
        ORDER BY e.created_at DESC
    ''').fetchall()

    events = []
    for r in rows:
        ev = dict(r)
        going_count = conn.execute("SELECT COUNT(*) FROM event_rsvps WHERE event_id = ? AND status = 'going'", (ev['id'],)).fetchone()[0]
        interested_count = conn.execute("SELECT COUNT(*) FROM event_rsvps WHERE event_id = ? AND status = 'interested'", (ev['id'],)).fetchone()[0]
        
        attendees = conn.execute('''
            SELECT s.name, s.avatar FROM students s
            JOIN event_rsvps r ON r.student_id = s.id
            WHERE r.event_id = ? AND r.status = 'going'
            LIMIT 5
        ''', (ev['id'],)).fetchall()

        user_rsvp = None
        if current_user_id:
            ur = conn.execute("SELECT status FROM event_rsvps WHERE event_id = ? AND student_id = ?", (ev['id'], current_user_id)).fetchone()
            if ur:
                user_rsvp = ur['status']

        ev['going_count'] = going_count
        ev['interested_count'] = interested_count
        ev['attendees'] = [dict(a) for a in attendees]
        ev['user_rsvp'] = user_rsvp
        events.append(ev)

    conn.close()
    return events

def update_event(event_id, title, description, category, date_str, location, image_url):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE events SET
            title = ?, description = ?, category = ?,
            date_str = ?, location = ?, image_url = ?
        WHERE id = ?
    ''', (title, description, category, date_str, location, image_url, event_id))
    conn.commit()
    conn.close()
    return True

def delete_event(event_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM event_rsvps WHERE event_id = ?", (event_id,))
    cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()
    return True

# ==================== MESSAGING (DMs) ====================

def send_message(sender_id, receiver_id, content):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (sender_id, receiver_id, content)
        VALUES (?, ?, ?)
    ''', (sender_id, receiver_id, content))
    msg_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return msg_id

def get_conversation(user1_id, user2_id):
    conn = get_db()
    # Mark incoming messages as read
    conn.execute('''
        UPDATE messages SET is_read = 1
        WHERE sender_id = ? AND receiver_id = ?
    ''', (user2_id, user1_id))
    conn.commit()

    rows = conn.execute('''
        SELECT m.*, s.name as sender_name, s.avatar as sender_avatar, s.handle as sender_handle
        FROM messages m
        JOIN students s ON m.sender_id = s.id
        WHERE (m.sender_id = ? AND m.receiver_id = ?) OR (m.sender_id = ? AND m.receiver_id = ?)
        ORDER BY m.created_at ASC
    ''', (user1_id, user2_id, user2_id, user1_id)).fetchall()
    messages = [dict(r) for r in rows]
    conn.close()
    return messages

def get_conversations_list(current_user_id):
    conn = get_db()
    # Find all students with whom current_user has exchanged messages or is friends with
    rows = conn.execute('''
        SELECT DISTINCT s.id, s.name, s.handle, s.avatar, s.department, s.batch_title,
            (SELECT content FROM messages 
             WHERE (sender_id = s.id AND receiver_id = ?) OR (sender_id = ? AND receiver_id = s.id)
             ORDER BY created_at DESC LIMIT 1) as last_message,
            (SELECT created_at FROM messages 
             WHERE (sender_id = s.id AND receiver_id = ?) OR (sender_id = ? AND receiver_id = s.id)
             ORDER BY created_at DESC LIMIT 1) as last_message_time,
            (SELECT COUNT(*) FROM messages 
             WHERE sender_id = s.id AND receiver_id = ? AND is_read = 0) as unread_count
        FROM students s
        WHERE s.id != ? AND (
            s.id IN (SELECT sender_id FROM messages WHERE receiver_id = ?) OR
            s.id IN (SELECT receiver_id FROM messages WHERE sender_id = ?) OR
            s.id IN (SELECT CASE WHEN student_id_1 = ? THEN student_id_2 ELSE student_id_1 END
                     FROM friendships WHERE (student_id_1 = ? OR student_id_2 = ?) AND status = 'friends')
        )
        ORDER BY last_message_time DESC, s.name ASC
    ''', (
        current_user_id, current_user_id,
        current_user_id, current_user_id,
        current_user_id,
        current_user_id,
        current_user_id, current_user_id,
        current_user_id, current_user_id, current_user_id
    )).fetchall()
    
    conversations = [dict(r) for r in rows]
    conn.close()
    return conversations

# ==================== CONFESSIONS CRUD ====================

def get_all_confessions():
    conn = get_db()
    rows = conn.execute("SELECT * FROM confessions ORDER BY created_at DESC").fetchall()
    confessions = [dict(r) for r in rows]
    conn.close()
    return confessions

def create_confession(content, category='General'):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO confessions (content, category) VALUES (?, ?)", (content, category))
    cid = cursor.lastrowid
    conn.commit()
    conn.close()
    return cid

def upvote_confession(confession_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE confessions SET upvotes = upvotes + 1 WHERE id = ?", (confession_id,))
    upvotes = cursor.execute("SELECT upvotes FROM confessions WHERE id = ?", (confession_id,)).fetchone()[0]
    conn.commit()
    conn.close()
    return upvotes

def delete_confession(confession_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM confessions WHERE id = ?", (confession_id,))
    conn.commit()
    conn.close()
    return True

# ==================== LEADERBOARDS ====================

def get_leaderboards(department=None):
    conn = get_db()
    global_top = conn.execute('''
        SELECT id, name, handle, avatar, department, batch_title, batch_year, gpa, karma, projects_count, badges
        FROM students
        ORDER BY karma DESC, gpa DESC
        LIMIT 20
    ''').fetchall()

    query = '''
        SELECT id, name, handle, avatar, department, batch_title, batch_year, gpa, karma, projects_count, badges
        FROM students
    '''
    params = []
    if department and department != 'All':
        query += " WHERE department = ?"
        params.append(department)
    
    query += " ORDER BY gpa DESC, karma DESC, projects_count DESC"
    dept_top = conn.execute(query, params).fetchall()

    def process_rows(rows):
        res = []
        for r in rows:
            d = dict(r)
            try: d['badges'] = json.loads(d['badges'])
            except Exception: d['badges'] = []
            res.append(d)
        return res

    result = {
        'global': process_rows(global_top),
        'department': process_rows(dept_top)
    }
    conn.close()
    return result
