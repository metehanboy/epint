# -*- coding: utf-8 -*-


import epint as ep
from epint.infrastructure.date_range_helper import (
    auto_split_date_range,
    with_auto_date_range_split,
)


ep.set_auth("*****", "*****")

if __name__ == "__main__":
    @with_auto_date_range_split()
    def get_realtime_geneartion(**kwargs):
        return ep.seffaflik_electricity.realtime_generation(**kwargs)

    @with_auto_date_range_split()
    def get_mcp(**kwargs):
        return ep.seffaflik_electricity.mcp_data(**kwargs)

    # data = get_realtime_geneartion(start='2024-01-01', end='2025-11-27', http_timeout=30)

    # print(data["items"][0])
    # print(data["items"][-1])

    ptf = get_mcp(start='2020-01-01',end='2025-11-27')
    print(ptf.keys())

