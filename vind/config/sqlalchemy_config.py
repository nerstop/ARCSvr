# -*- coding:utf-8 -*-

sqlalchemy_engine_settings = \
    {
        "production":
            {
                "encoding": "utf-8",
                "convert_unicode": True,
                "echo": False,
                "isolation_level": "READ COMMITTED"
            },
        "development":
            {
                "encoding": "utf-8",
                "convert_unicode": True,
                "echo": False,
                "isolation_level": "READ COMMITTED"
            }
    }

sqlalchemy_queuepool_settings = \
    {
        "production":
            {
                "max_overflow": 4,
                "recycle": 60,
                # "max_connections": 2,
                "pool_size": 8,
                "echo": False,
            },
        "development":
            {
                "max_overflow": 4,
                "recycle": 30,
                # "max_connections": 2,
                "pool_size": 8,
                "echo": False,
            }
    }

sqlalchemy_sessionmaker_settings = \
    {
        "Common":
            {
                "autocommit": False,
                "autoflush": False,
                "expire_on_commit": False,
            }
    }
