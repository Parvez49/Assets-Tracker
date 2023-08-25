from django.test import TestCase

# Create your tests here.

from .models import Company

class CompanyModelTestCase(TestCase):
    def setUp(self):
        Company.objects.create(name='company', registration_no='COMP123')

    def test_company_name(self):
        company = Company.objects.get(registration_no='COMP123')
        self.assertEqual(company.name, 'company')

    def test_company_registration_no(self):
        company = Company.objects.get(name='company')
        self.assertEqual(company.registration_no, 'COMP123')

    def test_company_str_representation(self):
        company = Company.objects.get(name='company')
        self.assertEqual(str(company), 'company')
