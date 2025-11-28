# -*- coding: utf-8 -*-

import epint as ep
from epint.infrastructure.date_range_helper import (
    auto_split_date_range,
    with_auto_date_range_split,
)

ep.set_auth("*****", "*****")
ep.set_mode("prod")


if __name__ == "__main__":
    # Total count service ile kullanım
    @with_auto_date_range_split(
        start_param="periodDateStart",
        end_param="periodDateEnd",
        total_count_service=ep.grid.meter_count
    )
    def get_meters(**kwargs):
        return ep.grid.meter_query(**kwargs)
    
    # Test çağrısı
    result = get_meters(
        periodDateStart='2025-11-01T00:00:00+03:00',
        periodDateEnd='2025-11-30T00:00:00+03:00',
        portfolioTypeId=1,
        usageTypeIds=[2, 5, 12],
        reconciliationVersionTypeId=2,
        statusId=2,
        page={"number": 1, "size": 1000, "sort": {"direction": "DESC", "field": "effectiveDateStart"}},
        http_timeout=60
    )
    
    # API response formatı: result['body']['content']['items'] ve result['body']['content']['page']
    content = result.get('body', {}).get('content', {})
    items = content.get('items', [])
    page_info = content.get('page', {})
    
    print(f"Toplam kayıt sayısı: {len(items)}")
    print(f"Page bilgisi: {page_info}")    

