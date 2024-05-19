import unittest
from main import app, db
from models import UserModel


class FlaskAppTests(unittest.TestCase):
    def create_app(self):
        app.config.from_object('config.TestConfig')
        return app

    def setUp(self):
        self.app = self.create_app()
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_register_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>Sign Up</title>', response.data)

    def test_login_page_loads(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>Log In</title>', response.data)

    def test_successful_register(self):
        response = self.client.post('/', data=dict(username='123', password='123'), follow_redirects=True)
        self.assertIn(b'<p>You have successfully registered.</p>', response.data)
        created_user = UserModel.query.filter_by(username='123').first()
        self.assertIsNotNone(created_user)
        self.assertEqual(created_user.username, '123')

    def test_failed_register_short_data(self):
        response = self.client.post('/', data=dict(username='12', password='12'))
        self.assertIn(b'<p>Username/password should contain at least 3 characters!</p>', response.data)
        created_user = UserModel.query.filter_by(username='12').first()
        self.assertIsNone(created_user)

    def test_failed_register_username_taken(self):
        self.client.post('/', data=dict(username='123', password='123'))
        response = self.client.post('/', data=dict(username='123', password='123'))
        self.assertIn(b'<p>Username already taken.</p>', response.data)
        users = UserModel.query.filter_by(username='123').all()
        self.assertEqual(len(users), 1)

    def test_successful_login(self):
        self.client.post('/', data=dict(username='123', password='123'))
        response = self.client.post('/login', data=dict(username='123', password='123'), follow_redirects=True)
        self.assertIn(b'<h1>Hi, 123! You logged in.</h1>', response.data)

    def test_failed_login(self):
        response = self.client.post('/login', data=dict(username='123', password='123'), follow_redirects=True)
        self.assertIn(b'<p>User not found.</p>', response.data)

    def test_content_page_loads(self):
        self.client.post('/', data=dict(username='123', password='123'))
        self.client.post('/login', data=dict(username='123', password='123'))
        response = self.client.get('/content', follow_redirects=True)
        self.assertIn(b'Hi, 123! You logged in.', response.data)

    def test_content_page_blocks(self):
        response = self.client.get('/content', follow_redirects=True)
        self.assertIn(b'<title>Log In</title>', response.data)


if __name__ == '__main__':
    unittest.main()
