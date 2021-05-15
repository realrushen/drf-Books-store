from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.test import TestCase

from store.models import Book, UserBookRelation
from store.serializers import BookSerializer


class BookSerializerTestCase(TestCase):
    def setUp(self) -> None:
        self.user1 = User.objects.create(username='test_username1')
        self.user2 = User.objects.create(username='test_username2', first_name='Smith', last_name='Jack')
        self.user3 = User.objects.create(username='test_username3')

        self.book_1 = Book.objects.create(name='Test book 1', price=1500, author_name='Author 1', owner=self.user1)
        self.book_2 = Book.objects.create(name='Test book 2', price=1700, author_name='Author 2', owner=self.user1)

        UserBookRelation.objects.create(user=self.user1, book=self.book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=self.user2, book=self.book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=self.user3, book=self.book_1, like=True, rate=4)

        UserBookRelation.objects.create(user=self.user1, book=self.book_2, like=True, rate=3)
        UserBookRelation.objects.create(user=self.user2, book=self.book_2, like=True, rate=4)
        UserBookRelation.objects.create(user=self.user3, book=self.book_2, like=False)

    def test_ok(self):
        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            rating=Avg('userbookrelation__rate')
        ).order_by('id')
        data = BookSerializer(books, many=True).data
        expected_data = [
            {
                'id': self.book_1.id,
                'name': 'Test book 1',
                'price': '1500.00',
                'author_name': 'Author 1',
                'annotated_likes': 3,
                'rating': '4.67',
                'owner_name': 'test_username1',
                'readers': [
                    {
                        "username": "test_username1",
                        "first_name": "",
                        "last_name": ""
                    },
                    {
                        "username": "test_username2",
                        "first_name": "Smith",
                        "last_name": "Jack"
                    },
                    {
                        "username": "test_username3",
                        "first_name": "",
                        "last_name": ""
                    },

        ]
            },
            {
                'id': self.book_2.id,
                'name': 'Test book 2',
                'price': '1700.00',
                'author_name': 'Author 2',
                'annotated_likes': 2,
                'rating': '3.50',
                'owner_name': 'test_username1',
                'readers': [
                    {
                        "username": "test_username1",
                        "first_name": "",
                        "last_name": ""
                    },
                    {
                        "username": "test_username2",
                        "first_name": "Smith",
                        "last_name": "Jack"
                    },
                    {
                        "username": "test_username3",
                        "first_name": "",
                        "last_name": ""
                    },
                ]
            },
        ]
        self.assertEqual(expected_data, data)


