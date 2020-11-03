from django.contrib.auth.models import User
from django.test import TestCase

from store.models import Book
from store.serializers import BookSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        user = User.objects.create(username='test_username')
        self.client.force_login(user)
        book_1 = Book.objects.create(name='Test book 1', price=1500, author_name='Author 1', owner=user)
        book_2 = Book.objects.create(name='Test book 2', price=1700, author_name='Author 2', owner=user)
        data = BookSerializer([book_1, book_2], many=True).data
        expected_data = [
            {
                'id': book_1.id,
                'name': 'Test book 1',
                'price': '1500.00',
                'author_name': 'Author 1',
                'owner': user.id,
            },
            {
                'id': book_2.id,
                'name': 'Test book 2',
                'price': '1700.00',
                'author_name': 'Author 2',
                'owner': user.id,
            },
        ]
        self.assertEqual(expected_data, data)
