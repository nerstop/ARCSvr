# -*- coding:utf-8 -*-

vars = \
    {
        "VAR_NAME_EXAMPLE1": \
            {
                "type": object,
                "default": [1,2,3,4,5]
            },
        "VAR_NAME_EXAMPLE2": \
            {
                "type": str,
                "default": "string value"
            },
        "VAR_NAME_EXAMPLE3": \
            {
                "type": int,
                "default": 2**16
            },
        "VAR_NAME_EXAMPLE4": \
            {
                "type": float,
                "default": 0.001
            },
        "VAR_NAME_CUSTOM1": \
            {
                "type": object,
                "default": {}
            },
        "VAR_CELERY_PUSH_CHUNK_SIZE": \
            {
                "type": int,
                "default": 20
            },
        "OPERATION_MODE": \
            {
                "type": str,
                "default": "development"
            },
        "SQLALCHEMY_CONNECTOR": \
            {
                "type": str,
                "default": "MySQLdb" # or mysql.connector
            },
        "POLICY_INITIAL_POINT_FOR_NEW_USER": \
            {
                "type": int,
                "default": 5000
            },
        "POLICY_INITIAL_BE_REGULAR_USER_DAYS": \
            {
                "type": int,
                "default": 365
            },
        "POLICY_INTRODUCED_POINT_FOR_NEW_USER": \
            {
                "type": int,
                "default": 5000
            },
        "POLICY_INTRODUCER_POINT_FOR_NEW_USER": \
            {
                "type": int,
                "default": 5000
            },
        "POLICY_BASE_COST_OF_30_DAYS": \
            {
                "type": int,
                "default": 20000
            },
        "POLICY_DISCOUNT_RATE_OF_A_YEAR": \
            {
                "type": float,
                "default": 25.
            },
        "POLICY_USER_WITHDRAW_POSTPONE_HOURS": \
            {
                "type": int,
                "default": 720
            },
        "POLICY_WARNING_DEFAULT_ACTIVE_HOURS": \
            {
                "type": int,
                "default": 720
            },
        "POLICY_ACTIVE_WARNING_COUNT_TO_DISABLE": \
            {
                "type": int,
                "default": 3
            },
        "POLICY_CHANGE_POST_TARGET_TO_PUBLIC_AFTER_SEC": \
            {
                "type": int,
                "default": 900
            },
        "POLICY_ORDER_FEE_RATE": \
            {
                "type": int,
                "default": 10
            },
        "POLICY_MASTER_COMMISSION_RATE": \
            {
                "type": int,
                "default": 0
            },
        "POLICY_ORDER_AUTO_CONFIRM_TIMEOUT_SEC": \
            {
                "type": int,
                "default": 300
            },
        "POLICY_PARTNER_REQUEST_CLEAN_TIMEOUT_HOURS": \
            {
                "type": int,
                "default": 720
            },
        "POLICY_ORDER_STATE0_TIMEOUT_MINS": \
            {
                "type": int,
                "default": 180
            },
        "POLICY_ORDER_STATE2_TIMEOUT_MINS": \
            {
                "type": int,
                "default": 2880
            },
        "POLICY_AD_PRICE_PER_DAYS": \
            {
                "type": int,
                "default": 3000
            },
        "POLICY_CHARGE_REQUEST_TIMEOUT_SEC": \
            {
                "type": int,
                "default": 10800
            },

    }
