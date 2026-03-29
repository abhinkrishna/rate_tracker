from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rates.models import Provider, Currency, RateType, Rate
from django.utils import timezone
import datetime

class RateAPITests(APITestCase):

    def setUp(self):
        # Create user and token for auth
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Setup initial data
        self.provider = Provider.objects.create(name='Provider A')
        self.provider_b = Provider.objects.create(name='Provider B')
        self.currency = Currency.objects.create(name='US Dollar', code='USD')
        self.rate_type = RateType.objects.create(name='spot')
        
        self.today = timezone.now().date()
        self.yesterday = self.today - datetime.timedelta(days=1)
        
        # Rate for Provider A today
        self.rate1 = Rate.objects.create(
            provider=self.provider,
            currency=self.currency,
            rate_type=self.rate_type,
            rate_value='1.0',
            effective_date=self.today,
            ingestion_ts=timezone.now(),
            raw_response_id='raw1'
        )
        # Rate for Provider A yesterday
        self.rate2 = Rate.objects.create(
            provider=self.provider,
            currency=self.currency,
            rate_type=self.rate_type,
            rate_value='1.1',
            effective_date=self.yesterday,
            ingestion_ts=timezone.now(),
            raw_response_id='raw2'
        )
        # Rate for Provider B today
        self.rate3 = Rate.objects.create(
            provider=self.provider_b,
            currency=self.currency,
            rate_type=self.rate_type,
            rate_value='2.0',
            effective_date=self.today,
            ingestion_ts=timezone.now(),
            raw_response_id='raw3'
        )
        
    def test_get_latest_rates(self):
        # Unauthenticated access should be allowed for read endpoints
        self.client.credentials() 
        response = self.client.get(reverse('rates-latest'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return most recent rate per provider (so 2 results)
        data = response.json().get('data')
        self.assertEqual(len(data), 2)
        provider_names = [d['provider'] for d in data]
        self.assertIn('Provider A', provider_names)
        self.assertIn('Provider B', provider_names)

        # Check filtering by type
        response = self.client.get(reverse('rates-latest') + "?type=spot")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get('data')), 2)

        response = self.client.get(reverse('rates-latest') + "?type=forward")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get('data')), 0)
        
    def test_get_history_rates(self):
        self.client.credentials()
        # Missing params should return bad request
        response = self.client.get(reverse('rates-history'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response = self.client.get(reverse('rates-history') + "?provider=Provider A&type=spot")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json().get('data')
        # Provider A has 2 rates
        self.assertEqual(len(data['results']), 2)
        self.assertEqual(data['count'], 2)
        
        # Test date filters
        response = self.client.get(reverse('rates-history') + f"?provider=Provider A&type=spot&from={self.today}&to={self.today}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json().get('data')
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['rate_value'], '1.0000000000')

    def test_post_ingest_rate(self):
        payload = {
            "provider_name": "Provider C",
            "currency_code": "EUR",
            "rate_type_name": "spot",
            "rate_value": "0.85",
            "effective_date": "2023-10-01",
            "raw_response_id": "raw-webhook-1"
        }
        # Authenticated
        response = self.client.post(reverse('rates-ingest'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Rate.objects.filter(raw_response_id="raw-webhook-1").exists())
        
        # Test idempotency / update
        payload['rate_value'] = "0.90"
        response = self.client.post(reverse('rates-ingest'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        from decimal import Decimal
        self.assertEqual(Rate.objects.get(raw_response_id="raw-webhook-1").rate_value, Decimal("0.90"))

    def test_post_ingest_rate_unauthenticated(self):
        self.client.credentials() # clear tokens
        payload = {}
        response = self.client.post(reverse('rates-ingest'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
