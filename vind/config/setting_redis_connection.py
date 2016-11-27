# -*- coding:utf-8 -*-

# DB 0 : Setting
# DB 1 : RLock
# DB 2 : Session
# DB 3 : Static Caching
# DB 4 : DB Caching
# DB 5 : Celery
# DB 6 : Celery Result

# redis.ConnectionPool(max_connections=128, **redis_server_settings["Setting"])

# remote_redis_server_uri = "192.168.137.120"
# remote_redis_server_port = 63709

redis_server_settings = \
    {
        "LocalSetting":
            {
                "db": 0,
                "password": None,
                "unix_socket_path": "/tmp/redis.sock"
            },

        "RemoteSetting":
            {
                # "host": remote_redis_server_uri,
                # "port": remote_redis_server_port,
                "unix_socket_path": "/tmp/redis.sock",
                "db": 0,
                "password": None,
                #"socket_timeout": None,
                #"charset": "utf-8",
                #"errors": "strict",
                #"unix_socket_path": None,
            },

        "RLock":
            {
                #"host": remote_redis_server_uri,
                #"port": remote_redis_server_port,
                "unix_socket_path": "/tmp/redis.sock",
                "db": 1,
                "password": None,
                # "socket_timeout": None,
            },

        "Session":
            {
                # "host": remote_redis_server_uri,
                # "port": remote_redis_server_port,
                "unix_socket_path": "/tmp/redis.sock",
                "db": 2,
                "password": None,
                # "socket_timeout": None,
            },

        "StaticCache":
            {
                # "host": remote_redis_server_uri,
                # "port": remote_redis_server_port,
                "unix_socket_path": "/tmp/redis.sock",
                "db": 3,
                "password": None,
                # "socket_timeout": None,
            },

        "DBCache":
            {
                # "host": remote_redis_server_uri,
                # "port": remote_redis_server_port,
                "unix_socket_path": "/tmp/redis.sock",
                "db": 4,
                "password": None,
                # "socket_timeout": None,
            },

        "Celery":
            {
                # "host": remote_redis_server_uri,
                # "port": remote_redis_server_port,
                "unix_socket_path": "/tmp/redis.sock",
                "db": 5,
                "password": None,
                # "socket_timeout": None,
            },

        "Log2Slack":
            {
                # "host": remote_redis_server_uri,
                # "port": remote_redis_server_port,
                "unix_socket_path": "/tmp/redis.sock",
                "db": 6,
                "password": None,
                # "socket_timeout": None,
            },
    }

