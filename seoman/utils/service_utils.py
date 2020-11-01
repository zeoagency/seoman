from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List

import typer  # type: ignore
from google.auth.exceptions import RefreshError  # type: ignore

from .. import auth
from .date_utils import create_date_range


def create_body_list(
    body: Dict[Any, Any], new_body: List[Dict[Any, Any]] = [], granularity: str = None,
) -> List[Dict[Any, Any]]:
    """
    Gets a body, and creates a new body from that.
    """
    dates = create_date_range(
        start=body.get("startDate"), end=body.get("endDate"), granularity=granularity,
    )
    if granularity is not None:

        if granularity in [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]:
            for idx in range(len(dates)):
                try:
                    """
                    If the detail level is low, medium or high
                    reduce end day by one to prevent duplications.
                    """
                    body.update({"startDate": dates[idx], "endDate": dates[idx]})
                    new_body.append(body.copy())
                except IndexError:
                    pass

        else:
            for idx in range(len(dates)):
                try:
                    """
                    If the detail level is low, medium or high
                    reduce end day by one to prevent duplications.
                    """
                    body.update(
                        {
                            "startDate": dates[idx],
                            "endDate": (
                                datetime.strptime(dates[idx + 1], "%Y-%m-%d")
                                - timedelta(days=1)
                            ).strftime("%Y-%m-%d"),
                        }
                    )
                    new_body.append(body.copy())
                except IndexError:
                    pass
    else:
        for date in dates:
            body.update({"startDate": date, "endDate": date})
            new_body.append(body.copy())

    return new_body


def path_exists(filename: str) -> bool:
    """
    Checks for the given file path exists.
    """
    from pathlib import Path

    return Path(filename).exists()


def regenerate_credentials(method: Callable) -> Callable:
    """
    If query raises RefreshError(Expired token causes this.)
    It automatically regenerate credentials
    and runs the method again.
    """

    def run_query(*args, **kw):
        try:
            result = method(*args, **kw)
        except RefreshError:
            regen = typer.confirm(
                "Your credentials has expired, do you want to regenerate them?",
                default=True,
            )

            if regen is True:
                auth.get_authenticated()
                typer.secho(
                    "Authenticated successfully!",
                    fg=typer.colors.BRIGHT_GREEN,
                    bold=True,
                ),
                result = method(*args, **kw)
            else:
                msg = typer.secho("Aborting...", bold=True, fg=typer.colors.BRIGHT_RED,)
                exit()

        return result

    return run_query
