from abc import abstractmethod
from typing import Set, Any, Union, List, Optional, Dict, Tuple

from loguru import logger

from .ausearch import Node, AuSearch
from ciphey.iface import SearchLevel, Config, registry, CrackResult, Searcher, ParamSpec, Decoder, DecoderComparer

import bisect


class Perfection(AuSearch):
    @staticmethod
    def getParams() -> Optional[Dict[str, ParamSpec]]:
        pass

    def findBestNode(self, nodes: Set[Node]) -> Node: return next(iter(nodes))

    def handleDecodings(self, target: Any) -> (bool, Union[Tuple[SearchLevel, str], List[SearchLevel]]):
        ret = []

        decoders = []

        for decoder_type, decoder_class in registry[Decoder][type(target)].items():
            for decoder in decoder_class:
                decoders.append(DecoderComparer(decoder))
        # Fun fact:
        #   with Python's glorious lists, a inserting n elements into the right position (with bisect) is O(n^2)
        #decoders.sort(reverse=True)

        for decoder_cmp in decoders:
            res = self._config()(decoder_cmp.value).decode(target)
            if res is None:
                continue
            level = SearchLevel(
                name=decoder_cmp.value.__name__.lower(),
                result=CrackResult(value=res)  # FIXME: CrackResult[decoder_type]
            )
            if type(res) == self._final_type:
                check_res = self._checker(res)
                if check_res is not None:
                    return True, (level, check_res)
            ret.append(level)
        return False, ret

    def __init__(self, config: Config):
        super().__init__(config)
        self._checker = self._config().objs["checker"]
        self._final_type = config.objs["format"]["out"]


registry.register(Perfection, Searcher)
