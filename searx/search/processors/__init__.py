# SPDX-License-Identifier: AGPL-3.0-or-later

from .online import OnlineProcessor
from .offline import OfflineProcessor
from .online_dictionary import OnlineDictionaryProcessor
from .online_currency import OnlineCurrencyProcessor
from .abstract import EngineProcessor
from searx import logger
import searx.engines as engines


__all__ = ['EngineProcessor', 'OfflineProcessor', 'OnlineProcessor',
           'OnlineDictionaryProcessor', 'OnlineCurrencyProcessor', 'processors']
logger = logger.getChild('search.processors')
processors = {}


def get_processor_class(engine_type):
    for c in [OnlineProcessor, OfflineProcessor, OnlineDictionaryProcessor, OnlineCurrencyProcessor]:
        if c.engine_type == engine_type:
            return c
    return None


def get_processor(engine, engine_name):
    engine_type = getattr(engine, 'engine_type', 'online')
    processor_class = get_processor_class(engine_type)
    if processor_class:
        return processor_class(engine, engine_name)
    else:
        return None


def initialize(engine_list):
    engines.initialize_engines(engine_list)
    for engine_name, engine in engines.engines.items():
        processor = get_processor(engine, engine_name)
        if processor is None:
            logger.error('Error get processor for engine %s', engine_name)
        else:
            processors[engine_name] = processor
