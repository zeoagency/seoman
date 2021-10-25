from datetime import date, datetime
from time import strftime, strptime
from typing import Any, List, Union

import inquirer  # type: ignore
import typer  # type: ignore

from .config_utils import ALL_GRANULARITIES


def create_selector(key: str, message: str, choices: List) -> Any:
    """
    Generic function that creates a dropdown selector from any list.
    """

    questions = [inquirer.List(name=key, message=message, choices=choices)]
    answer = inquirer.prompt(questions)
    return answer[key]


def create_granularity_selector(start: Union[str, date, datetime], end: Union[str, date, datetime]) -> str:
    """Create a dropdown selector for granularity & frequency."""

    start, end = (
        strftime("%d %b %Y", strptime(start, "%Y-%m-%d")
                 if isinstance(start, str) else start.timetuple()),
        strftime("%d %b %Y", strptime(end, "%Y-%m-%d")
                 if isinstance(end, str) else end.timetuple()),
    )

    questions = [
        inquirer.List(
            name="granularity",
            message=f"How frequently you would like to get your data between {start} and {end}",
            choices=ALL_GRANULARITIES,
        )
    ]

    answer = inquirer.prompt(questions)
    return answer["granularity"]
