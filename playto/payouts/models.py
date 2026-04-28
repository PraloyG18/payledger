from django.db import models
from django.db.models import Sum, Case, When, F, IntegerField
from django.db import transaction

# Create your models here.
class Merchant(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_balance(self):
        result = self.ledger_entries.aggregate(
            balance=Sum(
                Case(
                    When(entry_type="credit", then=F("amount")),
                    When(entry_type="debit", then=F("amount") * -1),
                    output_field=IntegerField()
                )
            )
        )
        return result["balance"] or 0


class LedgerEntry(models.Model):
    CREDIT = "credit"
    DEBIT = "debit"

    ENTRY_TYPE_CHOICES = [
        (CREDIT, "Credit"),
        (DEBIT, "Debit"),
    ]

    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE,
        related_name="ledger_entries"
    )

    amount = models.BigIntegerField()  # paise only

    entry_type = models.CharField(
        max_length=10,
        choices=ENTRY_TYPE_CHOICES
    )

    reference = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


class Payout(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
    ]

    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE,
        related_name="payouts"
    )

    amount_paise = models.BigIntegerField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    idempotency_key = models.CharField(max_length=255)

    attempts = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def transition_to(self, new_status):
        allowed_transitions = {
            "pending": ["processing"],
            "processing": ["completed", "failed"],
            "completed": [],
            "failed": [],
        }

        if new_status not in allowed_transitions[self.status]:
            raise ValueError(f"Invalid transition from {self.status} to {new_status}")

        with transaction.atomic():

            # If moving to failed → return funds
            if self.status == "processing" and new_status == "failed":
                from .models import LedgerEntry  # avoid circular import

                LedgerEntry.objects.create(
                    merchant=self.merchant,
                    amount=self.amount_paise,
                    entry_type="credit",
                    reference=f"payout_refund:{self.id}"
                )

            self.status = new_status
            self.save()

    class Meta:
        unique_together = ("merchant", "idempotency_key")