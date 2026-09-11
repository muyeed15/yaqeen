import os
import random
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import CharityCause, Foundation, Nominee, User
from agents.models import Agent, AgentTransaction
from banking.models import Bank, BankAccount, BankTransaction
from billpay.models import Biller, BillerCategory, BillPayment
from cards.models import Card
from charity.models import HawlTracking, Sadaqah, SadaqahJariyah, ZakatPayment
from common.utils import record_transaction
from loans.models import QardHasanApplication, QardHasanProduct
from merchants.models import Merchant, MerchantCategory
from notifications.models import Notification
from recharge.models import DataPack, Operator, OperatorType, RechargeTransaction
from remittance.models import RemittancePartner, RemittanceTransaction
from savings.models import MudarabahAccount, MudarabahContribution, MudarabahPlan
from support.models import SupportCategory
from tickets.models import TicketBooking, TicketCategory, TicketProvider, TicketTrip
from transactions.models import Transaction

PASSWORD = "12345678"

TEAM = [
    ("Dipra", "01827668054"),
    ("Tasdida", "01745583561"),
    ("Arafat", "01756469770"),
    ("Ayeman", "01880369079"),
    ("Samara", "01822995689"),
    ("Selim", "01612195390"),
    ("Sijan", "01708366765"),
    ("Tamim", "01303855526"),
    ("Zabid", "01326175976"),
    ("Nabil", "01835391536"),
]

BD_NAMES = [
    "Rahim Uddin",
    "Karim Mia",
    "Sumaiya Akter",
    "Nasrin Begum",
    "Rafiq Islam",
    "Jahanara Khatun",
    "Mizanur Rahman",
    "Shahida Parvin",
    "Abul Hossain",
    "Fatema Begum",
    "Nurul Islam",
    "Roksana Akter",
    "Shahidul Alam",
    "Mosammat Rina",
    "Belal Hossain",
    "Sharmin Sultana",
    "Aminul Islam",
    "Halima Khatun",
    "Monir Hossain",
    "Taslima Begum",
    "Sabbir Ahmed",
    "Nusrat Jahan",
    "Delwar Hossain",
    "Moriam Akter",
    "Mahbubur Rahman",
]

BD_MERCHANTS = [
    ("Aarong", "retail"),
    ("Shajgoj", "retail"),
    ("Daraz Bangladesh", "retail"),
    ("Kacchi Bhai", "food"),
    ("Haji Biriyani House", "food"),
    ("Star Kabab & Restaurant", "food"),
    ("Pathao", "transport"),
    ("Shohoz Rides", "transport"),
    ("Obhai", "transport"),
    ("DESCO", "utility"),
    ("Titas Gas", "utility"),
    ("Ibn Sina Hospital", "health"),
    ("Brac University", "education"),
    ("Star Cineplex", "entertainment"),
]

BD_FOUNDATIONS = [
    ("BRAC", "education", "NGO-0001"),
    ("Jaago Foundation", "education", "NGO-0002"),
    ("Emon Foundation", "orphan", "NGO-0003"),
    ("Musk Foundation", "health", "NGO-0004"),
    ("Al-Markazul Islami", "masjid", "NGO-0005"),
    ("Sharique Foundation", "poverty", "NGO-0006"),
    ("Bidyanondo Foundation", "education", "NGO-0007"),
    ("Dhaka Ahsania Mission", "health", "NGO-0008"),
    ("Sajida Foundation", "health", "NGO-0009"),
    ("Uttaran", "water", "NGO-0010"),
]

CHARITY_CAUSES = [
    ("education", "Education", "GraduationCap"),
    ("health", "Health", "HeartPulse"),
    ("poverty", "Poverty Alleviation", "HandCoins"),
    ("orphan", "Orphan Support", "Users"),
    ("masjid", "Masjid Development", "Landmark"),
    ("water", "Water & Sanitation", "Droplets"),
    ("emergency", "Emergency Relief", "LifeBuoy"),
    ("general", "General", "Heart"),
]

SUPPORT_CATEGORIES = [
    ("general", "General"),
    ("transaction", "Transaction"),
    ("account", "Account"),
    ("card", "Card"),
    ("recharge", "Recharge"),
    ("bill", "Bill"),
    ("loan", "Loan"),
    ("ticket", "Ticket"),
    ("other", "Other"),
]

BD_OPERATORS = [
    ("Grameenphone", "gp", "prepaid"),
    ("Banglalink", "bl", "prepaid"),
    ("Robi", "robi", "prepaid"),
    ("Airtel", "airtel", "prepaid"),
    ("Teletalk", "teletalk", "prepaid"),
]

BD_BILLERS = [
    ("DESCO", "electricity", "ELEC-001"),
    ("DPDC", "electricity", "ELEC-002"),
    ("Titas Gas", "gas", "GAS-001"),
    ("Dhaka WASA", "water", "WTR-001"),
    ("BTCL Internet", "internet", "INT-001"),
    ("DOT Internet", "internet", "INT-002"),
    ("Akash DTH", "tv", "TV-001"),
    ("IUB", "education", "EDU-001"),
    ("NSU", "education", "EDU-002"),
    ("AIUB", "education", "EDU-003"),
    ("DIU", "education", "EDU-004"),
]

BD_BANKS = [
    ("Islami Bank Bangladesh", "IBBL"),
    ("Shahjalal Islami Bank", "SJIBL"),
    ("Al-Arafah Islami Bank", "ALARAF"),
    ("Social Islami Bank", "SIBL"),
    ("First Security Islami Bank", "FSIB"),
    ("EXIM Bank (Islami Banking)", "EXIM"),
    ("Union Bank", "UNION"),
    ("ICB Islamic Bank", "ICB"),
]

BD_DISTRICTS = [
    "Dhaka",
    "Chattogram",
    "Rajshahi",
    "Khulna",
    "Sylhet",
    "Barishal",
    "Rangpur",
    "Mymensingh",
]
BD_THANAS = {
    "Dhaka": ["Gulshan", "Mirpur", "Dhanmondi", "Uttara", "Mohammadpur"],
    "Chattogram": ["Agrabad", "GEC", "Nasirabad"],
    "Sylhet": ["Zindabazar", "Ambarkhana"],
}

REMITTANCE_PARTNERS = [
    ("Western Union", "USA", "USD", Decimal("110.00")),
    ("MoneyGram", "USA", "USD", Decimal("109.00")),
    ("Ria Money Transfer", "UK", "GBP", Decimal("137.00")),
    ("Xpress Money", "UAE", "AED", Decimal("30.00")),
    ("Al Ansari Exchange", "UAE", "AED", Decimal("29.80")),
    ("Malaysia Remit", "Malaysia", "MYR", Decimal("24.00")),
]

TICKET_PROVIDERS = [
    ("Shohoz Bus", "bus"),
    ("Green Line Paribahan", "bus"),
    ("Hanif Enterprise", "bus"),
    ("Bangladesh Railway", "train"),
    ("US-Bangla Airlines", "airline"),
    ("Biman Bangladesh", "airline"),
    ("Star Cineplex", "cinema"),
    ("Blockbuster Cinemas", "cinema"),
    ("BIWTC Ferry", "ferry"),
    ("Green Line Waterways", "ferry"),
]

TRAIN_COACHES = ["ক", "খ", "গ", "ঘ", "ঙ", "চ", "ছ", "জ", "ঝ", "ঞ"]


class Command(BaseCommand):
    help = "Seed the database with realistic Bangladeshi fintech data"

    USER_COUNT = 25

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Clearing old data..."))
        self._clear()

        self.stdout.write("Seeding users...")
        users = self._seed_users()

        self.stdout.write("Seeding team...")
        self._seed_team()

        self.stdout.write("Seeding superuser...")
        self._seed_superuser()

        self.stdout.write("Seeding nominees...")
        self._seed_nominees(users)

        self.stdout.write("Seeding merchants...")
        self._seed_merchant_categories()
        merchants = self._seed_merchants(users)

        self.stdout.write("Seeding foundations...")
        self._seed_charity_causes()
        foundations = self._seed_foundations()
        self._seed_support_categories()

        self.stdout.write("Seeding cards...")
        self._seed_cards(users)

        self.stdout.write("Seeding operators...")
        self._seed_operator_types()
        operators = self._seed_operators()

        self.stdout.write("Seeding data packs...")
        self._seed_data_packs(operators)

        self.stdout.write("Seeding billers...")
        self._seed_biller_categories()
        billers = self._seed_billers()

        self.stdout.write("Seeding banks...")
        banks = self._seed_banks()

        self.stdout.write("Seeding bank accounts...")
        self._seed_bank_accounts(users, banks)

        self.stdout.write("Seeding agents...")
        agents = self._seed_agents()

        self.stdout.write("Seeding Qard Hasan products...")
        loan_products = self._seed_loan_products()

        self.stdout.write("Seeding remittance partners...")
        remit_partners = self._seed_remittance_partners()

        self.stdout.write("Seeding ticket providers...")
        self._seed_ticket_categories()
        ticket_providers = self._seed_ticket_providers()

        self._seed_icons()

        self.stdout.write("Seeding Mudarabah plans...")
        plans = self._seed_mudarabah_plans()

        self.stdout.write("Seeding Mudarabah accounts...")
        self._seed_mudarabah_accounts(users, plans)

        self.stdout.write("Seeding transactions...")
        self._seed_transactions(users, merchants)

        self.stdout.write("Seeding agent transactions...")
        self._seed_agent_transactions(users, agents)

        self.stdout.write("Seeding recharges...")
        self._seed_recharges(users, operators)

        self.stdout.write("Seeding bill payments...")
        self._seed_bill_payments(users, billers)

        self.stdout.write("Seeding bank transactions...")
        self._seed_bank_transactions(users, banks)

        self.stdout.write("Seeding Qard Hasan applications...")
        self._seed_loan_applications(users, loan_products)

        self.stdout.write("Seeding remittances...")
        self._seed_remittances(users, remit_partners)

        self.stdout.write("Seeding ticket bookings...")
        self._seed_ticket_bookings(users, ticket_providers)

        self.stdout.write("Seeding zakat payments...")
        self._seed_zakat(users, foundations)

        self.stdout.write("Seeding sadaqah...")
        self._seed_sadaqah(users, foundations)

        self.stdout.write("Seeding notifications...")
        self._seed_notifications(users)

        self.stdout.write("Seeding Hawl tracking...")
        self._seed_hawl_tracking(users)

        self.stdout.write("Seeding Sadaqah Jariyah...")
        self._seed_sadaqah_jariyah(users, foundations)

        self.stdout.write("Ensuring minimum balances...")
        self._ensure_minimum_balances(users)

        self.stdout.write(self.style.SUCCESS("\nSeeding complete."))
        self._print_summary(users, merchants, foundations)

    def _clear_media(self):
        media_root = Path(settings.MEDIA_ROOT)
        if media_root.exists():
            for p in media_root.rglob("*"):
                if p.is_file():
                    p.unlink()
        media_root.mkdir(parents=True, exist_ok=True)

    def _clear(self):
        self._clear_media()
        TicketBooking.objects.all().delete()
        TicketTrip.objects.all().delete()
        TicketProvider.objects.all().delete()
        TicketCategory.objects.all().delete()
        RemittanceTransaction.objects.all().delete()
        RemittancePartner.objects.all().delete()
        QardHasanApplication.objects.all().delete()
        QardHasanProduct.objects.all().delete()
        BankTransaction.objects.all().delete()
        BankAccount.objects.all().delete()
        Bank.objects.all().delete()
        BillPayment.objects.all().delete()
        Biller.objects.all().delete()
        BillerCategory.objects.all().delete()
        AgentTransaction.objects.all().delete()
        Agent.objects.all().delete()
        RechargeTransaction.objects.all().delete()
        DataPack.objects.all().delete()
        Operator.objects.all().delete()
        OperatorType.objects.all().delete()
        Nominee.objects.all().delete()
        SadaqahJariyah.objects.all().delete()
        HawlTracking.objects.all().delete()
        MudarabahContribution.objects.all().delete()
        MudarabahAccount.objects.all().delete()
        MudarabahPlan.objects.all().delete()
        Sadaqah.objects.all().delete()
        ZakatPayment.objects.all().delete()
        Notification.objects.all().delete()
        Transaction.objects.all().delete()
        Card.objects.all().delete()
        Merchant.objects.all().delete()
        MerchantCategory.objects.all().delete()
        Foundation.objects.all().delete()
        CharityCause.objects.all().delete()
        team_phones = [phone for _, phone in TEAM]
        User.objects.filter(is_superuser=False).exclude(phone__in=team_phones).delete()

    def _seed_users(self):
        users = []
        names = random.sample(BD_NAMES, min(self.USER_COUNT, len(BD_NAMES)))
        for name in names:
            user = User.objects.create_user(
                phone=self._unique_phone(),
                password=PASSWORD,
                full_name=name,
                nid=self._unique_nid(),
                is_verified=random.choices([True, False], weights=[80, 20])[0],
            )
            user.wallet.balance = Decimal(str(random.randint(500, 50000)))
            user.wallet.status = random.choices(["active", "frozen"], weights=[90, 10])[
                0
            ]
            user.wallet.save(update_fields=["balance", "status"])
            users.append(user)
        return users

    def _seed_team(self):
        team = []
        fee_rate = Decimal(str(settings.TRANSFER_FEE_PERCENT)) / Decimal("100")
        for name, phone in TEAM:
            user, new = User.objects.get_or_create(
                phone=phone,
                defaults={"full_name": name, "nid": self._unique_nid()},
            )
            user.set_password(phone)
            user.is_verified = True
            user.wallet.balance = Decimal(str(random.randint(50000, 150000)))
            user.wallet.status = "active"
            user.wallet.save(update_fields=["balance", "status"])
            user.save(update_fields=["is_verified", "password"])
            if not Card.objects.filter(user=user).exists():
                card = Card(
                    user=user,
                    card_type="debit",
                    cardholder_name=name,
                    expiry_month=random.randint(1, 12),
                    expiry_year=2029,
                    status="active",
                    card_network=random.choice(["visa", "mastercard"]),
                )
                card.set_number(
                    "4" + str(random.randint(100000000000000, 999999999999999))[:15]
                )
                card.save()
            team.append(user)
            self.stdout.write(f"  + {name} {phone}  ৳{user.wallet.balance}")

        for _ in range(30):
            s, r = random.sample(team, 2)
            a = Decimal(str(random.randint(100, 5000)))
            f = (a * fee_rate).quantize(Decimal("0.01"))
            if s.wallet.balance < a + f:
                continue
            s.wallet.balance -= a + f
            r.wallet.balance += a
            s.wallet.save(update_fields=["balance"])
            r.wallet.save(update_fields=["balance"])
            Transaction.objects.create(
                sender=s,
                receiver=r,
                amount=a,
                fee=f,
                transaction_type="send",
                status="completed",
                note=random.choice(
                    [
                        "Lunch bill",
                        "Chai party",
                        "Team dinner",
                        "Gift contrib",
                        "Travel fare",
                    ]
                ),
                created_at=self._past(60),
            )

        self.stdout.write(f"  + {len(team)} team members, ~30 transfers between them")
        return team

    def _seed_superuser(self):
        phone = "01772224381"
        user, new = User.objects.get_or_create(
            phone=phone,
            defaults={
                "full_name": "Super Admin",
                "nid": self._unique_nid(),
                "is_staff": True,
                "is_superuser": True,
            },
        )
        user.set_password(phone)
        if not user.is_superuser:
            user.is_staff = True
            user.is_superuser = True
        user.is_verified = True
        user.wallet.balance = Decimal("9999999")
        user.wallet.status = "active"
        user.wallet.save(update_fields=["balance", "status"])
        user.save(update_fields=["is_verified", "password", "is_staff", "is_superuser"])
        self.stdout.write(f"  + Superuser: {phone}  ৳{user.wallet.balance}")

    def _seed_nominees(self, users):
        count = 0
        relations = list(Nominee.RELATION_CHOICES)
        for user in random.sample(users, min(10, len(users))):
            Nominee.objects.create(
                user=user,
                full_name=random.choice(BD_NAMES),
                phone=self._unique_phone(),
                nid=self._unique_nid(),
                relationship=random.choice(relations)[0],
                is_primary=True,
            )
            count += 1
        self.stdout.write(f"  + {count} nominees")

    def _seed_charity_causes(self):
        for key, label, icon in CHARITY_CAUSES:
            CharityCause.objects.update_or_create(
                key=key,
                defaults={"label": label, "icon": icon, "is_active": True},
            )
        self.stdout.write(f"  + {len(CHARITY_CAUSES)} charity causes")

    def _seed_support_categories(self):
        for key, label in SUPPORT_CATEGORIES:
            SupportCategory.objects.update_or_create(
                key=key,
                defaults={"label": label, "is_active": True},
            )
        self.stdout.write(f"  + {len(SUPPORT_CATEGORIES)} support categories")

    def _seed_icons(self):
        icons_dir = Path(settings.BASE_DIR).parent / "extra" / "icons"
        if not icons_dir.exists():
            self.stdout.write("  ! extra/icons not found, skipping icons")
            return

        for sub in ["logos", "billers", "tickets"]:
            folder = Path(settings.MEDIA_ROOT) / sub
            if folder.exists():
                for p in folder.iterdir():
                    if p.is_file():
                        p.unlink()

        count = 0

        def save_icon(obj, field_name, source_path):
            nonlocal count
            with open(source_path, "rb") as fh:
                content = fh.read()
            getattr(obj, field_name).save(
                os.path.basename(source_path), ContentFile(content), save=True
            )
            count += 1

        for code in ["gp", "bl", "robi", "airtel", "teletalk"]:
            src = icons_dir / "operators" / f"{code}.svg"
            if src.exists():
                operator = Operator.objects.filter(operator_code=code).first()
                if operator:
                    save_icon(operator, "logo", src)

        biller_map = {
            "education/iub.svg": "IUB",
            "education/diu.svg": "DIU",
            "education/nsu.svg": "NSU",
            "education/aiub.svg": "AIUB",
            "tv/akash_dth.svg": "Akash DTH",
            "internet/btcl.svg": "BTCL Internet",
            "internet/dot_internet.svg": "DOT Internet",
            "utility/titas.svg": "Titas Gas",
            "utility/wasa.svg": "Dhaka WASA",
            "utility/dpdc.svg": "DPDC",
            "utility/desco.svg": "DESCO",
        }
        for rel, name in biller_map.items():
            src = icons_dir / rel
            if src.exists():
                biller = Biller.objects.filter(name=name).first()
                if biller:
                    save_icon(biller, "logo", src)

        provider_map = {
            "train/br.svg": "Bangladesh Railway",
            "airline/us_bangla.svg": "US-Bangla Airlines",
            "airline/biman.svg": "Biman Bangladesh",
        }
        for rel, name in provider_map.items():
            src = icons_dir / rel
            if src.exists():
                provider = TicketProvider.objects.filter(name=name).first()
                if provider:
                    save_icon(provider, "logo", src)

        self.stdout.write(f"  + {count} icons imported")

    def _seed_foundations(self):
        foundations = []
        for name, cause_key, reg_no in BD_FOUNDATIONS:
            cause = CharityCause.objects.get(key=cause_key)
            phone = "013" + str(random.randint(10000000, 99999999))
            user = User.objects.create_user(
                phone=phone,
                password=PASSWORD,
                full_name=name,
                nid=self._unique_nid(),
                role="foundation",
                is_verified=True,
            )
            foundation = Foundation.objects.create(
                user=user,
                organization_name=name,
                registration_number=reg_no,
                cause=cause,
                description=f"Verified {cause_key} organization in Bangladesh.",
                is_verified=True,
            )
            user.wallet.balance = Decimal(str(random.randint(50000, 500000)))
            user.wallet.save(update_fields=["balance"])
            foundations.append(foundation)
        self.stdout.write(f"  + {len(foundations)} foundations")
        return foundations

    def _seed_merchant_categories(self):
        keys = {category for _, category in BD_MERCHANTS}
        labels = {
            "retail": "Retail",
            "food": "Food & Beverage",
            "transport": "Transport",
            "utility": "Utility",
            "health": "Health & Pharmacy",
            "education": "Education",
            "entertainment": "Entertainment",
            "other": "Other",
        }
        for key in sorted(keys):
            MerchantCategory.objects.update_or_create(
                key=key,
                defaults={"label": labels.get(key, key.title())},
            )
        self.stdout.write(f"  + {len(keys)} merchant categories")

    def _seed_merchants(self, users):
        merchant_users = random.sample(users, min(len(BD_MERCHANTS), len(users)))
        merchants = []
        for user, (biz_name, category) in zip(merchant_users, BD_MERCHANTS):
            merchant = Merchant.objects.create(
                user=user,
                business_name=biz_name,
                category=MerchantCategory.objects.get(key=category),
                is_verified=random.choices([True, False], weights=[75, 25])[0],
            )
            merchants.append(merchant)
        return merchants

    def _seed_cards(self, users):
        card_count = 0
        networks = ["visa", "mastercard", "amex", "nexus"]
        for user in users:
            for _ in range(random.randint(1, 2)):
                network = random.choice(networks)
                prefixes = {
                    "visa": "423456",
                    "mastercard": "523456",
                    "amex": "371234",
                    "nexus": "623456",
                }
                raw = (
                    prefixes.get(network, "423456")
                    + str(random.randint(1000000000, 9999999999))[:10]
                )
                card = Card(
                    user=user,
                    card_network=network,
                    card_type=random.choice(["debit", "prepaid"]),
                    cardholder_name=user.full_name,
                    expiry_month=random.randint(1, 12),
                    expiry_year=random.randint(2025, 2030),
                    status=random.choices(
                        ["active", "blocked", "expired"], weights=[80, 10, 10]
                    )[0],
                )
                card.set_number(raw)
                card.save()
                card_count += 1
        self.stdout.write(f"  + {card_count} cards")

    def _seed_operator_types(self):
        labels = {"prepaid": "Prepaid", "postpaid": "Postpaid", "both": "Both"}
        for key, label in labels.items():
            OperatorType.objects.update_or_create(
                key=key,
                defaults={"label": label, "is_active": True},
            )
        self.stdout.write(f"  + {len(labels)} operator types")

    def _seed_operators(self):
        operators = []
        for name, code, op_type in BD_OPERATORS:
            op = Operator.objects.create(
                name=name,
                operator_code=code,
                type=OperatorType.objects.get(key=op_type),
            )
            operators.append(op)
        self.stdout.write(f"  + {len(operators)} operators")
        return operators

    def _seed_data_packs(self, operators):
        count = 0
        for op in operators:
            for i, (name, vol, days, amt) in enumerate(
                [
                    ("500 MB", "500 MB", 7, Decimal("48")),
                    ("1 GB", "1 GB", 7, Decimal("89")),
                    ("3 GB", "3 GB", 30, Decimal("199")),
                    ("5 GB", "5 GB", 30, Decimal("299")),
                    ("10 GB", "10 GB", 30, Decimal("399")),
                ]
            ):
                DataPack.objects.create(
                    operator=op,
                    name=name,
                    volume=vol,
                    validity_days=days,
                    amount=amt,
                )
                count += 1
        self.stdout.write(f"  + {count} data packs")

    def _seed_biller_categories(self):
        keys = {category for _, category, _ in BD_BILLERS}
        labels = {
            "electricity": "Electricity",
            "gas": "Gas",
            "water": "Water",
            "internet": "Internet",
            "tv": "Television / DTH",
            "education": "Education",
            "microfinance": "Microfinance",
        }
        for key in sorted(keys):
            BillerCategory.objects.update_or_create(
                key=key,
                defaults={"label": labels.get(key, key.title())},
            )
        self.stdout.write(f"  + {len(keys)} biller categories")

    def _seed_billers(self):
        billers = []
        for name, category, code in BD_BILLERS:
            b = Biller.objects.create(
                name=name,
                category=BillerCategory.objects.get(key=category),
                biller_code=code,
            )
            billers.append(b)
        self.stdout.write(f"  + {len(billers)} billers")
        return billers

    def _seed_banks(self):
        banks = []
        for name, code in BD_BANKS:
            b = Bank.objects.create(name=name, bank_code=code, is_islamic=True)
            banks.append(b)
        self.stdout.write(f"  + {len(banks)} Islamic banks")
        return banks

    def _seed_bank_accounts(self, users, banks):
        count = 0
        for user in random.sample(users, min(8, len(users))):
            bank = random.choice(banks)
            BankAccount.objects.create(
                user=user,
                bank=bank,
                account_number=str(random.randint(100000000000, 999999999999)),
                account_holder=user.full_name,
                branch=random.choice(["Gulshan", "Mirpur", "Dhanmondi", "Motijheel"]),
                routing_number=str(random.randint(100000000, 999999999)),
            )
            count += 1
        self.stdout.write(f"  + {count} bank accounts")

    def _seed_agents(self):
        agents = []
        shops = [
            "Mama's Store",
            "Rahim General Store",
            "City Point",
            "Bismillah Telecom",
            "Modern Shop",
            "Shahjalal Traders",
            "Dhaka Point",
        ]
        for i, shop in enumerate(shops):
            dist = BD_DISTRICTS[i % len(BD_DISTRICTS)]
            thanas = BD_THANAS.get(dist, ["Central"])
            a = Agent.objects.create(
                full_name=random.choice(BD_NAMES),
                phone=self._unique_phone(),
                nid=self._unique_nid(),
                shop_name=shop,
                district=dist,
                thana=random.choice(thanas),
                address=f"{random.randint(1, 200)}, {random.choice(['Road', 'Street'])}, {dist}",
                latitude=Decimal(str(23.75 + random.random() * 2)),
                longitude=Decimal(str(90.35 + random.random() * 2)),
                is_verified=True,
                commission_pct=Decimal(
                    str(random.choice(["0.50", "0.80", "1.00", "1.20"]))
                ),
            )
            agents.append(a)
        self.stdout.write(f"  + {len(agents)} agents")
        return agents

    def _seed_loan_products(self):
        products = []
        for name, min_a, max_a, days, fee in [
            ("Qard Hasan Small", Decimal("500"), Decimal("5000"), 30, Decimal("0.00")),
            (
                "Qard Hasan Medium",
                Decimal("1000"),
                Decimal("10000"),
                60,
                Decimal("50.00"),
            ),
            (
                "Qard Hasan Large",
                Decimal("5000"),
                Decimal("50000"),
                90,
                Decimal("100.00"),
            ),
        ]:
            p = QardHasanProduct.objects.create(
                name=name,
                min_amount=min_a,
                max_amount=max_a,
                tenure_days=days,
                service_fee=fee,
                description=(
                    f"Interest-free benevolent loan (Qard Hasan). "
                    f"Up to ৳{max_a}, repay within {days} days. "
                    f"No riba, no interest. Only principal repayment required."
                ),
            )
            products.append(p)
        self.stdout.write(f"  + {len(products)} Qard Hasan products")
        return products

    def _seed_remittance_partners(self):
        partners = []
        for name, country, curr, rate in REMITTANCE_PARTNERS:
            p = RemittancePartner.objects.create(
                name=name,
                country=country,
                currency=curr,
                exchange_rate=rate,
            )
            partners.append(p)
        self.stdout.write(f"  + {len(partners)} remittance partners")
        return partners

    def _seed_ticket_categories(self):
        keys = {category for _, category in TICKET_PROVIDERS}
        labels = {
            "bus": "Bus",
            "train": "Train",
            "airline": "Airline",
            "cinema": "Cinema",
            "event": "Event",
            "ferry": "Ferry",
        }
        for key in sorted(keys):
            TicketCategory.objects.update_or_create(
                key=key,
                defaults={"label": labels.get(key, key.title())},
            )
        self.stdout.write(f"  + {len(keys)} ticket categories")

    def _seed_ticket_providers(self):
        providers = []
        trip_data = {
            "bus": [
                (
                    "Dhaka to Chittagong Express",
                    "Dhaka",
                    "Chittagong",
                    "08:00 AM",
                    "03:00 PM",
                    "AC",
                    Decimal("800"),
                ),
                (
                    "Dhaka to Sylhet Volvo",
                    "Dhaka",
                    "Sylhet",
                    "10:30 PM",
                    "06:00 AM",
                    "AC",
                    Decimal("1200"),
                ),
                (
                    "Dhaka to Cox's Bazar",
                    "Dhaka",
                    "Cox's Bazar",
                    "09:00 PM",
                    "07:00 AM",
                    "Non-AC",
                    Decimal("900"),
                ),
            ],
            "train": [
                (
                    "Subarna Express (702)",
                    "Dhaka",
                    "Chittagong",
                    "07:00 AM",
                    "01:30 PM",
                    "First Class",
                    Decimal("500"),
                ),
                (
                    "Parabat Express (710)",
                    "Dhaka",
                    "Sylhet",
                    "10:15 PM",
                    "06:45 AM",
                    "AC",
                    Decimal("750"),
                ),
                (
                    "Ekota Express (724)",
                    "Dhaka",
                    "Dinajpur",
                    "08:30 AM",
                    "04:00 PM",
                    "Shovon",
                    Decimal("400"),
                ),
            ],
            "airline": [
                (
                    "BS-101 Dhaka to Chittagong",
                    "Dhaka",
                    "Chittagong",
                    "09:00 AM",
                    "09:50 AM",
                    "Economy",
                    Decimal("3500"),
                ),
                (
                    "BG-202 Dhaka to Sylhet",
                    "Dhaka",
                    "Sylhet",
                    "02:00 PM",
                    "02:45 PM",
                    "Economy",
                    Decimal("3000"),
                ),
            ],
            "cinema": [
                (
                    "The Blockbuster",
                    "",
                    "",
                    "03:00 PM",
                    "06:00 PM",
                    "Regular",
                    Decimal("300"),
                ),
                (
                    "Avenger Returns",
                    "",
                    "",
                    "06:30 PM",
                    "09:30 PM",
                    "Premium",
                    Decimal("500"),
                ),
            ],
            "ferry": [
                (
                    "MV Karnafuli",
                    "Dhaka",
                    "Barisal",
                    "06:00 PM",
                    "06:00 AM",
                    "Cabin",
                    Decimal("600"),
                ),
                (
                    "MV Sundarban",
                    "Dhaka",
                    "Khulna",
                    "07:00 PM",
                    "07:00 AM",
                    "Deck",
                    Decimal("350"),
                ),
            ],
            "event": [
                (
                    "Bangladesh Music Fest 2026",
                    "",
                    "",
                    "05:00 PM",
                    "10:00 PM",
                    "VIP",
                    Decimal("2000"),
                ),
            ],
        }

        for name, cat in TICKET_PROVIDERS:
            p = TicketProvider.objects.create(
                name=name,
                category=TicketCategory.objects.get(key=cat),
            )
            for trip in trip_data.get(cat, []):
                TicketTrip.objects.create(
                    provider=p,
                    name=trip[0],
                    origin=trip[1],
                    destination=trip[2],
                    departure_time=trip[3],
                    arrival_time=trip[4],
                    coach_class=trip[5],
                    price=trip[6],
                    coaches=TRAIN_COACHES if cat == "train" else [],
                )
            providers.append(p)
        self.stdout.write(f"  + {len(providers)} ticket providers with trips")
        return providers

    def _seed_mudarabah_plans(self):
        plans_data = [
            ("6-Month Mudarabah", 6, Decimal("1000"), Decimal("30.00")),
            ("1-Year Mudarabah", 12, Decimal("1000"), Decimal("40.00")),
            ("2-Year Mudarabah", 24, Decimal("2000"), Decimal("50.00")),
            ("3-Year Mudarabah", 36, Decimal("1500"), Decimal("55.00")),
            ("5-Year Mudarabah", 60, Decimal("1000"), Decimal("60.00")),
        ]
        plans = []
        for name, months, monthly, profit in plans_data:
            plan = MudarabahPlan.objects.create(
                name=name,
                duration_months=months,
                monthly_amount=monthly,
                profit_ratio=profit,
                is_active=True,
            )
            plans.append(plan)
        self.stdout.write(f"  + {len(plans)} plans")
        return plans

    def _seed_mudarabah_accounts(self, users, plans):
        count = 0
        active_users = [u for u in users if u.wallet.status == "active"]
        for user in random.sample(active_users, min(8, len(active_users))):
            plan = random.choice(plans)
            account = MudarabahAccount.objects.create(user=user, plan=plan)
            paid = random.randint(1, min(plan.duration_months, 6))
            for i in range(1, paid + 1):
                MudarabahContribution.objects.create(
                    mudarabah_account=account,
                    installment_number=i,
                    amount=plan.monthly_amount,
                )
            account.total_deposited = plan.monthly_amount * paid
            account.update_expected_payout()
            account.save(update_fields=["total_deposited", "expected_payout"])
            record_transaction(
                sender=user,
                transaction_type="savings",
                amount=account.total_deposited,
                note=f"{plan.name} - {paid} installment(s)",
                counterparty=plan.name,
            )
            count += 1
        self.stdout.write(f"  + {count} Mudarabah accounts")

    def _seed_transactions(self, users, merchants):
        active_users = [u for u in users if u.wallet.status == "active"]
        verified_merchants = [m for m in merchants if m.is_verified]
        fee_rate = Decimal(str(settings.TRANSFER_FEE_PERCENT)) / Decimal("100")

        for _ in range(35):
            if len(active_users) < 2:
                break
            sender, receiver = random.sample(active_users, 2)
            amount = Decimal(str(random.randint(100, 5000)))
            fee = (amount * fee_rate).quantize(Decimal("0.01"))
            self._ensure_balance(sender.wallet, amount + fee)
            sender.wallet.balance -= amount + fee
            receiver.wallet.balance += amount
            sender.wallet.save(update_fields=["balance"])
            receiver.wallet.save(update_fields=["balance"])
            Transaction.objects.create(
                sender=sender,
                receiver=receiver,
                amount=amount,
                fee=fee,
                transaction_type="send",
                status="completed",
                note=random.choice(
                    [
                        "House rent",
                        "Grocery bill",
                        "Tuition fee",
                        "Medicine cost",
                        "Salary transfer",
                    ]
                ),
                created_at=self._past(),
            )

        for _ in range(30):
            if not verified_merchants or not active_users:
                break
            merchant = random.choice(verified_merchants)
            candidates = [u for u in active_users if u != merchant.user]
            if not candidates:
                continue
            sender = random.choice(candidates)
            amount = Decimal(str(random.randint(50, 3000)))
            fee = (amount * fee_rate).quantize(Decimal("0.01"))
            self._ensure_balance(sender.wallet, amount + fee)
            sender.wallet.balance -= amount + fee
            merchant.user.wallet.balance += amount
            sender.wallet.save(update_fields=["balance"])
            merchant.user.wallet.save(update_fields=["balance"])
            Transaction.objects.create(
                sender=sender,
                receiver=merchant.user,
                merchant=merchant,
                amount=amount,
                fee=fee,
                transaction_type="payment",
                status="completed",
                note=f"Payment at {merchant.business_name}",
                created_at=self._past(),
            )

        for _ in range(20):
            user = random.choice(users)
            amount = Decimal(str(random.randint(500, 10000)))
            user.wallet.balance += amount
            user.wallet.save(update_fields=["balance"])
            Transaction.objects.create(
                sender=None,
                receiver=user,
                amount=amount,
                fee=Decimal("0.00"),
                transaction_type="cash_in",
                status="completed",
                note=random.choice(["Agent cash in", "Bank deposit", "Salary top-up"]),
                created_at=self._past(),
            )

        for _ in range(15):
            sender = random.choice(active_users)
            amount = Decimal(str(random.randint(200, 5000)))
            fee = (amount * fee_rate).quantize(Decimal("0.01"))
            self._ensure_balance(sender.wallet, amount + fee)
            sender.wallet.balance -= amount + fee
            sender.wallet.save(update_fields=["balance"])
            Transaction.objects.create(
                sender=sender,
                receiver=None,
                amount=amount,
                fee=fee,
                transaction_type="cash_out",
                status="completed",
                note=random.choice(
                    ["ATM withdrawal", "Agent cash out", "Emergency cash"]
                ),
                created_at=self._past(),
            )

    def _seed_agent_transactions(self, users, agents):
        count = 0
        for _ in range(15):
            user = random.choice(users)
            if user.wallet.status != "active":
                continue
            agent = random.choice(agents)
            amount = Decimal(str(random.randint(500, 5000)))
            txn_type = random.choice(["cash_in", "cash_out"])
            if txn_type == "cash_out":
                self._ensure_balance(user.wallet, amount)
                fee = (amount * Decimal("1.8") / Decimal("100")).quantize(
                    Decimal("0.01")
                )
                user.wallet.balance -= amount + fee
            else:
                user.wallet.balance += amount
                fee = Decimal("0.00")
            user.wallet.save(update_fields=["balance"])
            commission = (amount * agent.commission_pct / Decimal("100")).quantize(
                Decimal("0.01")
            )
            AgentTransaction.objects.create(
                user=user,
                agent=agent,
                amount=amount,
                fee=fee,
                commission=commission,
                transaction_type=txn_type,
                reference="AGT" + str(random.randint(10000000, 99999999)),
                status="completed",
                created_at=self._past(),
            )
            record_transaction(
                sender=user if txn_type == "cash_out" else None,
                receiver=user if txn_type == "cash_in" else None,
                transaction_type=txn_type,
                amount=amount,
                fee=fee,
                note=f"Agent cash {'out' if txn_type == 'cash_out' else 'in'} at "
                f"{agent.shop_name or agent.full_name}",
                counterparty=agent.shop_name or agent.full_name,
            )
            count += 1
        self.stdout.write(f"  + {count} agent transactions")

    def _seed_recharges(self, users, operators):
        count = 0
        for _ in range(30):
            user = random.choice(users)
            if user.wallet.status != "active":
                continue
            op = random.choice(operators)
            amount = Decimal(str(random.choice([20, 50, 100, 200, 500, 1000])))
            self._ensure_balance(user.wallet, amount)
            user.wallet.balance -= amount
            user.wallet.save(update_fields=["balance"])
            RechargeTransaction.objects.create(
                user=user,
                operator=op,
                phone_number="01" + str(random.randint(700000000, 999999999)),
                amount=amount,
                fee=Decimal("0.00"),
                recharge_type="prepaid",
                reference="RCH" + str(random.randint(10000000, 99999999)),
                status="completed",
                created_at=self._past(),
            )
            record_transaction(
                sender=user,
                transaction_type="recharge",
                amount=amount,
                note=f"{op.name} prepaid recharge",
                counterparty=op.name,
            )
            count += 1
        self.stdout.write(f"  + {count} recharges")

    def _seed_bill_payments(self, users, billers):
        count = 0
        for _ in range(20):
            user = random.choice(users)
            if user.wallet.status != "active":
                continue
            biller = random.choice(billers)
            amount = Decimal(str(random.randint(100, 5000)))
            self._ensure_balance(user.wallet, amount)
            user.wallet.balance -= amount
            user.wallet.save(update_fields=["balance"])
            BillPayment.objects.create(
                user=user,
                biller=biller,
                account_number=str(random.randint(100000000, 999999999)),
                amount=amount,
                fee=Decimal("0.00"),
                bill_month=f"{random.randint(1, 12):02d}/2026",
                reference="BILL" + str(random.randint(10000000, 99999999)),
                status="completed",
                created_at=self._past(),
            )
            record_transaction(
                sender=user,
                transaction_type="bill",
                amount=amount,
                note=f"{biller.name} bill",
                counterparty=biller.name,
            )
            count += 1
        self.stdout.write(f"  + {count} bill payments")

    def _seed_bank_transactions(self, users, banks):
        count = 0
        user_bank_map = {}
        for ba in BankAccount.objects.all():
            user_bank_map[ba.user_id] = ba

        for _ in range(15):
            candidates = [
                u
                for u in users
                if u.id in user_bank_map and u.wallet.status == "active"
            ]
            if not candidates:
                break
            user = random.choice(candidates)
            ba = user_bank_map[user.id]
            amount = Decimal(str(random.randint(1000, 20000)))
            txn_type = random.choice(["add_money", "withdraw"])
            if txn_type == "withdraw":
                self._ensure_balance(user.wallet, amount)
                fee = (amount * Decimal("0.5") / Decimal("100")).quantize(
                    Decimal("0.01")
                )
                user.wallet.balance -= amount + fee
            else:
                user.wallet.balance += amount
                fee = Decimal("0.00")
            user.wallet.save(update_fields=["balance"])
            BankTransaction.objects.create(
                user=user,
                bank_account=ba,
                amount=amount,
                fee=fee,
                transaction_type=txn_type,
                status="completed",
                created_at=self._past(),
            )
            record_transaction(
                sender=user if txn_type == "withdraw" else None,
                receiver=user if txn_type == "add_money" else None,
                transaction_type="bank",
                amount=amount,
                fee=fee,
                note=("Withdrew to " if txn_type == "withdraw" else "Added money from ")
                + ba.bank.name,
                counterparty=ba.bank.name,
            )
            count += 1
        self.stdout.write(f"  + {count} bank transactions")

    def _seed_loan_applications(self, users, products):
        count = 0
        for _ in range(8):
            user = random.choice(users)
            if user.wallet.status != "active":
                continue
            product = random.choice(products)
            amount = Decimal(
                str(random.randint(int(product.min_amount), int(product.max_amount)))
            )
            due = amount + product.service_fee
            if product.service_fee > 0:
                self._ensure_balance(user.wallet, product.service_fee + amount)
            user.wallet.balance += amount
            user.wallet.save(update_fields=["balance"])
            QardHasanApplication.objects.create(
                user=user,
                product=product,
                amount=amount,
                service_fee=product.service_fee,
                amount_due=due,
                amount_paid=Decimal("0.00"),
                tenure_days=product.tenure_days,
                status=random.choice(["disbursed", "repaid"]),
                due_date=date.today() + timedelta(days=random.randint(1, 60)),
                disbursed_at=self._past(),
                created_at=self._past(60),
            )
            if product.service_fee > 0:
                record_transaction(
                    sender=user,
                    transaction_type="loan",
                    amount=product.service_fee,
                    note=f"{product.name} service fee",
                    counterparty=product.name,
                )
            record_transaction(
                receiver=user,
                transaction_type="loan",
                amount=amount,
                note=f"{product.name} disbursed",
                counterparty=product.name,
            )
            count += 1
        self.stdout.write(f"  + {count} Qard Hasan applications")

    def _seed_remittances(self, users, partners):
        count = 0
        for _ in range(10):
            user = random.choice(users)
            if user.wallet.status != "active":
                continue
            partner = random.choice(partners)
            foreign = Decimal(str(random.randint(100, 2000)))
            bdt = (foreign * partner.exchange_rate).quantize(Decimal("0.01"))
            user.wallet.balance += bdt
            user.wallet.save(update_fields=["balance"])
            RemittanceTransaction.objects.create(
                user=user,
                partner=partner,
                sender_name=random.choice(BD_NAMES),
                sender_country=partner.country,
                amount_foreign=foreign,
                amount_bdt=bdt,
                exchange_rate=partner.exchange_rate,
                status="completed",
                created_at=self._past(30),
            )
            record_transaction(
                receiver=user,
                transaction_type="remittance",
                amount=bdt,
                note=f"Remittance via {partner.name}",
                counterparty=partner.name,
            )
            count += 1
        self.stdout.write(f"  + {count} remittance transactions")

    def _seed_ticket_bookings(self, users, providers):
        count = 0
        trips = list(
            TicketTrip.objects.filter(is_active=True).select_related("provider")
        )
        for _ in range(12):
            user = random.choice(users)
            if user.wallet.status != "active":
                continue
            trip = random.choice(trips)
            provider = trip.provider
            amount = trip.price
            self._ensure_balance(user.wallet, amount)
            user.wallet.balance -= amount
            user.wallet.save(update_fields=["balance"])
            TicketBooking.objects.create(
                user=user,
                provider=provider,
                journey_date=date.today() + timedelta(days=random.randint(1, 30)),
                departure_time=trip.departure_time,
                origin=trip.origin,
                destination=trip.destination,
                trip_name=trip.name,
                coach_class=trip.coach_class,
                coach=str(random.randint(1, 10))
                if provider.category in ("bus", "train")
                else "",
                seat_number=f"{random.choice('ABCD')}{random.randint(1, 20)}",
                passengers=random.randint(1, 3),
                amount=amount * random.randint(1, 2),
                status="confirmed",
                created_at=self._past(14),
            )
            record_transaction(
                sender=user,
                transaction_type="ticket",
                amount=amount,
                note=f"{provider.name} ticket {trip.origin} to {trip.destination}",
                counterparty=provider.name,
            )
            count += 1
        self.stdout.write(f"  + {count} ticket bookings")

    def _seed_zakat(self, users, foundations):
        count = 0
        for user in random.sample(users, min(5, len(users))):
            wealth = Decimal(str(random.randint(100000, 2000000)))
            zakat = (wealth * Decimal("2.5")) / Decimal("100")
            foundation = random.choice(foundations)
            zakat_amount = zakat.quantize(Decimal("0.01"))
            ZakatPayment.objects.create(
                user=user,
                recipient=foundation.user,
                amount=zakat_amount,
                asset_type=random.choice(["cash", "gold", "business"]),
                hawl_year=2026,
            )
            foundation.user.wallet.balance += zakat_amount
            foundation.user.wallet.save(update_fields=["balance"])
            record_transaction(
                sender=user,
                receiver=foundation.user,
                transaction_type="charity",
                amount=zakat_amount,
                note=f"Zakat to {foundation.organization_name}",
                counterparty=foundation.organization_name,
            )
            count += 1
        self.stdout.write(f"  + {count} zakat payments")

    def _seed_sadaqah(self, users, foundations):
        causes = list(CharityCause.objects.all())
        donations = [
            Sadaqah(
                user=random.choice(users),
                recipient=random.choice(foundations).user,
                amount=Decimal(str(random.randint(50, 5000))),
                cause=random.choice(causes),
            )
            for _ in range(20)
        ]
        Sadaqah.objects.bulk_create(donations)
        for d in donations:
            if d.recipient:
                d.recipient.wallet.balance += d.amount
                d.recipient.wallet.save(update_fields=["balance"])
                record_transaction(
                    sender=d.user,
                    receiver=d.recipient,
                    transaction_type="charity",
                    amount=d.amount,
                    note="Sadaqah",
                    counterparty=d.recipient.full_name,
                )
        self.stdout.write(f"  + {len(donations)} sadaqah donations")

    def _seed_notifications(self, users):
        templates = [
            "You sent {amount} BDT successfully.",
            "You received {amount} BDT.",
            "Cash in of {amount} BDT completed.",
            "Cash out of {amount} BDT completed.",
            "Your transaction of {amount} BDT failed.",
            "QR payment of {amount} BDT was successful.",
            "Your account has been verified.",
            "A new login was detected on your account.",
            "Your daily limit has been reset.",
            "Welcome to Yaqeen!",
            "Your recharge of {amount} BDT was successful.",
            "Bill payment of {amount} BDT completed.",
        ]
        notifications = [
            Notification(
                user=random.choice(users),
                message=random.choice(templates).format(
                    amount=random.randint(50, 10000)
                ),
                is_read=random.choices([True, False], weights=[40, 60])[0],
            )
            for _ in range(50)
        ]
        Notification.objects.bulk_create(notifications)
        self.stdout.write(f"  + {len(notifications)} notifications")

    def _seed_hawl_tracking(self, users):
        count = 0
        for user in random.sample(users, min(8, len(users))):
            HawlTracking.objects.update_or_create(
                user=user,
                defaults={
                    "is_eligible": True,
                    "nisab_crossed_at": timezone.now()
                    - timedelta(days=random.randint(30, 300)),
                    "next_hawl_date": date.today()
                    + timedelta(days=random.randint(30, 120)),
                },
            )
            count += 1
        self.stdout.write(f"  + {count} Hawl tracking records")

    def _seed_sadaqah_jariyah(self, users, foundations):
        causes = list(CharityCause.objects.all())
        count = 0
        for user in random.sample(users, min(5, len(users))):
            foundation = random.choice(foundations)
            amount = Decimal(str(random.randint(100, 2000)))
            SadaqahJariyah.objects.create(
                user=user,
                recipient=foundation.user,
                amount=amount,
                cause=random.choice(causes),
                frequency="monthly",
                is_active=True,
                total_donated=amount,
            )
            foundation.user.wallet.balance += amount
            foundation.user.wallet.save(update_fields=["balance"])
            record_transaction(
                sender=user,
                receiver=foundation.user,
                transaction_type="charity",
                amount=amount,
                note=f"Sadaqah Jariyah to {foundation.organization_name}",
                counterparty=foundation.organization_name,
            )
            count += 1
        self.stdout.write(f"  + {count} Sadaqah Jariyah subscriptions")

    def _ensure_balance(self, wallet, required):
        if wallet.balance < required:
            wallet.balance = required + Decimal("100")
            wallet.save(update_fields=["balance"])

    def _ensure_minimum_balances(self, users):
        minimum = Decimal("5000")
        count = 0
        for user in users:
            if user.wallet.status == "active" and user.wallet.balance < minimum:
                user.wallet.balance = Decimal(str(random.randint(5000, 20000)))
                user.wallet.save(update_fields=["balance"])
                count += 1
        self.stdout.write(f"  + {count} users topped up")

    def _past(self, days=90):
        offset = random.randint(1, days)
        return timezone.now() - timedelta(
            days=offset, hours=random.randint(0, 23), minutes=random.randint(0, 59)
        )

    def _unique_phone(self):
        prefixes = ["01711", "01811", "01911", "01611", "01511", "01311", "01412"]
        while True:
            phone = random.choice(prefixes) + str(random.randint(100000, 999999))
            if not User.objects.filter(phone=phone).exists():
                return phone

    def _unique_nid(self):
        while True:
            nid = str(random.randint(1000000000, 9999999999))
            if not User.objects.filter(nid=nid).exists():
                return nid

    def _print_summary(self, users, merchants, foundations):
        self.stdout.write(self.style.MIGRATE_HEADING("\n-- Seed Summary --"))
        self.stdout.write(f"  Users            : {len(users)}")
        self.stdout.write(f"  Nominees         : {Nominee.objects.count()}")
        self.stdout.write(f"  Merchants        : {len(merchants)}")
        self.stdout.write(f"  Foundations      : {Foundation.objects.count()}")
        self.stdout.write(f"  Cards            : {Card.objects.count()}")
        self.stdout.write(f"  Transactions     : {Transaction.objects.count()}")
        self.stdout.write(f"  Operators        : {Operator.objects.count()}")
        self.stdout.write(f"  Recharges        : {RechargeTransaction.objects.count()}")
        self.stdout.write(f"  Billers          : {Biller.objects.count()}")
        self.stdout.write(f"  Bill Payments    : {BillPayment.objects.count()}")
        self.stdout.write(f"  Banks            : {Bank.objects.count()}")
        self.stdout.write(f"  Bank Accounts    : {BankAccount.objects.count()}")
        self.stdout.write(f"  Bank Txs         : {BankTransaction.objects.count()}")
        self.stdout.write(f"  Agents           : {Agent.objects.count()}")
        self.stdout.write(f"  Agent Txs        : {AgentTransaction.objects.count()}")
        self.stdout.write(f"  Qard Hasan Prods : {QardHasanProduct.objects.count()}")
        self.stdout.write(
            f"  Qard Hasan Loans : {QardHasanApplication.objects.count()}"
        )
        self.stdout.write(f"  Remit Partners   : {RemittancePartner.objects.count()}")
        self.stdout.write(
            f"  Remittances      : {RemittanceTransaction.objects.count()}"
        )
        self.stdout.write(f"  Ticket Providers : {TicketProvider.objects.count()}")
        self.stdout.write(f"  Bookings         : {TicketBooking.objects.count()}")
        self.stdout.write(f"  Mudarabah Accts  : {MudarabahAccount.objects.count()}")
        self.stdout.write(f"  Zakat Paid       : {ZakatPayment.objects.count()}")
        self.stdout.write(f"  Sadaqah Given    : {Sadaqah.objects.count()}")
        self.stdout.write(f"  Sadaqah Jariyah  : {SadaqahJariyah.objects.count()}")
        self.stdout.write(f"  Hawl Tracking    : {HawlTracking.objects.count()}")
        self.stdout.write(f"  Notifications    : {Notification.objects.count()}")
        self.stdout.write(f"\n  Password: {PASSWORD}")
        self.stdout.write(self.style.SUCCESS("  All users ready to log in.\n"))
