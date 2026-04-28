import random
import time
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import Payout


def process_payouts():
    payouts = Payout.objects.filter(status="pending")

    for payout in payouts:
        with transaction.atomic():

            payout = Payout.objects.select_for_update().get(id=payout.id)

            payout.transition_to("processing")

            time.sleep(1)

            rand = random.random()

            if rand < 0.7:
                payout.transition_to("completed")

            elif rand < 0.9:
                payout.transition_to("failed")

            else:
                # simulate stuck
                continue


def retry_stuck_payouts():
    threshold_time = timezone.now() - timedelta(seconds=30)

    stuck_payouts = Payout.objects.filter(
        status="processing",
        created_at__lt=threshold_time,
        attempts__lt=3
    )

    for payout in stuck_payouts:
        with transaction.atomic():
            payout = Payout.objects.select_for_update().get(id=payout.id)

            payout.attempts += 1
            payout.status = "pending"
            payout.save()