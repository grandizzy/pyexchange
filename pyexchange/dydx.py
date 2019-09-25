# This file is part of Maker Keeper Framework.
#
# Copyright (C) 2019 grandizzy
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from pprint import pformat

from dydx.client import Client
from pyexchange.api import PyexAPI
from pymaker import Wad
from typing import List, Optional

import dateutil.parser

import dydx.constants as consts
import dydx.util as utils


class Order:
    def __init__(self,
                 order_id: str,
                 pair: str,
                 is_sell: bool,
                 price: Wad,
                 amount: Wad):

        assert(isinstance(pair, str))
        assert(isinstance(is_sell, bool))
        assert(isinstance(price, Wad))
        assert(isinstance(amount, Wad))

        self.order_id = order_id
        self.pair = pair
        self.is_sell = is_sell
        self.price = price
        self.amount = amount

    @property
    def sell_to_buy_price(self) -> Wad:
        return self.price

    @property
    def buy_to_sell_price(self) -> Wad:
        return self.price

    @property
    def remaining_buy_amount(self) -> Wad:
        return self.amount*self.price if self.is_sell else self.amount

    @property
    def remaining_sell_amount(self) -> Wad:
        return self.amount if self.is_sell else self.amount*self.price

    def __repr__(self):
        return pformat(vars(self))

    @staticmethod
    def to_order(item: list, pair: str):
        return Order(order_id=item['id'],
                     pair=pair,
                     is_sell=True if item['side'] == 'sell' else False,
                     price=Wad.from_number(item['price']),
                     amount=Wad.from_number(item['size']))


class Trade:
    def __init__(self,
                 trade_id: str,
                 timestamp: int,
                 pair: str,
                 price: Wad,
                 amount: Wad,
                 created_at: int):

        assert(isinstance(trade_id, str) or (trade_id is None))
        assert(isinstance(timestamp, int))
        assert(isinstance(pair, str))
        assert(isinstance(price, Wad))
        assert(isinstance(amount, Wad))
        assert(isinstance(created_at, int))

        self.trade_id = trade_id
        self.timestamp = timestamp
        self.pair = pair
        self.price = price
        self.amount = amount
        self.created_at = created_at

    def __eq__(self, other):
        assert(isinstance(other, Trade))
        return self.trade_id == other.trade_id and \
               self.timestamp == other.timestamp and \
               self.pair == other.pair and \
               self.price == other.price and \
               self.amount == other.amount and \
               self.created_at == other.created_at

    def __hash__(self):
        return hash((self.trade_id,
                     self.timestamp,
                     self.pair,
                     self.price,
                     self.amount,
                     self.created_at))

    def __repr__(self):
        return pformat(vars(self))

    @staticmethod
    def from_list(trade):
        print(trade)
        return Trade(trade_id=trade['uuid'],
                     timestamp=int(dateutil.parser.parse(trade['createdAt']).timestamp()),
                     pair=trade['order']['pair']['name'],
                     price=Wad.from_number(trade['price']),
                     amount=Wad(int(trade['fillAmount'])),
                     created_at=int(dateutil.parser.parse(trade['createdAt']).timestamp()))


class DydxApi(PyexAPI):
    """Dydx API interface.
    """

    logger = logging.getLogger()

    def __init__(self, node: str, private_key: str, timeout: float):
        assert(isinstance(node, str))
        assert(isinstance(private_key, str))
        assert(isinstance(timeout, float))

        self.client = Client(private_key=private_key, node=node)

    def get_symbols(self):
        return self.client.get_pairs()

    def get_balances(self):
        return self.client.get_my_balances()

    def get_orders(self, pair: str) -> List[Order]:
        assert(isinstance(pair, str))

        orders = self.client.get_my_orders(pairs=[pair], limit=None, startingBefore=None)

        return list(map(lambda item: Order.to_order(item, pair), orders['items']))

    def place_order(self, pair: str, is_sell: bool, price: Wad, amount: Wad) -> str:
        assert(isinstance(pair, str))
        assert(isinstance(is_sell, bool))
        assert(isinstance(price, Wad))
        assert(isinstance(amount, Wad))

        # side = self.client.SIDE_SELL if is_sell else self.client.SIDE_BUY
        #
        # self.logger.info(f"Placing order ({side}, amount {amount} of {pair},"
        #                  f" price {price})...")
        #
        # result = self.client.create_limit_order(pair, side, str(price), str(amount))
        # order_id = result['orderId']
        #
        # self.logger.info(f"Placed order as #{order_id}")
        # return order_id

    def cancel_order(self, order_id: str):
        assert(isinstance(order_id, str))

        self.logger.info(f"Cancelling order #{order_id}...")

        canceled_order = self.client.cancel_order(hash=order_id)
        return canceled_order['order']['uuid'] == order_id

    def get_trades(self, pair: str, page_number: int = 1) -> List[Trade]:
        assert(isinstance(pair, str))
        assert(isinstance(page_number, int))

        result = self.client.get_my_fills(pairs=[pair])

        return list(map(lambda item: Trade.from_list(item), result['fills']))

    def get_all_trades(self, pair: str, page_number: int = 1) -> List[Trade]:
        assert(isinstance(pair, str))
        assert(page_number == 1)

        result = self.client.get_fills(pairs=[pair], limit=10)['fills']
        trades = filter(lambda item: item['status'] == 'CONFIRMED' and item['order']['status'] == 'FILLED', result)

        return list(map(lambda item: Trade.from_list(item), trades))
