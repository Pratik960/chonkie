"""Custom types for recursive chunking."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Literal

from chonkie.types.base import Chunk


@dataclass
class RecursiveLevel:
    """RecursiveLevels express the chunking rules at a specific level for the recursive chunker.

    Attributes:
        whitespace_delimiter (bool): Whether to use whitespace as a delimiter.
        custom_delimiters (list[str] | str | None): Custom delimiters for chunking.
        include_delim (Literal["prev", "next"] | None): Whether to include the delimiter at all, or in the previous chunk, or the next chunk.

    """

    whitespace_delimiter: bool = False
    custom_delimiters: list[str] | str | None = None
    include_delim: Literal["prev", "next"] | None = "prev"

    def _validate_fields(self) -> None:
        """Validate all fields have legal values."""
        if self.custom_delimiters is not None and self.whitespace_delimiter:
            raise NotImplementedError(
                "Cannot use whitespace as a delimiter and also specify custom delimiters."
            )
        if self.custom_delimiters is not None:
            if (
                isinstance(self.custom_delimiters, str)
                and len(self.custom_delimiters) == 0
            ):
                raise ValueError("Custom delimiters cannot be an empty string.")
            if isinstance(self.custom_delimiters, list):
                if any(
                    not isinstance(delim, str) or len(delim) == 0
                    for delim in self.custom_delimiters
                ):
                    raise ValueError(
                        "Custom delimiters cannot be an empty string."
                    )
                if any(delim == " " for delim in self.custom_delimiters):
                    raise ValueError(
                        "Custom delimiters cannot be whitespace only. Set whitespace_delimiter to True instead."
                    )

    def __post_init__(self) -> None:
        """Validate attributes."""
        self._validate_fields()

    def __repr__(self) -> str:
        """Return a string representation of the RecursiveLevel."""
        return (
            f"RecursiveLevel(delimiters={self.custom_delimiters}, "
            f"whitespace={self.whitespace_delimiter}, include_delim={self.include_delim})"
        )

    def to_dict(self) -> dict:
        """Return the RecursiveLevel as a dictionary."""
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict) -> "RecursiveLevel":
        """Create RecursiveLevel object from a dictionary."""
        return cls(**data)


@dataclass
class RecursiveRules:
    """Expression rules for recursive chunking."""

    levels: list[RecursiveLevel] | RecursiveLevel | None = None

    def __post_init__(self):
        """Validate attributes."""
        if self.levels is None:
            paragraphs = RecursiveLevel(
                custom_delimiters=["\n", "\n\n", "\r\n"]
            )
            sentences = RecursiveLevel(
                custom_delimiters=[
                    ".",
                    "!",
                    "?",
                ],
            )
            pauses = RecursiveLevel(
                custom_delimiters=[
                    "{",
                    "}",
                    '"',
                    "[",
                    "]",
                    "<",
                    ">",
                    "(",
                    ")",
                    ":",
                    ";",
                    ",",
                    "—",
                    "|",
                    "~",
                    "-",
                    "...",
                    "`",
                    "'",
                ],
            )
            word = RecursiveLevel(whitespace_delimiter=True)
            token = RecursiveLevel()
            self.levels = [paragraphs, sentences, pauses, word, token]
        elif isinstance(self.levels, RecursiveLevel):
            self.levels._validate_fields()
        elif isinstance(self.levels, list):
            for level in self.levels:
                level._validate_fields()
        else:
            raise ValueError(
                "Levels must be a RecursiveLevel object or a list of RecursiveLevel objects."
            )

    def __repr__(self) -> str:
        """Return a string representation of the RecursiveRules."""
        return f"RecursiveRules(levels={self.levels})"

    def __len__(self) -> int:
        """Return the number of levels."""
        return len(self.levels)

    def __getitem__(self, index: int) -> RecursiveLevel:
        """Return the RecursiveLevel at the specified index."""
        if isinstance(self.levels, list):
            return self.levels[index]
        raise TypeError(
            "Levels must be a list of RecursiveLevel objects to use indexing."
        )

    def __iter__(self) -> Iterator[RecursiveLevel]:
        """Return an iterator over the RecursiveLevels."""
        if isinstance(self.levels, list):
            return iter(self.levels)
        raise TypeError(
            "Levels must be a list of RecursiveLevel objects to use iteration."
        )

    @classmethod
    def from_dict(cls, data: dict) -> "RecursiveRules":
        """Create a RecursiveRules object from a dictionary."""
        dict_levels = data.pop("levels")
        object_levels = None
        if dict_levels is not None:
            if isinstance(dict_levels, dict):
                object_levels = RecursiveLevel.from_dict(dict_levels)
            elif isinstance(dict_levels, list):
                object_levels = [
                    RecursiveLevel.from_dict(d_level) for d_level in dict_levels
                ]
        return cls(levels=object_levels)

    def to_dict(self) -> dict:
        """Return the RecursiveRules as a dictionary."""
        result = dict()
        result["levels"] = None
        if isinstance(self.levels, RecursiveLevel):
            result["levels"] = self.levels.to_dict()
        elif isinstance(self.levels, list):
            result["levels"] = [level.to_dict() for level in self.levels]
        else:
            raise ValueError(
                "Levels must be a RecursiveLevel object or a list of RecursiveLevel objects."
            )
        return result


@dataclass
class RecursiveChunk(Chunk):
    """Class to represent recursive chunks.

    Attributes:
        recursive_level (int | None): The level of recursion for the chunk, if any.
        
    """

    recursive_level: int | None = None

    def str_repr(self) -> str:
        """Return a string representation of the RecursiveChunk."""
        return (
            f"RecursiveChunk(text={self.text}, start_index={self.start_index}, "
            f"end_index={self.end_index}, token_count={self.token_count}, "
            f"recursive_level={self.recursive_level})"
        )

    def __repr__(self) -> str:
        """Return a string representation of the RecursiveChunk."""
        return self.str_repr()

    def __str__(self):
        """Return a string representation of the RecursiveChunk."""
        return self.str_repr()

    def to_dict(self) -> dict:
        """Return the RecursiveChunk as a dictionary."""
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict) -> RecursiveChunk:
        """Create a RecursiveChunk object from a dictionary."""
        return cls(**data)
