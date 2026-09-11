import uuid

from django.conf import settings
from django.db import models


class TicketCategory(models.Model):
    key = models.CharField(max_length=10, unique=True)
    label = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ticket Category"
        verbose_name_plural = "Ticket Categories"
        ordering = ["label"]

    def __str__(self):
        return self.label


class TicketProvider(models.Model):
    name = models.CharField(max_length=150)
    category = models.ForeignKey(
        TicketCategory,
        on_delete=models.PROTECT,
        related_name="providers",
    )
    logo = models.FileField(upload_to="tickets/", blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ticket Provider"
        verbose_name_plural = "Ticket Providers"
        ordering = ["category", "name"]

    def __str__(self):
        return f"{self.name} ({self.category.label if self.category_id else ''})"


class TicketBooking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ticket_bookings",
    )
    provider = models.ForeignKey(
        TicketProvider, on_delete=models.PROTECT, related_name="bookings"
    )
    booking_reference = models.CharField(max_length=30, unique=True, editable=False)
    journey_date = models.DateField()
    departure_time = models.CharField(
        max_length=10, blank=True, help_text="e.g. 08:30 AM"
    )
    origin = models.CharField(
        max_length=100, blank=True, help_text="Origin city/station"
    )
    destination = models.CharField(
        max_length=100, blank=True, help_text="Destination city/station"
    )
    trip_name = models.CharField(
        max_length=150,
        blank=True,
        help_text="Bus name, train number, flight number, movie name, event name",
    )
    coach_class = models.CharField(
        max_length=50,
        blank=True,
        help_text="AC/Non-AC, Shovon/First Class, Economy/Business, Regular/Premium",
    )
    coach = models.CharField(
        max_length=20, blank=True, help_text="Coach/bogi number or name"
    )
    seat_number = models.CharField(
        max_length=50, blank=True, help_text="e.g. A1, B3-B5"
    )
    passengers = models.PositiveSmallIntegerField(default=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ticket Booking"
        verbose_name_plural = "Ticket Bookings"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = "TKT" + uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking_reference} - {self.provider.name}"


class TicketTrip(models.Model):
    provider = models.ForeignKey(
        TicketProvider, on_delete=models.CASCADE, related_name="trips"
    )
    name = models.CharField(
        max_length=150,
        help_text="Bus name, train number, movie title, flight number, event name",
    )
    origin = models.CharField(max_length=100, blank=True)
    destination = models.CharField(max_length=100, blank=True)
    departure_time = models.CharField(
        max_length=10, blank=True, help_text="e.g. 08:00 AM"
    )
    arrival_time = models.CharField(max_length=10, blank=True)
    coach_class = models.CharField(max_length=50, blank=True)
    coaches = models.JSONField(
        default=list,
        blank=True,
        help_text='Coach designations for trains, e.g. ["ক", "খ", "গ"]',
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ticket Trip"
        verbose_name_plural = "Ticket Trips"
        ordering = ["provider", "name"]

    def __str__(self):
        return f"{self.provider.name} - {self.name} ({self.departure_time})"
