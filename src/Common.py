from typing import Callable
from collections.abc import Iterable
import random
import decimal
import os

type number = int | float | decimal.Decimal


not_bellow_zero: Callable[[number], number] = lambda x: x if x >= 0 else 0

def shuffle[T](sequence: Iterable[T]) -> list[T]:
    sequence_as_list: list[T] = list(sequence)
    new_list_shuffle_index_list: list[int]= list(range(len(sequence_as_list)))
    new_list: list[T] = sequence_as_list.copy()
    random.shuffle(new_list_shuffle_index_list)
    for Index, item in enumerate(new_list_shuffle_index_list):
        new_list[Index] = sequence_as_list[item]
    return new_list

listdir_with_file_ending: Callable[[str, list[str]], list[str]] = \
        lambda path, allowed_endings: list(filter(
                lambda item: any([item.endswith(ending) for ending in allowed_endings]), 
                os.listdir(path)
                ))



