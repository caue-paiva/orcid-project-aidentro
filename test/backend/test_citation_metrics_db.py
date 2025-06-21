from django.test import TestCase
from config.models import User, Work, WorkAuthor, CitationTimeSeries
from unittest.mock import patch


class CitationMetricsDBTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="alice",
            email="alice@example.com",
            orcid_id="0000-0001-2345-6789",
        )
        self.work = Work.objects.create(
            title="My Test Paper",
            publication_year=2024,
            doi="10.9999/xyz123",
        )
        WorkAuthor.objects.create(
            work=self.work,
            user=self.user,
            author_order=1,
        )
        CitationTimeSeries.objects.create(
            user=self.user,
            year=2024,
            citations_count=10,
        )

    @patch("integrations.orcid_api.ORCIDAPIClient.get_citation_metrics_for_dashboard")
    def test_metrics_come_from_db(self, mock_fetch):
        metric = CitationTimeSeries.objects.get(user=self.user, year=2024)
        self.assertFalse(mock_fetch.called)
        self.assertEqual(metric.citations_count, 10)
