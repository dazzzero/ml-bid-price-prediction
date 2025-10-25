# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 14:41:02 2021

@author: USER
"""
from PyQt5.QtCore import pyqtSignal

class SignalDispatcher:
    """
    Simple signal dispatcher.
    """
    signals = {}
    handlers = {}

    @staticmethod
    def register_signal(alias: str, signal: pyqtSignal):
        """
        Used to register signal at the dispatcher. Note that you can not use alias that already exists.
        :param alias: Alias of the signal. String.
        :param signal: Signal itself. Usually pyqtSignal instance.
        :return:
        """
        if SignalDispatcher.signal_alias_exists(alias):
            raise SignalDispatcherError('Alias "' + alias + '" for signal already exists!')

        SignalDispatcher.signals[alias] = signal

    @staticmethod
    def register_handler(alias: str, handler: callable):
        """
        Used to register handler at the dispatcher.
        :param alias: Signal alias to match handler to.
        :param handler: Handler. Some callable.
        :return:
        """
        if SignalDispatcher.handlers.get(alias) is None:
            SignalDispatcher.handlers[alias] = [handler]
        else:
            SignalDispatcher.handlers.get(alias).append(handler)

    @staticmethod
    def dispatch():
        """
        This methods runs the wheel. It is used to connect signal with their handlers, based on the aliases.
        :return:
        """
        aliases = SignalDispatcher.signals.keys()

        for alias in aliases:
            handlers = SignalDispatcher.handlers.get(alias)
            signal = SignalDispatcher.signals.get(alias)

            if signal is None or handlers.__len__() == 0:
                continue

            for handler in handlers:
                signal.connect(handler)

    @staticmethod
    def signal_aliases():
        """
        Returns all available signal aliases.
        :return:
        """
        return SignalDispatcher.signals.keys()

    @staticmethod
    def handler_aliases():
        """
        Gets all available handler aliases.
        :return:
        """
        return SignalDispatcher.handlers.keys()

    @staticmethod
    def signal_alias_exists(alias: str) -> bool:
        """
        Checks if signal alias exists.
        :param alias: Signal alias.
        :return:
        """
        if SignalDispatcher.signals.get(alias):
            return True

        return False

    @staticmethod
    def handler_alias_exists(alias: str) -> bool:
        """
        Checks if handler alisa exists.
        :param alias: Handler alias.
        :return:
        """
        if SignalDispatcher.handlers.get(alias):
            return True

        return False


class SignalDispatcherError(Exception):
    def __init__(self, message: str):
        super().__init__(message)