import json
import pdb

from django.contrib.auth.models import User
from django.db.models import When, Case, Count, Avg, F
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from store.models import Book, UserBookRelation
from store.serializers import BookSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(username='test_username')
        self.user2 = User.objects.create(username='test_username2')
        self.user_staff = User.objects.create(username='test_username3', is_staff=True)

        self.book_1 = Book.objects.create(name='Test book 1', author_name='Author 1', price=1500, owner=self.user,
                                          discount=100)
        self.book_2 = Book.objects.create(name='Test book Author 1', author_name='Author 2', price=1700,
                                          owner=self.user)
        self.book_3 = Book.objects.create(name='Test book 3', author_name='Author 3', price=1500, owner=self.user)
        self.books = Book.objects.all().annotate(annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
                                                 rating=Avg('userbookrelation__rate'),
                                                 price_with_discount=F('price')-F('discount'),
                                                 )
        UserBookRelation.objects.create(user=self.user, book=self.book_1, rate=5, like=True)
        self.url = reverse('book-list')

    def test_get(self):
        response = self.client.get(self.url)
        serializer_data = BookSerializer(self.books.order_by('id'), many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

        self.assertEqual('5.00', serializer_data[0]['rating'])
        self.assertEqual(1, serializer_data[0]['annotated_likes'])

        self.assertEqual('1400.00', serializer_data[0]['price_with_discount'])

    def test_get_filter(self):
        # filter by price
        response = self.client.get(self.url, data={'price': 1500})
        serializer_data = BookSerializer(self.books.filter(id__in=[self.book_1.id, self.book_3.id]), many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

        # filter by author_name
        response = self.client.get(self.url, data={'author_name': 'Author 1'})
        serializer_data2 = BookSerializer(self.books.filter(id=self.book_1.id), many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(serializer_data2, response.data)

    def test_get_search(self):
        response = self.client.get(self.url, data={'search': 'Author 1'})
        serializer_data = BookSerializer(self.books.filter(id__in=[self.book_1.id, self.book_2.id]).order_by('id'), many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering(self):
        # ordering by price asc
        response = self.client.get(self.url, data={'ordering': 'price, author_name'})
        serializer_data = BookSerializer(self.books.order_by('price', 'author_name'), many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

        # ordering by author_name desc
        response = self.client.get(self.url, data={'ordering': '-author_name'})
        serializer_data = BookSerializer(self.books.order_by('-author_name'), many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        books_before = Book.objects.all().count()
        data = {
            "name": "Automate the Boring Stuff with Python",
            "price": "2000.00",
            "author_name": "Al Sweigart",
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)

        response = self.client.post(self.url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(books_before + 1, Book.objects.all().count())
        self.assertEqual(self.user, Book.objects.last().owner)

    def test_update(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": 1550,
            "author_name": self.book_1.author_name,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.book_1.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1550, self.book_1.price)

    def test_update_not_owner(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": 1550,
            "author_name": self.book_1.author_name,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.book_1.refresh_from_db()
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                                code='permission_denied')}, response.data)
        self.assertEqual(1500, self.book_1.price)

    def test_delete(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        books_before = Book.objects.all().count()
        self.client.force_login(self.user)
        response = self.client.delete(url, content_type='application-json')
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(books_before - 1, Book.objects.all().count())

    def test_get_one_book(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        serializer_data = BookSerializer(self.books[0]).data
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_update_not_owner_but_staff(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": 1550,
            "author_name": self.book_1.author_name,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user_staff)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(1550, self.book_1.price)


class BookRelationTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(username='test_username')
        self.user2 = User.objects.create(username='test_username2')
        self.book_1 = Book.objects.create(name='Test book 1', author_name='Author 1', price=1500, owner=self.user)
        self.book_2 = Book.objects.create(name='Test book Author 1', author_name='Author 2', price=1700,
                                          owner=self.user)

    def test_like_and_in_bookmarks(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            "like": True,
        }
        json_data = json.dumps(data)
        self.client.force_login(user=self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book_1)
        self.assertTrue(relation.like)

        data = {
            "in_bookmarks": True,
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book_1)
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        rate_value = 3
        data = {
            "rate": rate_value,
        }
        json_data = json.dumps(data)
        self.client.force_login(user=self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book_1)
        self.assertEqual(rate_value, relation.rate)
