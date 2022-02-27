# SPDX-License-Identifier: AGPL-3.0-or-later

import threading

from .online import OnlineProcessor
from .offline import OfflineProcessor
from .online_dictionary import OnlineDictionaryProcessor
from .online_currency import OnlineCurrencyProcessor
from .abstract import EngineProcessor
from searx import logger
import searx.engines as engines


__all__ = ['EngineProcessor', 'OfflineProcessor', 'OnlineProcessor',
           'OnlineDictionaryProcessor', 'OnlineCurrencyProcessor', 'PROCESSORS']
logger = logger.getChild('search.processors')
PROCESSORS = {}


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
    return None


def initialize_processor(processor):
    """Initialize one processor
    Call the init function of the engine
    """
    if processor.has_initialize_function:
        t = threading.Thread(target=processor.initialize, daemon=True)
        t.start()


def initialize(engine_list):
    """Initialize all engines and store a processor for each engine in :py:obj:`PROCESSORS`."""
    for engine_data in engine_list:
        engine_name = engine_data['name']
        engine = engines.engines.get(engine_name)
        if engine:
            processor = get_processor(engine, engine_name)
            initialize_processor(processor)
            if processor is None:
                engine.logger.error('Error get processor for engine %s', engine_name)
            else:
                PROCESSORS[engine_name] = processor
