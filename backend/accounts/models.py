from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("Phone number is required.")
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(phone, password, **extra_fields)

    def create(self, **kwargs):
        password = kwargs.pop("password", None)
        user = super().create(**kwargs)
        if password:
            user.set_password(password)
            user.save(update_fields=["password"])
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ("individual", "Individual"),
        ("foundation", "Foundation"),
    ]

    phone = models.CharField(max_length=15, unique=True)
    full_name = models.CharField(max_length=100)
    nid = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="individual")
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["full_name", "nid"]

    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]

    def __str__(self):
        return self.phone


class Wallet(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("frozen", "Frozen"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    daily_limit = models.DecimalField(max_digits=12, decimal_places=2, default=10000.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Wallet"
        verbose_name_plural = "Wallets"

    def __str__(self):
        return f"{self.user.phone} - {self.balance}"


class Nominee(models.Model):
    RELATION_CHOICES = [
        ("parent", "Parent"),
        ("spouse", "Spouse"),
        ("child", "Child"),
        ("sibling", "Sibling"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="nominees")
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    nid = models.CharField(max_length=20, blank=True)
    relationship = models.CharField(max_length=10, choices=RELATION_CHOICES)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Nominee"
        verbose_name_plural = "Nominees"
        ordering = ["-is_primary", "created_at"]
        unique_together = [["user", "nid"]]

    def __str__(self):
        return f"{self.full_name} ({self.get_relationship_display()})"


class KYCVerification(models.Model):
    DOC_TYPE_CHOICES = [
        ("nid", "National ID"),
        ("passport", "Passport"),
        ("driving_license", "Driving License"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("verified", "Verified"),
        ("rejected", "Rejected"),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="kyc_verification"
    )
    document_type = models.CharField(
        max_length=20, choices=DOC_TYPE_CHOICES, default="nid"
    )
    document_number = models.CharField(max_length=30)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    face_image = models.URLField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "KYC Verification"
        verbose_name_plural = "KYC Verifications"

    def __str__(self):
        return f"KYC - {self.user.phone} ({self.status})"


class OTPVerification(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="otp_verifications"
    )
    otp = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, default="2fa")
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "OTP Verification"
        verbose_name_plural = "OTP Verifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"OTP for {self.user.phone} ({self.purpose})"


class CharityCause(models.Model):
    key = models.CharField(max_length=20, unique=True)
    label = models.CharField(max_length=50)
    icon = models.CharField(max_length=30, default="Heart")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Charity Cause"
        verbose_name_plural = "Charity Causes"
        ordering = ["label"]

    def __str__(self):
        return self.label


class Foundation(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="foundation_profile"
    )
    organization_name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=50, unique=True)
    cause = models.ForeignKey(
        CharityCause,
        on_delete=models.PROTECT,
        related_name="foundations",
        help_text="Charity cause this foundation supports",
    )
    logo = models.FileField(upload_to="foundations/", blank=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=15, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Foundation"
        verbose_name_plural = "Foundations"
        ordering = ["organization_name"]

    def __str__(self):
        return self.organization_name
