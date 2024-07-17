from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
import json


class IndexViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_view_get(self):
        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather/index.html')

        self.assertIn('search_history', response.context)
        search_history = response.context['search_history']
        self.assertIsInstance(search_history, list)

    @patch('requests.get')
    def test_index_view_post_success(self, mock_get):
        mock_weather_data = {
            'weather': [{'icon': '01d'}],
            'main': {'temp': 25, 'feels_like': 26, 'temp_min': 20, 'temp_max': 30}
        }
        mock_response = mock_get.return_value
        mock_response.json.return_value = mock_weather_data

        response = self.client.post(reverse('index'), {'city': 'Moscow'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather/index.html')

        self.assertIn('icon', response.context)
        self.assertIn('temperature', response.context)
        self.assertIn('temperature_feels', response.context)
        self.assertIn('min_temp', response.context)
        self.assertIn('max_temp', response.context)
        self.assertIn('city', response.context)
        self.assertIn('search_history', response.context)

        self.assertIn('search_history', response.cookies)
        cookies_data = json.loads(response.cookies['search_history'].value)
        self.assertIn('Moscow', cookies_data)

    @patch('requests.get')
    def test_index_view_post_city_not_found(self, mock_get):
        mock_get.return_value.json.side_effect = Exception('City not found')

        response = self.client.post(reverse('index'), {'city': 'UnknownCity'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather/index.html')

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Города UnknownCity не существует, введите информацию заново')
