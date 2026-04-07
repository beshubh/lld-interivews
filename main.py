import requests

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar, Generic, Any


# payment providers
"""
Design layout
There can be different payment providers, so i will have payment provider strategy

`PaymentProvider`

each payment provider will have separete configuration
used to make api call, stripe might have different settings
razorpay diff etc.

`ProviderConfig`

each provider will return a response object in different format

we can have a unified format for storing the PaymentLink object at our end
`PaymentLink`

Each `PaymentProvider` will have a adapter that will take object in provider's format
and produce a unified `PaymentLink`
"""

ConfigT = TypeVar("ConfigT")


@dataclass
class PaymentLink:
    """unique id of the PaymentLink in our service's DB"""

    unique_id: str
    external_link_id: str
    amount: float
    currency: str
    description: str
    checkout_id: str
    provider: str
    raw_payload: dict


@dataclass
class Checkout:
    checkout_id: str
    customer_id: str
    amount: float
    currency: str
    description: str
    provider: str


class PaymentProviderError(Exception):
    pass


class IPaymentProvider(Generic[ConfigT], ABC):
    def __init__(self, config: ConfigT, request_client) -> None:
        self._config = config
        self._request_client = request_client

    @abstractmethod
    def create_payment_link(self, checkout: Checkout) -> PaymentLink:
        pass


@dataclass
class StripeConfig:
    api_key: str
    api_secret: str
    base_url: str


class StripePaymentProvider(IPaymentProvider[StripeConfig]):
    def create_payment_link(self, checkout: Checkout) -> PaymentLink:

        try:
            res = self._request_client.post(
                f"{self._config.base_url}/payment-links",
                headers={
                    "api-key": self._config.api_key,
                    "api-secret": self._config.api_secret,
                },
                json={
                    "customer_id": checkout.customer_id,
                    "amount": checkout.amount,
                    "currency": checkout.currency,
                    "description": checkout.description,
                },
            )
            if not res.ok:
                raise PaymentProviderError(
                    "request to `Stripe` failed with status code: {}, error: {}",
                    res.status_code,
                    res.text,
                )
            data = res.json()
            payment_link = PaymentLink(
                checkout_id=checkout.checkout_id,
                unique_id="123",
                pg_link_id=data.get("id"),
                amount=data.get("amount"),
                description=data.get("description"),
                currency=data.get("currency"),
            )
            return payment_link
        except requests.RequestException as e:
            raise PaymentProviderError from e


PAYMENTS_PROVIDER_REGISTRY: dict[str, IPaymentProvider] = {
    "stripe": StripePaymentProvider
}


def register_provider(name: str, IPaymentProvider) -> None:
    global PAYMENTS_PROVIDER_REGISTRY
    PAYMENTS_PROVIDER_REGISTRY[name] = IPaymentProvider


ModelT = TypeVar("ModelT")


class Repostory(Generic[ModelT]):
    def __init__(self) -> None:
        self._store: dict[str, ModelT] = {}

    def create(self, instance: ModelT) -> None:
        self._store[instance.id] = instance

    def find(self, id: str) -> ModelT | None:
        return self._store.get(id)


checkout_repo = Repostory[Checkout]()
payment_links_repo = Repostory[PaymentLink]()


class ValidationError(Exception):
    pass


# services
def create_payment_link(
    *,
    checkout: Checkout,
    request_client,
    payment_links_repo: Repostory[PaymentLink],
    provider: IPaymentProvider,
) -> PaymentLink:
    if not checkout.checkout_id:
        raise ValidationError(
            "field `checkout_id` should contain a valid value, currently: {}".format(
                checkout.checkout_id
            )
        )

    if checkout.amount <= 0:
        raise ValidationError("field `checkout.amount` should contain a value > 0")

    link = provider.create_payment_link(checkout)
    payment_links_repo.create(link)
    return link


def checkout_links_api(checkout: Checkout):
    provider = PAYMENTS_PROVIDER_REGISTRY.get(checkout.provider)
    if not provider:
        raise ValidationError(f"provider not supported: {provider}")
    link = create_payment_link(
        checkout=checkout,
        request_client=requests,
        payment_links_repo=payment_links_repo,
        provider=provider,
    )
    print(f"Payment Link: {link}")
    return link


def initialize_app():
    register_provider(
        "stripe",
        StripePaymentProvider(
            StripeConfig(
                api_key="123", api_secret="sec_123", base_url="https://stripe.com"
            ),
            request_client=requests,
        ),
    )


def main():
    initialize_app()
    checkout = Checkout(
        checkout_id="123",
        customer_id="cust_123",
        amount=1500,
        currency="USD",
        description="Order #1001",
        provider="stripe",
    )
    _link = checkout_links_api(checkout)


if __name__ == "__main__":
    main()
