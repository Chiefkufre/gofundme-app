from abc import ABC, abstractmethod
import requests
import aiohttp
import asyncio
from core.conf.settings import settings
from core.utils.general import generate_transaction_reference

# from rave_python import Rave


BASE_URL = settings.BASE_URL


class PaymentGateway(ABC):
    @abstractmethod
    def __init__(self, credentials):
        pass

    @abstractmethod
    def charge(self, amount, currency, description):
        pass


class PaypalGateway(PaymentGateway):
    def __init__(self, client_id, secret):
        # Initialize Paypal client with credentials
        pass

    def charge(self, amount, currency, description):
        # Send payment request to Paypal API
        # Parse response and return success/failure
        pass


class FlutterwaveGateway(PaymentGateway):
    def __init__(self, api_key, secret_key):
        # Initialize Flutterwave API client with credentials
        pass

    async def charge(
        amount, currency, customer_id: str, customer_mac, customer_email, customer_pn
    ):
        """Async function for making payment request to flutterwave payment enpoint
        Args:
         Takes all payment parameters.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.flutterwave.com/v3/payments",
                    headers={
                        "Authorization": "Bearer: your_access_token_here",
                    },
                    data={
                        "tx_ref": generate_transaction_reference(customer_id),
                        "amount": amount,
                        "currency": currency,
                        "redirect_url": "fffff",
                        "meta": {
                            "consumer_id": customer_id,
                            "consumer_mac": customer_mac,
                        },
                        "customer": {
                            "email": customer_email,
                            "phonenumber": customer_pn,
                        },
                        "customizations": {
                            "title": settings.SITE_NAME,
                            "logo": "http://www.piedpiper.com/app/themes/joystick-v27/images/logo.png",
                        },
                    },
                ) as response:
                    data = await response.json()
                return data  # Return response data
        except Exception as e:
            return {"error": str(e)}


class StripeGateway(PaymentGateway):
    def __init__(self, api_key):
        # Initialize Stripe API client with credentials
        pass

    def charge(self, amount, currency, description):
        # Send payment request to Stripe API
        # Parse response and return success/failure
        pass


class BitcoinGateway(PaymentGateway):
    def __init__(self, address):
        # Initialize Bitcoin wallet/payment processor with address
        pass

    def charge(self, amount, currency, description):
        # Create Bitcoin transaction and attempt to send payment
        # Parse response and return success/failure
        pass


def process_payment(gateway, amount, currency, description, campaign_id, user_id=None):
    try:
        gateway.charge(amount, currency, description)
        print("Payment successful!")

        # Build the payload with payment details
        payload = {
            "amount": amount,
            "user_id": user_id,
            "campaign_id": campaign_id,
        }

        # Send POST request to your endpoint
        url = f"{BASE_URL}/campaigns/{campaign_id}/donation"
        response = requests.post(url, json=payload)

        # Handle the response from your endpoint
        if response.status_code == 200:
            print("Donation details sent successfully!")
        else:
            print(f"Error sending donation details: {response.text}")
    except Exception as e:
        print(f"Payment failed: {e}")


# Choose your desired payment gateway and provide credentials
gateway = PaypalGateway("client_id", "secret")
# gateway = FlutterwaveGateway("api_key", "secret_key")
# gateway = StripeGateway("api_key")
# gateway = BitcoinGateway("your_bitcoin_address")

# Initiate payment with chosen gateway
process_payment(gateway, 100, "USD", "Sample purchase")
