from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Merchant, LedgerEntry, Payout

def create_payout(merchant_id, amount_paise, idempotency_key):
    with transaction.atomic():

        merchant = Merchant.objects.select_for_update().get(id=merchant_id)

        # 🔁 Check idempotency
        existing_payout = Payout.objects.filter(
            merchant=merchant,
            idempotency_key=idempotency_key
        ).first()

        if existing_payout:
            return existing_payout

        balance = merchant.get_balance()

        if balance < amount_paise:
            raise ValidationError("Insufficient balance")

        payout = Payout.objects.create(
            merchant=merchant,
            amount_paise=amount_paise,
            status="pending",
            idempotency_key=idempotency_key
        )

        LedgerEntry.objects.create(
            merchant=merchant,
            amount=amount_paise,
            entry_type="debit",
            reference=f"payout:{payout.id}"
        )

        return payout