# -*- coding:utf-8 -*-
__author__ = 'ery'

from datetime import datetime, timedelta


def get_fastest_push_timing(hour_from=9, hour_to=20):
    now = datetime.now()
    now_total_second = (now.hour * 3600) + (now.minute * 60) + now.second
    if (now.hour >= hour_from) and (now.hour <= hour_to):
        return now + timedelta(seconds=30)
    else:
        if now_total_second > (hour_to * 3600):
            return now + timedelta(seconds=(86400 - now_total_second) + (hour_from * 3600) + 60)
        elif now_total_second < (hour_from * 3600):
            return now + timedelta(seconds=(hour_from * 3600) - now_total_second + 60)
