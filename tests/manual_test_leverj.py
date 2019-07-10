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

import sys

from web3 import Web3, HTTPProvider
from pymaker.keys import register_private_key

from pyexchange.leverj import LeverjAPI


account = sys.argv[1]
api_key = sys.argv[2]
api_secret = sys.argv[3]
private_key = sys.argv[4]


web3 = Web3(HTTPProvider("http://localhost:8545", request_kwargs={"timeout": 600}))
web3.eth.defaultAccount = account
register_private_key(web3, private_key)

leverjApi = LeverjAPI(web3, "https://test.leverj.io", account, api_key, api_secret, 10)
print(leverjApi.get_account())