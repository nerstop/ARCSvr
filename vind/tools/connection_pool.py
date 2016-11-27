# -*- coding:utf-8 -*-
__author__ = 'ery'

import os
import logging

from time import time as stime
from os import getpid

import gevent
from gevent.lock import BoundedSemaphore, RLock
from gevent.queue import Queue as GQueue, PriorityQueue as GPQueue

from contextlib import contextmanager


# 잠재적 문제점 정리
# 1. uwsgi 는 일단 하나의 객체를 생성한다음 그것을 fork(복제) 하는 전략을 취한다.
#    그러므로, 각 커넥션 객체의 identity 가 겹칠 수 있다.
# -> 어차피 uwsgi 가 켜지는 극 초기의 경우에는 커넥션이 1개여도 무방하다. (잘 작동한다는 전제하에)
#    그렇다면, 극 초기(분기 전)와 분기 후를 판단하여 동작을 바꿀 수 있다면 되지 않겠는가?
#    그것을 위한 방법은 여럿 있겠지만, 가장 간단한건 역시 시간 딜레이를 두는 것이다.
#    하지만, 그것은 역시 불안정하다. 분기 전에 들어가는 시간이 얼마나 걸릴지 알고 딜레이를 정하는가.
#    가장 합당한것은 객체 자체가 만들어 질때의 pid 를 구해 놓고, 그 이후 루프를 돌면서 계속 pid 를 얻어서 그 값을 대조하는 것이다.
#    처음 객체가 만들어 질떄 저장된 pid 와 현재 얻어진 pid 가 다르다면 분기가 되었다는 확실한 증거이니
#    그렇게 분기가 되었다는 것을 확신할 수 있다면, 이전에 만들어 놓았던 커넥션(1개)를 제거하고, 실제 계획되었던
#    풀의 크기만큼 커넥션 수를 확장하는 것이 이상적이다.
#    하지만, 검사를 해봐야 알겠지만, 만약 4개를 fork 한다고 하면 그중 1개는 pid 가 변하지 않을 가능성이 있다.
#    즉 4개의 인스턴스라면 1개가 master 이고 3번의 fork 를 통한 3개의 clone 인 케이스이다.
#    이건 실험을 통해 알아봐야 한다.

class IConnectionPool(object):
    SPAWN_FREQUENCY = 0.033

    def __init__(self, logger_name, size=8, keepalive=30, \
                 exc_classes=tuple(), logger_level=logging.INFO, ensure_unique=True):
        self.logger = logging.getLogger("vind." + logger_name)
        self._ld = self.logger.debug
        self._li = self.logger.info
        self._lw = self.logger.warning
        self._le = self.logger.error
        self._lc = self.logger.critical

        if logger_level:
            self.logger.setLevel(logger_level)
        else:
            self.logger.setLevel(logging.WARNING)

        self.ensure_unique = ensure_unique
        self.initial_pid = 0
        if self.ensure_unique:
            self.initial_pid = getpid()
            self._ld("IConnectionPool.__init__, initial_pid=%s" % (str(self.initial_pid),))

        self._size = size
        self._keepalive_period = keepalive
        self._exc_classes = tuple(exc_classes)
        self._internal_work_flag = False

        with self._internal_work_scope():
            if self.ensure_unique:
                self.lock = BoundedSemaphore(value=1)
                self.pool = GPQueue(maxsize=1)
                # for single connection
                self.lock.acquire()
                self._add_connection()
            else:
                self.lock = BoundedSemaphore(value=size)
                self.pool = GPQueue(maxsize=size)
                for i in range(size):
                    self.lock.acquire()
                for i in range(size):
                    self._add_connection()
                # self.pool.put_nowait((0, self._new_connection()))
                # self.lock.release()
                # for i in range(size):
                #     gevent.spawn_later(15 + self.SPAWN_FREQUENCY * i, self._add_connection)
            # gevent.spawn_later(1.5 * size, self._keepalive_periodic)
            gevent.spawn_later(0.25, self._keepalive_periodic)

    def set_logger_lever(self, lv):
        self.logger.setLevel(lv)

    def _dump_state(self):
        return "pid=%s, pool.qsize=%s, lock.counter=%s" % (str(getpid()), str(self.pool.qsize()), str(self.lock.counter))

    def _internal_work_spinlock(self, timeout=0):
        target_time = 0
        if timeout > 0:
            target_time = stime() + timeout

        while True:
            if timeout > 0 and target_time < stime():
                return False

            if not self._internal_work_flag:
                return True

    @contextmanager
    def _internal_work_scope(self):
        self._internal_work_spinlock()
        self._internal_work_flag = True
        yield
        self._internal_work_flag = False

    def _new_connection(self):
        """exception handling required in this function
        return None, or Connection object"""
        raise NotImplementedError

    def _dispose_connection(self, cnx):
        """exception handling required in this function"""
        raise NotImplementedError

    def _keepalive(self, cnx):
        """don't handle exception in this function"""
        raise NotImplementedError

    # def _reset_connection(self, cnx):
    #     """exception handling required in this function"""
    #     raise NotImplementedError

    def _keepalive_periodic(self):
        delay = float(self._keepalive_period) / self._size
        self._ld("_keepalive_periodic spawned, delay=%.2f" % (delay,))

        if self.ensure_unique:
            # 여기서 자신이 최초 만들어 졌을때의 pid 와 현재의 pid 를 한번 비교해 보고
            # 다르다면, 큐를 싹다 비우고 재생성 하는 부분이 필요하다.
            # 보통은 필요없겠지만 MySQLSetting 때문에 그렇다.
            for _ in range(512):
                with self._internal_work_scope():
                    current_pid = getpid()
                    if self.initial_pid != current_pid:
                        # 처음 pid 와 현재의 pid 가 다르다면
                        self._ld("_keepalive_periodic, initial_pid(%s) != current_pid(%s) -> reset pool" % \
                                 (str(self.initial_pid), str(current_pid)))
                        # 락을 그냥 새로 생성함
                        self.lock = BoundedSemaphore(value=self._size)

                        # 안에 들은 커넥션을 모조리 뽑고 끊음
                        qsize = self.pool.qsize()
                        for _ in range(qsize):
                            self._dispose_connection(self.pool.get_nowait())
                        # 풀을 재생성
                        self.pool = GPQueue(maxsize=self._size)
                        # for i in range(self.size):
                        #     # 락을 일단 모두 회수
                        #     self.lock.acquire(blocking=True, timeout=None)
                        # if not self.lock.locked():
                        #     # 여기서 locked 가 아니라면 치명적인 로직 에러
                        #     self._lc("_keepalive_periodic, %d lock acquired but semaphore still unlocked on reset pool" % \
                        #              (self._size,))
                        #     raise AssertionError("_keepalive_periodic, self.lock.locked()=False, critical logic error")
                        # for i in range(self._size):
                        #     # pool 에 있는 모든 커넥션을 인출
                        #     # 만약 이 지점에서 에러가 난다면 치명적 로직 에러
                        #     try:
                        #         ts, cnx = self.pool.get_nowait()
                        #     except gevent.queue.Empty:
                        #         # 치명적 로직 에러
                        #         self._lc("_keepalive_periodic, every lock acquired but raised queue.Empty on reset pool")
                        #         raise AssertionError("_keepalive_periodic, queue.Empty, critical logic error")
                        #     # 커넥션을 버린다.
                        #     self._dispose_connection(cnx)
                        for _ in range(self._size):
                            self.lock.acquire()
                        for i in range(self._size):
                            gevent.spawn_later(self.SPAWN_FREQUENCY * i, self._add_connection)
                        self._li("_keepalive_periodic, reset pool start, " + self._dump_state())
                        while True:
                            if self.lock.counter == self._size:
                                self._ld("_keepalive_periodic, exit connection creation waiting loop, " + self._dump_state())
                                break
                            else:
                                self._ld("_keepalive_periodic, waiting for connection creation, " + self._dump_state())
                                gevent.sleep(0.025)
                        self._li("_keepalive_periodic, reset pool done, " + self._dump_state())
                        break
                    else:
                        self._ld("IConnectionPool.__init__, initial_pid=%s, current_pid=%s -> waiting" % \
                                 (str(self.initial_pid), str(current_pid)))
                        gevent.sleep(0.05)
                        continue

        while True:
            cnx = None
            if self.lock.acquire(blocking=True, timeout=3):
                try:
                    # 여기서 Queue.Empty 따위 에러가 나면 로직상 에러다.
                    with self._internal_work_scope():
                        ts, cnx = self.pool.get_nowait()
                    self._keepalive(cnx)
                    self._ld("keepalive success cnx=%s" % (str(cnx),))
                except self._exc_classes as err:
                    # 이쪽은 보통 커넥터/네트워크 계열 에러
                    # 이 에러가 난다면 커넥션을 폐기한다음, 새로 만들어야 한다.
                    # 왜냐면 보통 _keepalive 에서 재연결을 위한 조치를 취했을 것이기 때문이다.
                    self._dispose_connection(cnx)
                    gevent.spawn_later(0.1, self._add_connection)
                    self._le("_keepalive_periodic, connection err=%s" % (str(err),))
                except gevent.queue.Empty:
                    # 비어있다? 이것은 로직 에러다. 갯수가 안맞는 것으로 치명적인 에러를 뜻한다.
                    # 고로 이것은 에러만을 출력하고 무언가 조치를 취하진 않는다.
                    self._lc("_keepalive_periodic, lock acquired but raise queue.Empty")
                    raise AssertionError("_keepalive_periodic, queue.Empty, critical logic error")
                except Exception as err:
                    # 이 외에 나는 에러도 ... 로직 에러와 동급이므로 치명적 에러다.
                    self._lc("_keepalive_periodic, general err=%s" % (str(err),))
                    raise AssertionError("_keepalive_periodic, Exception, critical error")
                else:
                    # 에러가 안 난 경우이다.
                    # 이 경우에는 cnx 가 None 이 아닌지 검사한 후 다시 큐에 넣고, 락을 릴리즈 한다.
                    if cnx:
                        with self._internal_work_scope():
                            self.pool.put_nowait(item=(stime(), cnx))
                        self.lock.release()
                    else:
                        # cnx 가 None 인 경우이다.
                        # 이 경우 커넥션을 새로 하나 추가한다.
                        # 어차피 cnx 가 None 이므로 폐기 액션을 취할 필요는 없다.
                        gevent.spawn_later(0.1, self._add_connection)
                finally:
                    # 일단 무조껀 해줘야 하는경우
                    # 지금 같은 경우는 할일이 없다.
                    pass
                gevent.sleep(delay)
            else:
                # 락을 얻는데 실패했다.
                # 이 경우는 .. 바로 continue 를 먹인다.
                self._ld("_keepalive_periodic, lock acquire timeout")
                continue

    def _add_connection(self):
        from random import normalvariate as norm
        delay = 0.025
        cnx = None
        while True:
            cnx = self._new_connection()
            if cnx:
                break
            else:
                self._ld("self._new_connection() returned %s" % (str(cnx)))
            gevent.sleep(delay)
            if delay < 15:
                delay *= abs(norm(1.125, 0.075))
            else:
                delay = abs(norm(1.5, 0.25))

        try:
            self.pool.put(item=(stime(), cnx), block=False)
        except gevent.queue.Full:
            # 크리티컬한 로직 에러, 어떤 경우에도 일어나면 안된다.
            # 일어나면 디버그 대상임.
            self._lc("Exception[gevent.queue.Full], in _add_connection self.conn.qsize=%d" % (self.pool.qsize(),))
            raise AssertionError("_add_connection, queue.Full, critical logic error")

        self.lock.release()
        self._ld("_add_connection success, cnx=%s" % (str(cnx),))

    @contextmanager
    def get(self):
        cnx = None
        if self._internal_work_spinlock(timeout=5):
            if self.lock.acquire(blocking=True, timeout=10):
                try:
                    ts, cnx = self.pool.get_nowait()
                    # 여기에서 Queue.Empty 같은게 나면 로직에 문제가 있는거다.
                    yield cnx
                except gevent.queue.Empty:
                    self._lc("get, lock acquired but raise queue.Empty")
                    raise AssertionError("get, queue.Empty, critical logic error")
                except Exception as err:
                    # 이것 또한 치명적인 로직 에러이다.
                    # self._reset_connection(cnx)
                    self._lc("get, general err=%s" % (str(err),))
                    raise AssertionError("get, Exception, critical general error")
                else:
                    # 문제가 없을 떄에나 여기로 들어온다.
                    if cnx:
                        # 여기서 에러가 나면 답이 없는데.. 안나야 정상인데
                        self.pool.put_nowait(item=(stime(), cnx))
                        self.lock.release()
                    else:
                        # 사실상 이것도 로직 에러라고 봐야 함.
                        gevent.spawn_later(0.1, self._add_connection)
                finally:
                    # 지금은 여기서 할 일이 없다.
                    pass
            else:
                # 이게 발동한다는건..
                # 1. checkout 된 커넥션이 checkin 되지 않는다.
                # 2. 세마포어 개수만 가져가고 커넥션이 그 숫자에 맞게 생성되지 않았다.
                lock_counter = self.lock.counter
                pool_qsize = self.pool.qsize()

                raise RuntimeError("lock acquire timeout, lock_counter=%s, pool_qsize=%s" %
                                   (str(lock_counter), str(pool_qsize)))
        else:
            yield None
