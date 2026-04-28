from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Merchant, Payout
from .services import create_payout
from rest_framework import status
from django.core.exceptions import ValidationError


@api_view(["GET"])
def get_dashboard(request, merchant_id):
    merchant = Merchant.objects.get(id=merchant_id)

    payouts = Payout.objects.filter(merchant=merchant).values()

    return Response({
        "balance": merchant.get_balance(),
        "payouts": list(payouts)
    })


@api_view(["POST"])

def create_payout_view(request, merchant_id):
    try:
        amount = int(request.data.get("amount"))

        payout = create_payout(
            merchant_id,
            amount,
            request.headers.get("Idempotency-Key")
        )

        return Response({"id": payout.id})

    except ValidationError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )