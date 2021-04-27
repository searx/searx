# SPDX-License-Identifier: AGPL-3.0-or-later
# lint: pylint

"""Implement request processores used by engine-types.

"""

__all__ = [
    'EngineProcessor',
    'OfflineProcessor',
    'OnlineProcessor',
    'OnlineDictionaryProcessor',
    'OnlineCurrencyProcessor',
    'processors',
]

from searx import logger
import searx.engines as engines

from .online import OnlineProcessor
from .offline import OfflineProcessor
from .online_dictionary import OnlineDictionaryProcessor
from .online_currency import OnlineCurrencyProcessor
from .abstract import EngineProcessor

logger = logger.getChild('search.processors')
processors = {}
"""Cache request processores, stored by *engine-name* (:py:func:`initialize`)"""

def get_processor_class(engine_type):
    """Return processor class according to the ``engine_type``"""
    for c in [OnlineProcessor, OfflineProcessor, OnlineDictionaryProcessor, OnlineCurrencyProcessor]:
        if c.engine_type == engine_type:
            return c
    return None

def get_processor(engine, engine_name):
    """Return processor instance that fits to ``engine.engine.type``)"""
    engine_type = getattr(engine, 'engine_type', 'online')
    processor_class = get_processor_class(engine_type)
    if processor_class:
        return processor_class(engine, engine_name)
    return None

def initialize(engine_list):
    """Initialize all engines and store a processor for each engine in :py:obj:`processors`."""
    engines.initialize_engines(engine_list)
    for engine_name, engine in engines.engines.items():
        processor = get_processor(engine, engine_name)
        if processor is None:
            logger.error('Error get processor for engine %s', engine_name)
        else:
            processors[engine_name] = processor
