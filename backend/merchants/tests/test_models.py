from django.test import TestCase

from common.tests.helpers import make_merchant_category, make_user
from merchants.models import Merchant


class MerchantModelTest(TestCase):
    def setUp(self):
        self.user = make_user("01700000001", "1111111111")
        self.merchant = Merchant.objects.create(
            user=self.user,
            business_name="Test Store",
            category=make_merchant_category("retail", "Retail"),
        )

    def test_str(self):
        self.assertEqual(str(self.merchant), "Test Store (Retail)")

    def test_default_is_not_verified(self):
        self.assertFalse(self.merchant.is_verified)

    def test_verified_manager(self):
        Merchant.objects.create(
            user=make_user("01700000003", "3333333333"),
            business_name="Verified Shop",
            category=make_merchant_category("retail"),
            is_verified=True,
        )
        self.assertEqual(Merchant.verified.count(), 1)
        self.assertEqual(Merchant.objects.count(), 2)

    def test_user_relation(self):
        self.assertEqual(self.merchant.user, self.user)

    def test_ordering(self):
        Merchant.objects.create(
            user=make_user("01700000002", "2222222222"),
            business_name="A Store",
            category=make_merchant_category("retail"),
        )
        qs = Merchant.objects.all()
        self.assertEqual(qs.first().business_name, "A Store")

    def test_all_categories_valid(self):
        for i, key in enumerate(
            ["retail", "food", "transport", "utility", "health", "education"]
        ):
            phone = f"0170000{100 + i:0>4}"
            nid = str(1000000000 + i)
            m = Merchant.objects.create(
                user=make_user(phone, nid),
                business_name=f"Shop {key}",
                category=make_merchant_category(key),
            )
            self.assertEqual(m.category.key, key)

    def test_verified_manager_excludes_unverified(self):
        Merchant.objects.create(
            user=make_user("0170000099", "9999999999"),
            business_name="Not Verified",
            category=make_merchant_category("retail"),
        )
        self.assertEqual(Merchant.verified.count(), 0)

    def test_merchant_with_other_category(self):
        m = Merchant.objects.create(
            user=make_user("0170000098", "8888888888"),
            business_name="No Category",
            category=make_merchant_category("other", "Other"),
        )
        self.assertEqual(m.category.key, "other")
