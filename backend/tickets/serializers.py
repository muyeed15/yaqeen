from rest_framework import serializers

from .models import TicketBooking, TicketProvider, TicketTrip


class TicketTripSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketTrip
        fields = [
            "id",
            "provider",
            "name",
            "origin",
            "destination",
            "departure_time",
            "arrival_time",
            "coach_class",
            "coaches",
            "price",
            "is_active",
        ]


class TicketProviderSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    category_label = serializers.SerializerMethodField()
    trips = TicketTripSerializer(many=True, read_only=True)

    class Meta:
        model = TicketProvider
        fields = [
            "id",
            "name",
            "category",
            "category_label",
            "logo",
            "is_active",
            "trips",
        ]

    def get_logo(self, obj):
        if not obj.logo:
            return None
        return obj.logo.url

    def get_category(self, obj):
        return obj.category.key if obj.category_id else ""

    def get_category_label(self, obj):
        return obj.category.label if obj.category_id else ""


class TicketBookingSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source="provider.name", read_only=True)
    provider_category = serializers.CharField(
        source="provider.category", read_only=True
    )

    class Meta:
        model = TicketBooking
        fields = [
            "id",
            "booking_reference",
            "provider",
            "provider_name",
            "provider_category",
            "journey_date",
            "departure_time",
            "origin",
            "destination",
            "trip_name",
            "coach_class",
            "coach",
            "seat_number",
            "passengers",
            "amount",
            "fee",
            "status",
            "created_at",
        ]
        read_only_fields = ["booking_reference", "status", "created_at"]


class BookTicketSerializer(serializers.Serializer):
    provider_id = serializers.IntegerField()
    trip_id = serializers.IntegerField(required=False)
    journey_date = serializers.DateField()
    origin = serializers.CharField(max_length=100, required=False, default="")
    destination = serializers.CharField(max_length=100, required=False, default="")
    departure_time = serializers.CharField(max_length=10, required=False, default="")
    trip_name = serializers.CharField(max_length=150, required=False, default="")
    coach_class = serializers.CharField(max_length=50, required=False, default="")
    coach = serializers.CharField(max_length=20, required=False, default="")
    seat_number = serializers.CharField(max_length=50, required=False, default="")
    passengers = serializers.IntegerField(min_value=1, default=1)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
