from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book
from store.serializers import BookSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self) -> None:
        self.book_1 = Book.objects.create(name='Test book 1', author_name='Author 1', price=1500)
        self.book_2 = Book.objects.create(name='Test book Author 1', author_name='Author 2', price=1700)
        self.book_3 = Book.objects.create(name='Test book 3', author_name='Author 3', price=1500)
        self.url = reverse('book-list')

    def test_get(self):
        response = self.client.get(self.url)
        serializer_data = BookSerializer([self.book_1, self.book_2, self.book_3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_filter(self):
        # filter by price
        response = self.client.get(self.url, data={'price': 1500})
        serializer_data = BookSerializer([self.book_1, self.book_3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

        # filter by author_name
        response = self.client.get(self.url, data={'author_name': 'Author 1'})
        serializer_data = BookSerializer([self.book_1], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        response = self.client.get(self.url, data={'search': 'Author 1'})
        serializer_data = BookSerializer([self.book_1, self.book_2], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering(self):
        # ordering by price asc
        response = self.client.get(self.url, data={'ordering': 'price'})
        serializer_data = BookSerializer([self.book_1, self.book_3, self.book_2], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

        # ordering by author_name desc
        response = self.client.get(self.url, data={'ordering': '-author_name'})
        serializer_data = BookSerializer([self.book_3, self.book_2, self.book_1], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
