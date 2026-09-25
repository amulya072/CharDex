import os
import json
import sqlite3
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from models import (
    get_db, init_db, get_all_students, get_student_by_id, update_student, create_student, delete_student,
    get_student_friends, get_student_followers, get_student_following,
    get_relationship_status, get_feed_posts, update_post, delete_post, delete_comment,
    get_all_polls, update_poll, delete_poll,
    get_all_events, update_event, delete_event,
    send_message, get_conversation, get_conversations_list,
    get_all_confessions, create_confession, upvote_confession, delete_confession,
    get_leaderboards
)

app = Flask(__name__)
app.secret_key = 'thecollege-unofficial-campus-network-2004'

@app.before_request
def ensure_current_user():
    current_id = session.get('student_id')
    if not current_id or not get_student_by_id(current_id):
        conn = get_db()
        row = conn.execute("SELECT id FROM students ORDER BY id ASC LIMIT 1").fetchone()
        conn.close()
        if row:
            session['student_id'] = row['id']

@app.context_processor
def inject_global_data():
    current_user_id = session.get('student_id', 1)
    current_user = get_student_by_id(current_user_id)
    all_students = get_all_students()
    
    conn = get_db()
    # Pending friend requests
    pending_requests = conn.execute('''
        SELECT s.*, f.id as friendship_id FROM students s
        JOIN friendships f ON f.student_id_1 = s.id
        WHERE f.student_id_2 = ? AND f.status = 'pending'
    ''', (current_user_id,)).fetchall()
    
    # Poke notifications
    pokes = conn.execute('''
        SELECT s.name, s.avatar, s.id, p.count, p.last_poked
        FROM pokes p
        JOIN students s ON p.sender_id = s.id
        WHERE p.receiver_id = ?
        ORDER BY p.last_poked DESC
    ''', (current_user_id,)).fetchall()
    
    # Unread messages count
    unread_msg_count = conn.execute('''
        SELECT COUNT(*) FROM messages WHERE receiver_id = ? AND is_read = 0
    ''', (current_user_id,)).fetchone()[0]

    conn.close()

    return {
        'current_user': current_user,
        'all_students_menu': all_students,
        'pending_friend_requests': [dict(r) for r in pending_requests],
        'poke_notifications': [dict(p) for p in pokes],
        'unread_msg_count': unread_msg_count
    }

# ==================== PAGE ROUTES ====================

@app.route('/')
def index():
    current_user_id = session.get('student_id', 1)
    posts = get_feed_posts(current_user_id=current_user_id)
    all_polls = get_all_polls(current_user_id=current_user_id)
    all_events = get_all_events(current_user_id=current_user_id)
    leaderboards = get_leaderboards()
    
    featured_poll = all_polls[0] if all_polls else None
    next_event = all_events[0] if all_events else None
    top_students = leaderboards['global'][:5]
    
    return render_template(
        'feed.html',
        posts=posts,
        featured_poll=featured_poll,
        next_event=next_event,
        top_students=top_students,
        active_tab='feed'
    )

@app.route('/directory')
def directory():
    search = request.args.get('q', '').strip()
    department = request.args.get('dept', 'All')
    batch = request.args.get('batch', 'All')
    
    students = get_all_students(search=search if search else None, department=department, batch=batch)
    return render_template(
        'directory.html',
        students=students,
        search=search,
        selected_dept=department,
        selected_batch=batch,
        active_tab='directory'
    )

@app.route('/profile/<int:student_id>')
def profile(student_id):
    current_user_id = session.get('student_id', 1)
    student = get_student_by_id(student_id)
    if not student:
        return redirect(url_for('directory'))

    relationship = get_relationship_status(current_user_id, student_id)
    friends = get_student_friends(student_id)
    followers = get_student_followers(student_id)
    following = get_student_following(student_id)
    posts = get_feed_posts(current_user_id=current_user_id, student_id=student_id)

    return render_template(
        'profile.html',
        student=student,
        relationship=relationship,
        friends=friends,
        followers=followers,
        following=following,
        posts=posts,
        active_tab='profile' if student_id == current_user_id else 'directory'
    )

@app.route('/leaderboard')
def leaderboard():
    department = request.args.get('dept', 'Computer Science')
    leaderboards = get_leaderboards(department=department)
    
    departments_list = [
        'Computer Science',
        'Mechanical Engineering',
        'Electrical Engineering',
        'Business Administration',
        'Biotechnology',
        'Design & Arts'
    ]
    
    return render_template(
        'leaderboard.html',
        global_leaderboard=leaderboards['global'],
        dept_leaderboard=leaderboards['department'],
        selected_dept=department,
        departments=departments_list,
        active_tab='leaderboard'
    )

@app.route('/polls')
def polls():
    current_user_id = session.get('student_id', 1)
    polls_list = get_all_polls(current_user_id=current_user_id)
    return render_template(
        'polls.html',
        polls=polls_list,
        active_tab='polls'
    )

@app.route('/events')
def events():
    current_user_id = session.get('student_id', 1)
    category = request.args.get('cat', 'All')
    events_list = get_all_events(current_user_id=current_user_id)
    if category != 'All':
        events_list = [e for e in events_list if e['category'] == category]
        
    return render_template(
        'events.html',
        events=events_list,
        selected_cat=category,
        active_tab='events'
    )

@app.route('/messages')
@app.route('/messages/<int:target_id>')
def messages_view(target_id=None):
    current_user_id = session.get('student_id', 1)
    conversations = get_conversations_list(current_user_id)
    
    active_target = None
    chat_messages = []
    
    if target_id:
        active_target = get_student_by_id(target_id)
        if active_target:
            chat_messages = get_conversation(current_user_id, target_id)
    elif conversations:
        # Default to first conversation
        first_c = conversations[0]
        active_target = get_student_by_id(first_c['id'])
        if active_target:
            chat_messages = get_conversation(current_user_id, active_target['id'])
    
    return render_template(
        'messages.html',
        conversations=conversations,
        active_target=active_target,
        chat_messages=chat_messages,
        active_tab='messages'
    )

@app.route('/confessions')
def confessions():
    all_c = get_all_confessions()
    return render_template(
        'confessions.html',
        confessions=all_c,
        active_tab='confessions'
    )

# ==================== STUDENT CRUD APIs (Everything Editable) ====================

@app.route('/api/edit-student/<int:student_id>', methods=['POST'])
def api_edit_student(student_id):
    data = request.get_json() or {}
    updated = update_student(student_id, data)
    if updated:
        return jsonify({'success': True, 'student': updated})
    return jsonify({'success': False, 'error': 'Update failed'}), 400

@app.route('/api/create-student', methods=['POST'])
def api_create_student():
    data = request.get_json() or {}
    if not data.get('name') or not data.get('roll_no'):
        return jsonify({'success': False, 'error': 'Name and Roll Number required'}), 400
    
    if not data.get('handle'):
        data['handle'] = data['name'].lower().replace(' ', '_')
        
    try:
        new_id = create_student(data)
        return jsonify({'success': True, 'id': new_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/delete-student/<int:student_id>', methods=['POST'])
def api_delete_student(student_id):
    delete_student(student_id)
    return jsonify({'success': True})

# ==================== POSTS & COMMENTS CRUD APIs ====================

@app.route('/api/create-post', methods=['POST'])
def create_post():
    current_user_id = session.get('student_id', 1)
    content = request.form.get('content', '').strip()
    image_url = request.form.get('image_url', '').strip() or None
    tags = request.form.get('tags', '').strip() or None

    if not content:
        return redirect(url_for('index'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO posts (student_id, content, image_url, tags)
        VALUES (?, ?, ?, ?)
    ''', (current_user_id, content, image_url, tags))
    cursor.execute('UPDATE students SET karma = karma + 10 WHERE id = ?', (current_user_id,))
    conn.commit()
    conn.close()

    return redirect(request.referrer or url_for('index'))

@app.route('/api/edit-post/<int:post_id>', methods=['POST'])
def api_edit_post(post_id):
    data = request.get_json() or {}
    content = data.get('content', '').strip()
    image_url = data.get('image_url', '').strip() or None
    tags = data.get('tags', '').strip() or None
    if not content:
        return jsonify({'success': False, 'error': 'Content cannot be empty'}), 400

    update_post(post_id, content, image_url, tags)
    return jsonify({'success': True})

@app.route('/api/delete-post/<int:post_id>', methods=['POST'])
def api_delete_post(post_id):
    delete_post(post_id)
    return jsonify({'success': True})

@app.route('/api/delete-comment/<int:comment_id>', methods=['POST'])
def api_delete_comment(comment_id):
    delete_comment(comment_id)
    return jsonify({'success': True})

@app.route('/api/like-post', methods=['POST'])
def like_post():
    current_user_id = session.get('student_id', 1)
    data = request.get_json() or {}
    post_id = data.get('post_id')

    if not post_id:
        return jsonify({'success': False, 'error': 'Missing post ID'}), 400

    conn = get_db()
    cursor = conn.cursor()
    exists = cursor.execute('SELECT 1 FROM post_likes WHERE post_id = ? AND student_id = ?', (post_id, current_user_id)).fetchone()

    if exists:
        cursor.execute('DELETE FROM post_likes WHERE post_id = ? AND student_id = ?', (post_id, current_user_id))
        is_liked = False
    else:
        cursor.execute('INSERT INTO post_likes (post_id, student_id) VALUES (?, ?)', (post_id, current_user_id))
        is_liked = True

    likes_count = cursor.execute('SELECT COUNT(*) FROM post_likes WHERE post_id = ?', (post_id,)).fetchone()[0]
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'is_liked': is_liked, 'likes_count': likes_count})

@app.route('/api/comment-post', methods=['POST'])
def comment_post():
    current_user_id = session.get('student_id', 1)
    data = request.get_json() or {}
    post_id = data.get('post_id')
    content = data.get('content', '').strip()

    if not post_id or not content:
        return jsonify({'success': False, 'error': 'Missing comment'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO post_comments (post_id, student_id, content)
        VALUES (?, ?, ?)
    ''', (post_id, current_user_id, content))
    comment_id = cursor.lastrowid
    cursor.execute('UPDATE students SET karma = karma + 2 WHERE id = ?', (current_user_id,))
    conn.commit()

    student = cursor.execute('SELECT name, avatar, handle FROM students WHERE id = ?', (current_user_id,)).fetchone()
    conn.close()

    return jsonify({
        'success': True,
        'comment': {
            'id': comment_id,
            'author_name': student['name'],
            'author_avatar': student['avatar'],
            'author_handle': student['handle'],
            'content': content
        }
    })

# ==================== POLLS CRUD APIs ====================

@app.route('/api/create-poll', methods=['POST'])
def create_poll():
    current_user_id = session.get('student_id', 1)
    question = request.form.get('question', '').strip()
    category = request.form.get('category', 'Campus Life').strip()
    options = [opt.strip() for opt in request.form.getlist('options[]') if opt.strip()]

    if not question or len(options) < 2:
        return jsonify({'success': False, 'error': 'Question and at least 2 options required'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO polls (question, category, creator_id, options_json)
        VALUES (?, ?, ?, ?)
    ''', (question, category, current_user_id, json.dumps(options)))
    cursor.execute('UPDATE students SET karma = karma + 15 WHERE id = ?', (current_user_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('polls'))

@app.route('/api/edit-poll/<int:poll_id>', methods=['POST'])
def api_edit_poll(poll_id):
    data = request.get_json() or {}
    question = data.get('question', '').strip()
    category = data.get('category', 'Campus Life').strip()
    if not question:
        return jsonify({'success': False, 'error': 'Question cannot be empty'}), 400
    update_poll(poll_id, question, category)
    return jsonify({'success': True})

@app.route('/api/delete-poll/<int:poll_id>', methods=['POST'])
def api_delete_poll(poll_id):
    delete_poll(poll_id)
    return jsonify({'success': True})

@app.route('/api/vote-poll', methods=['POST'])
def vote_poll():
    current_user_id = session.get('student_id', 1)
    data = request.get_json() or {}
    poll_id = data.get('poll_id')
    option_index = data.get('option_index')

    if poll_id is None or option_index is None:
        return jsonify({'success': False, 'error': 'Invalid poll or option'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO poll_votes (poll_id, student_id, option_index)
        VALUES (?, ?, ?)
    ''', (poll_id, current_user_id, option_index))
    
    cursor.execute('UPDATE students SET karma = karma + 2 WHERE id = ?', (current_user_id,))
    conn.commit()

    poll_row = cursor.execute('SELECT * FROM polls WHERE id = ?', (poll_id,)).fetchone()
    if not poll_row:
        conn.close()
        return jsonify({'success': False, 'error': 'Poll not found'}), 404

    options = json.loads(poll_row['options_json'])
    v_rows = cursor.execute('SELECT option_index, COUNT(*) as cnt FROM poll_votes WHERE poll_id = ? GROUP BY option_index', (poll_id,)).fetchall()
    
    counts = {i: 0 for i in range(len(options))}
    total_votes = 0
    for vr in v_rows:
        counts[vr['option_index']] = vr['cnt']
        total_votes += vr['cnt']

    options_data = []
    for idx, opt in enumerate(options):
        c = counts[idx]
        pct = round((c / total_votes * 100), 1) if total_votes > 0 else 0
        options_data.append({'index': idx, 'text': opt, 'votes': c, 'percentage': pct})

    conn.close()
    return jsonify({
        'success': True,
        'poll_id': poll_id,
        'user_voted_idx': option_index,
        'total_votes': total_votes,
        'options_data': options_data
    })

# ==================== EVENTS CRUD APIs ====================

@app.route('/api/create-event', methods=['POST'])
def create_event():
    current_user_id = session.get('student_id', 1)
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    category = request.form.get('category', 'Campus Life').strip()
    date_str = request.form.get('date_str', '').strip()
    location = request.form.get('location', '').strip()
    image_url = request.form.get('image_url', '').strip() or 'https://images.unsplash.com/photo-1511578314322-379afb476865?w=800&auto=format&fit=crop&q=80'

    if not title or not location or not date_str:
        return jsonify({'success': False, 'error': 'Required fields missing'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO events (title, description, category, date_str, location, image_url, host_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (title, description, category, date_str, location, image_url, current_user_id))
    cursor.execute('UPDATE students SET karma = karma + 20 WHERE id = ?', (current_user_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('events'))

@app.route('/api/edit-event/<int:event_id>', methods=['POST'])
def api_edit_event(event_id):
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    category = data.get('category', 'Campus Life').strip()
    date_str = data.get('date_str', '').strip()
    location = data.get('location', '').strip()
    image_url = data.get('image_url', '').strip()
    
    if not title or not location or not date_str:
        return jsonify({'success': False, 'error': 'Title, location and date required'}), 400
        
    update_event(event_id, title, description, category, date_str, location, image_url)
    return jsonify({'success': True})

@app.route('/api/delete-event/<int:event_id>', methods=['POST'])
def api_delete_event(event_id):
    delete_event(event_id)
    return jsonify({'success': True})

@app.route('/api/rsvp-event', methods=['POST'])
def rsvp_event():
    current_user_id = session.get('student_id', 1)
    data = request.get_json() or {}
    event_id = data.get('event_id')
    status = data.get('status')

    if not event_id or status not in ['going', 'interested', 'cant_go']:
        return jsonify({'success': False, 'error': 'Invalid parameters'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO event_rsvps (event_id, student_id, status)
        VALUES (?, ?, ?)
    ''', (event_id, current_user_id, status))
    conn.commit()

    going_count = cursor.execute("SELECT COUNT(*) FROM event_rsvps WHERE event_id = ? AND status = 'going'", (event_id,)).fetchone()[0]
    interested_count = cursor.execute("SELECT COUNT(*) FROM event_rsvps WHERE event_id = ? AND status = 'interested'", (event_id,)).fetchone()[0]
    conn.close()

    return jsonify({
        'success': True,
        'event_id': event_id,
        'user_rsvp': status,
        'going_count': going_count,
        'interested_count': interested_count
    })

# ==================== MESSAGING (DMs) APIs ====================

@app.route('/api/send-message', methods=['POST'])
def api_send_message():
    current_user_id = session.get('student_id', 1)
    data = request.get_json() or {}
    receiver_id = data.get('receiver_id')
    content = data.get('content', '').strip()

    if not receiver_id or not content:
        return jsonify({'success': False, 'error': 'Recipient and content required'}), 400

    msg_id = send_message(current_user_id, receiver_id, content)
    sender = get_student_by_id(current_user_id)
    
    return jsonify({
        'success': True,
        'message': {
            'id': msg_id,
            'sender_id': current_user_id,
            'sender_name': sender['name'],
            'sender_avatar': sender['avatar'],
            'content': content,
            'created_at': 'Just now'
        }
    })

@app.route('/api/messages/<int:target_id>')
def api_get_messages(target_id):
    current_user_id = session.get('student_id', 1)
    messages = get_conversation(current_user_id, target_id)
    return jsonify({'success': True, 'messages': messages})

# ==================== CONFESSIONS APIs ====================

@app.route('/api/create-confession', methods=['POST'])
def api_create_confession():
    content = request.form.get('content', '').strip()
    category = request.form.get('category', 'General').strip()
    if not content:
        return redirect(url_for('confessions'))
    create_confession(content, category)
    return redirect(url_for('confessions'))

@app.route('/api/upvote-confession', methods=['POST'])
def api_upvote_confession():
    data = request.get_json() or {}
    cid = data.get('confession_id')
    if not cid:
        return jsonify({'success': False}), 400
    votes = upvote_confession(cid)
    return jsonify({'success': True, 'upvotes': votes})

@app.route('/api/delete-confession/<int:confession_id>', methods=['POST'])
def api_delete_confession(confession_id):
    delete_confession(confession_id)
    return jsonify({'success': True})

# ==================== SOCIAL & SYSTEM APIs ====================

@app.route('/api/switch-user', methods=['POST'])
def switch_user():
    data = request.get_json() or {}
    new_user_id = data.get('student_id')
    if new_user_id:
        student = get_student_by_id(new_user_id)
        if student:
            session['student_id'] = student['id']
            return jsonify({'success': True, 'name': student['name'], 'handle': student['handle']})
    return jsonify({'success': False, 'error': 'Invalid user'}), 400

@app.route('/api/poke', methods=['POST'])
def poke_student():
    current_user_id = session.get('student_id', 1)
    data = request.get_json() or {}
    target_id = data.get('target_id')
    if not target_id or target_id == current_user_id:
        return jsonify({'success': False, 'error': 'Cannot poke yourself'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO pokes (sender_id, receiver_id, count, last_poked)
        VALUES (?, ?, 1, CURRENT_TIMESTAMP)
        ON CONFLICT(sender_id, receiver_id) DO UPDATE SET
            count = count + 1,
            last_poked = CURRENT_TIMESTAMP
    ''', (current_user_id, target_id))
    
    cursor.execute('UPDATE students SET karma = karma + 5 WHERE id = ?', (target_id,))
    count = cursor.execute('SELECT count FROM pokes WHERE sender_id = ? AND receiver_id = ?', (current_user_id, target_id)).fetchone()[0]
    target_name = cursor.execute('SELECT name FROM students WHERE id = ?', (target_id,)).fetchone()[0]
    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'message': f"You poked {target_name}! They have been poked {count} times by you.",
        'poke_count': count
    })

@app.route('/api/friend-action', methods=['POST'])
def friend_action():
    current_user_id = session.get('student_id', 1)
    data = request.get_json() or {}
    target_id = data.get('target_id')
    action = data.get('action')

    if not target_id or target_id == current_user_id:
        return jsonify({'success': False, 'error': 'Invalid target'}), 400

    conn = get_db()
    cursor = conn.cursor()

    if action == 'send':
        cursor.execute('''
            INSERT OR REPLACE INTO friendships (student_id_1, student_id_2, status)
            VALUES (?, ?, 'pending')
        ''', (current_user_id, target_id))
        new_status = 'requested'
    elif action == 'accept':
        cursor.execute('''
            UPDATE friendships SET status = 'friends'
            WHERE ((student_id_1 = ? AND student_id_2 = ?) OR (student_id_1 = ? AND student_id_2 = ?))
        ''', (current_user_id, target_id, target_id, current_user_id))
        new_status = 'friends'
    elif action in ['remove', 'decline']:
        cursor.execute('''
            DELETE FROM friendships 
            WHERE (student_id_1 = ? AND student_id_2 = ?) OR (student_id_1 = ? AND student_id_2 = ?)
        ''', (current_user_id, target_id, target_id, current_user_id))
        new_status = None
    else:
        conn.close()
        return jsonify({'success': False, 'error': 'Unknown action'}), 400

    conn.commit()
    conn.close()
    return jsonify({'success': True, 'friend_status': new_status})

@app.route('/api/follow-action', methods=['POST'])
def follow_action():
    current_user_id = session.get('student_id', 1)
    data = request.get_json() or {}
    target_id = data.get('target_id')

    if not target_id or target_id == current_user_id:
        return jsonify({'success': False, 'error': 'Invalid target'}), 400

    conn = get_db()
    cursor = conn.cursor()
    exists = cursor.execute('SELECT 1 FROM follows WHERE follower_id = ? AND following_id = ?', (current_user_id, target_id)).fetchone()
    
    if exists:
        cursor.execute('DELETE FROM follows WHERE follower_id = ? AND following_id = ?', (current_user_id, target_id))
        is_following = False
    else:
        cursor.execute('INSERT INTO follows (follower_id, following_id) VALUES (?, ?)', (current_user_id, target_id))
        is_following = True

    followers_count = cursor.execute('SELECT COUNT(*) FROM follows WHERE following_id = ?', (target_id,)).fetchone()[0]
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'is_following': is_following, 'followers_count': followers_count})

@app.route('/api/search-students')
def search_students_api():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    students = get_all_students(search=query)
    results = [{
        'id': s['id'],
        'name': s['name'],
        'handle': s['handle'],
        'avatar': s['avatar'],
        'department': s['department'],
        'batch_title': s['batch_title'],
        'dorm': s['dorm']
    } for s in students[:8]]
    return jsonify(results)

if __name__ == '__main__':
    init_db()
    print("Unofficial College Network running on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
