import unittest
import json
import os
from app import app
from models import init_db, DB_PATH
from seed_data import seed_database

class CollegeNetworkFullTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        seed_database()

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    # Base page views
    def test_feed_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'[thecollege]', response.data)
        self.assertIn(b'The Wire', response.data)

    def test_directory_page(self):
        response = self.client.get('/directory')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'The Undergraduate Directory', response.data)
        self.assertIn(b'Amulya Srivastava', response.data)

    def test_directory_search(self):
        response = self.client.get('/directory?q=Zuckerberg')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Mark Zuckerberg', response.data)

    def test_profile_page(self):
        response = self.client.get('/profile/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Amulya Srivastava', response.data)
        self.assertIn(b'[ Information ]', response.data)
        self.assertIn(b'Edit Profile', response.data)

    def test_leaderboard_page(self):
        response = self.client.get('/leaderboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Campus Karma & Department Leaderboards', response.data)

    def test_polls_page(self):
        response = self.client.get('/polls')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Pulse of the Quad', response.data)

    def test_events_page(self):
        response = self.client.get('/events')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Events, Hackathons', response.data)

    def test_messages_page(self):
        response = self.client.get('/messages')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Campus Messenger', response.data)

    def test_confessions_page(self):
        response = self.client.get('/confessions')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'The Underground Wire', response.data)

    # Editing and CRUD APIs ("Everything is Editable")
    def test_edit_student_api(self):
        response = self.client.post('/api/edit-student/2', json={
            'canteen_fav': 'Mark\'s Special Double Espresso',
            'gpa': 3.99
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['student']['canteen_fav'], 'Mark\'s Special Double Espresso')

    def test_create_student_api(self):
        import time
        unique_roll = f'TEST{int(time.time()) % 100000}'
        response = self.client.post('/api/create-student', json={
            'name': 'Jordan Bell',
            'handle': f'jordanbell_{int(time.time()) % 100000}',
            'roll_no': unique_roll,
            'department': 'Computer Science',
            'batch_title': 'Freshman',
            'batch_year': 2029,
            'gpa': 4.0,
            'dorm': 'Weld Hall #401'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIsNotNone(data['id'])

    def test_edit_post_api(self):
        response = self.client.post('/api/edit-post/2', json={
            'content': 'Kirkland House cluster just got upgraded with high-speed fiber!',
            'tags': '#Kirkland #Fiber #Fast'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    def test_edit_poll_api(self):
        response = self.client.post('/api/edit-poll/1', json={
            'question': 'Which midnight campus food spot is undisputed king? (Updated)',
            'category': 'Food & Hangouts'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    def test_edit_event_api(self):
        response = self.client.post('/api/edit-event/1', json={
            'title': 'TechnoPulse 2026: 48-Hour National Hackathon',
            'description': 'Upgraded to 48 hours with more prizes!',
            'category': 'Hackathon',
            'date_str': 'Saturday, Sept 14 • 08:00 AM',
            'location': 'Student Activity Center Main Hall',
            'image_url': 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=800&auto=format&fit=crop&q=80'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    # Direct Messaging
    def test_send_and_get_message(self):
        response = self.client.post('/api/send-message', json={
            'receiver_id': 2,
            'content': 'Hey Mark, did you check the updated course rankings?'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['message']['content'], 'Hey Mark, did you check the updated course rankings?')

        # Retrieve conversation
        conv_response = self.client.get('/api/messages/2')
        self.assertEqual(conv_response.status_code, 200)
        conv_data = json.loads(conv_response.data)
        self.assertTrue(conv_data['success'])
        self.assertTrue(len(conv_data['messages']) > 0)

    # Social and Poke
    def test_poke_api(self):
        response = self.client.post('/api/poke', json={'target_id': 2})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    def test_upvote_confession(self):
        response = self.client.post('/api/upvote-confession', json={'confession_id': 1})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

if __name__ == '__main__':
    unittest.main()
