from asgiref.sync import async_to_sync
from django.forms.models import model_to_dict
from celery import shared_task
from channels.layers import get_channel_layer
import requests

from .models import Coin


channel_layer = get_channel_layer()


@shared_task
def get_coins_data():

    url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false'
    data = requests.get(url).json()

    coins = []

    for coin in data:
        # return either an object or creates it. 'created' is a bool
        obj, created = Coin.objects.get_or_create(symbol=coin['symbol'])

        obj.name = coin['name']
        obj.symbol = coin['symbol']

        if obj.price > coin['current_price']:
            state = 'fall'
        elif obj.price < coin['current_price']:
            state = 'raise'
        else:
            state = 'same'

        obj.price = coin['current_price']
        obj.rank = coin['market_cap_rank']
        obj.image = coin['image']

        obj.save()

        new_data = model_to_dict(obj)
        new_data.update({'state': state})

        coins.append(new_data)

    # Sending data to our websocket:
    # We convert our channel_layer async method to sync method using async_to_sync.
    # We pass channel_layer.group_send method as an object in argument.
    # We have to call the returning method with two arguments:
    # The group to pass the data, here it is 'coins'
    # and the message, a dict. Two keys:
    # type, it's the name of the method of the 'coins' consumer class that will handle the message.
    # text, the message. Here, it's the coins list returned from celery.
    async_to_sync(channel_layer.group_send)('coins', {'type': 'send_new_data', 'text': coins})
