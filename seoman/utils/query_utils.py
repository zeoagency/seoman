from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import inquirer  # type: ignore
import toml
import typer  # type: ignore

from seoman.utils.date_utils import process_date


def query_builder() -> str:
    typer.secho(
        """
    FORMATTING AND TIPS

    GENERAL FORMATTING
        [Tip] You are not supposed to answer questions if it is not [REQUIRED] 
        If you want to skip that question, just press space then enter.

    URL
        [Formatting: sc-domain:example.com or https://example.com]

    DATES
        [Formatting] Dates are in YYYY-MM-DD format.
        [Example] 23 march 2020 | 2020-03-10 | 2 weeks and 4 months ago 

    FILTERS
        [Formatting] If you want to add multiple filters split them by ',' 
        [Example] country equals FRA, device notContains tablet
        [Suggested Format] dimensions, operator, expression
    
    GRANULARITY
        Granularity specifies the frequency of the data, higher frequency means higher response time.
        [Examples] If you specify 'monday' seoman returns results only from mondays between start date and end date.
        [Examples] If you specify 'fivedaily' it splits your date range by 5 then runs unique queries.
        if your start date is 2020-03-10 and the end date is 2020-04-10 it first sends query for 03-10 to 03-15 then 03-15 to 03-20 then merges them all.   

    DIMENSIONS
        [Valid Parameters] page, query, date, device, country | for simplicity you can type 'all' to include all of them.
    
    EXPORT TYPE
        [Valid Parameters] excel, csv, json, tsv.

    ROW LIMIT
        [Valid Parameters] Must be a number from 1 to 25000.

    START ROW 
        [Valid Parameters] Must be a non-negative number.

    """,
        fg=typer.colors.BRIGHT_GREEN,
        bold=True,
    )

    questions = [
        inquirer.Text("url", message="[Required] The site's URL"),
        inquirer.Text(
            "start_date", message="[Required] Start date of the requested date range",
        ),
        inquirer.Text(
            "end_date", message="[Required] End date of the requested date range",
        ),
    ]

    answers = inquirer.prompt(questions)
    url = answers.get("url", "")
    start_date = answers.get("start_date", "")
    end_date = answers.get("end_date", "")

    questions = [
        inquirer.List(
            "dimensions",
            message="Which dimensions of Search Analytics you would like to group by?",
            choices=[
                "all [date, query, page, device, country]",
                "keywords & pages [date, query, page]",
                "by devices [date, device]",
                "by countries [date, countries]",
                "custom [Choose from: date - query - page - device - country]",
            ],
        ),
    ]

    answers = inquirer.prompt(questions)

    if (
        answers.get("dimensions")
        == "custom [Choose from: date - query - page - device - country]"
    ):
        questions = [
            inquirer.Checkbox(
                "dimensions",
                message="Which dimensions of Search Analytics you would like to group by?",
                choices=["date", "query", "page", "country", "device"],
            ),
        ]
        answers = inquirer.prompt(questions)
        dimensions = answers.get("dimensions", [])

    else:
        dimensions = answers.get("dimensions", "")

    questions = [
        inquirer.Text(
            "filters",
            message="Zero or more groups of filters to apply to the dimension grouping values",
        ),
        inquirer.Text(
            "start_row", message="First row of the response [Known as start-row]",
        ),
        inquirer.Text(
            "row_limit", message="The maximum number of rows to return [0-25000]",
        ),
        inquirer.List(
            "search_type",
            message="The search type to filter for",
            choices=["web", "image", "video"],
            default="web",
        ),
        inquirer.List(
            "export",
            message="The export type for the results",
            choices=["xlsx", "csv", "json", "tsv"],
        ),
    ]

    answers = inquirer.prompt(questions)
    filters = answers.get("filters", "")
    start_row = answers.get("start_row", "")
    row_limit = answers.get("row_limit", "")
    search_type = answers.get("search_type", "")
    export = answers.get("export", "")

    query: Dict[str, Dict[str, Any]] = {"query": {}}
    all_dimensions = ["page", "query", "date", "device", "country"]

    if len(url) > 5:
        query["query"].update({"url": url})

    if start_date.strip() != "":
        query["query"].update(
            {"start-date": process_date(dt=start_date, which_date="start")}
        )

    if end_date.strip() != "":
        query["query"].update({"end-date": process_date(dt=end_date, which_date="end")})

    if isinstance(dimensions, str):
        if dimensions == "all [date, query, page, device, country]":
            query["query"].update(
                {"dimensions": ["date", "query", "page", "device", "country"]}
            )

        elif dimensions == "keywords & pages [date, query, page]":
            query["query"].update({"dimensions": ["date", "query", "page"]},)

        elif dimensions == "by devices [date, device]":
            query["query"].update({"dimensions": ["date", "device"]},)

        elif dimensions == "by country [date, country]":
            query["query"].update({"dimensions": ["date", "country"]},)
    else:
        query["query"].update({"dimensions": [dim for dim in dimensions]})

    if filters.strip() != "":
        query["query"].update({"filters": [filt for filt in filters.split(",")]})

    if start_row.strip() != "" and start_row.isnumeric():
        query["query"].update({"start-row": start_row})

    if row_limit.strip() != "" and row_limit.isnumeric():
        if int(row_limit) >= 25000:
            row_limit = "25000"
        query["query"].update({"row-limit": row_limit.strip()})

    if search_type.strip() != "":
        query["query"].update({"search-type": search_type.strip().lower()})

    if export.strip() != "":
        query["query"].update({"export-type": export})

    typer.secho("\nYour query is ready\n", fg=typer.colors.BRIGHT_GREEN, bold=True)

    filename = typer.prompt("Give a name to your query") + ".toml"
    folder_path = Path.home() / ".queries"
    file_path = Path.home() / ".queries" / Path(filename)

    if not Path(folder_path).exists():
        Path(folder_path).mkdir(exist_ok=False)

    if not Path(file_path).exists():
        with open(file_path, "w") as file:
            toml.dump(query, file)

        return filename

    else:
        new_name = typer.prompt("File name already exists, enter a new name.") + ".toml"
        file_path = Path.home() / ".queries" / Path(new_name)

        if not Path(file_path).exists():
            with open(file_path, "w") as file:
                toml.dump(query, file)

    return new_name


def query_deleter(filename: str) -> None:
    """
    Delete a query from queries directory.
    """

    if not filename.endswith(".toml"):
        filename = filename + ".toml"

    p = Path.home() / ".queries" / filename

    p.unlink()


def query_lister(filename: str) -> None:
    """
    Show details of the selected query.
    """

    import toml
    from pytablewriter import UnicodeTableWriter  # type: ignore

    writer = UnicodeTableWriter()

    writer.table_name = filename

    if not filename.endswith(".toml"):
        filename = filename + ".toml"

    p = Path.home() / ".queries" / filename

    with open(str(p), "r") as file:
        query_file = toml.load(file)

    writer.headers = [k for k in query_file["query"]]
    writer.value_matrix = [
        [
            " ".join(v) if isinstance(v, list) else v
            for k, v in query_file["query"].items()
        ]
    ]

    writer.write_table()
