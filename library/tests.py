from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Book, Favorite
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class RecommendationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_authenticate(user=self.user)

        # Create sample books
        self.book1 = Book.objects.create(title='Django for Beginners', isbn='1234567890123', description='Learn Django step by step.')
        self.book2 = Book.objects.create(title='Advanced Django', isbn='1234567890124', description='Deep dive into Django.')
        self.book3 = Book.objects.create(title='Python Crash Course', isbn='1234567890125', description='Learn Python quickly.')
        # Compute vectors for sample books if necessary

    def test_recommendations_with_no_favorites(self):
        response = self.client.get('/api/recommendations/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_recommendations_with_favorites(self):
        Favorite.objects.create(user=self.user, book=self.book1)
        response = self.client.get('/api/recommendations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) <= 5)
