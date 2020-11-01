from typing import List

import typer  # type: ignore

from . import auth
from .utils.completion_utils import dimensions, export_type, month_complete, searchtype
from .utils.date_utils import (
    create_date,
    days_last_util,
    get_day_granularity,
    get_today,
    process_date,
)
from .utils.path_utils import create_toml_list
from .utils.query_utils import query_builder, query_deleter, query_lister
from .utils.selector_utils import create_granularity_selector, create_selector

app = typer.Typer(add_completion=False, name="Seoman")
query_app = typer.Typer(
    add_completion=False, name="Seoman", short_help="Create and run your queries."
)
app.add_typer(query_app, name="query")


@app.command("auth")
def get_auth():
    """
    Get authenticated.
    """

    auth.get_authenticated()


@app.command("manual")
def manual(
    url: str = typer.Option(..., help="That's how world wide web works."),
    start_date: str = typer.Option(
        None, help="Give a date to start [Example: 2020-03, 2 months ago, 4 ay önce]"
    ),
    end_date: str = typer.Option(
        None,
        help="Give a date to end [Example: 2020-08-11, 23 hours ago, yaklaşık 23 saat önce]",
    ),
    search_type: str = typer.Option(
        None, help="Search type ", autocompletion=searchtype
    ),
    dimensions: List[str] = typer.Option(
        None, help="Add dimensions ", autocompletion=dimensions
    ),
    row_limit: int = typer.Option(
        None, help="Maximum number of rows to return [Default is 1,000] "
    ),
    start_row: int = typer.Option(None, help="Set starting index [Default is 0]"),
    export: str = typer.Option(
        None, help="Specify export type ", autocompletion=export_type,
    ),
    granularity: str = typer.Option(
        None,
        help="Set a frequency/granularity or group your queries [Example: daily, twodaily, monday, tuesday, weekdays, weekends]",
    ),
):

    """
    Top pages in the site
    """
    service = auth.load_service()

    if start_date is not None:
        start = process_date(dt=start_date, which_date="start")
    if end_date is not None:
        end = process_date(dt=end_date, which_date="end")

    service.update_body({"startDate": start, "endDate": end or get_today()})

    if len(dimensions) >= 1:
        if "all" in dimensions:
            service.update_body(
                {"dimensions": ["date", "page", "query", "country", "device"]}
            )
        else:
            service.update_body({"dimensions": [dimension for dimension in dimensions]})

    if search_type is not None:
        service.update_body({"searchType": search_type})

    if row_limit is not None:
        service.update_body({"rowLimit": row_limit})

    if start_row is not None:
        service.update_body({"startRow": start_row})

    service.concurrent_query_asyncio(url=url, granularity=granularity or "daily")
    service.export(export_type=export, url=url, command="manual")


@app.command("sites")
def show_sites(
    url: str = typer.Option(None, help="Retrieve information about specific site."),
    export: str = typer.Option(
        None, help="Specify export type ", autocompletion=export_type,
    ),
):
    """
    List all the web sites or the permission level for the specific site that associated with the account.
    """

    service = auth.load_service()

    service.sites(url=url or None)

    service.export(export_type=export, command="sites", url=url or "seoman")


@app.command("sitemaps")
def show_sitemap(
    url: str = typer.Option(
        ..., help="The site's URL [Example: http://www.example.com/]"
    ),
    feedpath: str = typer.Option(
        None,
        help="The URL of the actual sitemap [Example: http://www.example.com/sitemap.xml]",
    ),
    export: str = typer.Option(
        None, help="Specify export type ", autocompletion=export_type,
    ),
):
    """
    List sitemaps-entries or get specific the sitemaps.
    """

    service = auth.load_service()

    service.sitemaps(url=url or None, feedpath=feedpath or None)

    service.export(export_type=export, command="sitemaps", url=url or "seoman")


@app.command("traffic")
def show_traffic(
    days: int = typer.Argument(None, help="Get total traffic from last given days."),
    site: str = typer.Option(
        None, help="Get traffic from specific website instead of all."
    ),
    export: str = typer.Option(
        None, help="Specify export type.", autocompletion=export_type,
    ),
):
    """
    Get total traffic from your sites.
    """

    service = auth.load_service()

    days = days or 30
    start, end = (
        days_last_util(days).get("startDate"),
        days_last_util(days).get("endDate"),
    )
    service.get_traffic(site=site or None, days=days)

    service.export(
        export_type=export or "table", command="traffic", url=f"{start}-{end}"
    )


@app.command("feedback")
def give_feedback():
    """
    Give us a feedback about your experience.
    """

    import webbrowser

    link = "https://github.com/zeoagency/seoman/issues/new"
    try:
        webbrowser.open(url=link)
    except webbrowser.Error:
        typer.secho(
            f"We could not find the browser, you can give us a feedback by visiting this link: {link}",
            bold=True,
            fg=typer.colors.RED,
        )


@app.command("version")
def show_version():
    """
    Show version and exit.
    """

    import pkg_resources

    typer.echo(pkg_resources.get_distribution("seoman").version)


@query_app.command("run")
def run_query(
    url: str = typer.Argument(
        None, help="Enter a url to override default one(If there is one.)"
    )
):
    """
    Select a query then run it.
    """
    name = create_selector(
        key="name", message="Select a query.", choices=create_toml_list()
    )
    service = auth.load_service()
    service.process_toml(filename=name)

    start_date, end_date = (
        service.__dict__["body"]["startDate"],
        service.__dict__["body"]["endDate"],
    )
    granularity = create_granularity_selector(start=start_date, end=end_date)

    try:
        toml_url, export_type = (
            service.__dict__["utils"]["url"],
            service.__dict__["utils"]["export-type"],
        )

    except KeyError:
        typer.secho(
            f"An error occured: Make sure you have export-type and url in your {name} file.",
            bold=True,
            fg=typer.colors.RED,
        )
        exit()

    service.concurrent_query_asyncio(
        url=url if url is not None else toml_url, granularity=granularity or "daily"
    )

    service.export(
        export_type=export_type, url=url if url is not None else toml_url, command=name
    )


@query_app.command("add")
def add_query():
    """
    Build a query interactively.
    """

    name = query_builder()

    _run = typer.confirm(f"{name} created successfully. Do you want to run it?")

    if _run:
        service = auth.load_service()
        service.process_toml(filename=name)
        start_date, end_date = (
            service.__dict__["body"]["startDate"],
            service.__dict__["body"]["endDate"],
        )
        granularity = create_granularity_selector(start=start_date, end=end_date)

        try:
            toml_url, export_type = (
                service.__dict__["utils"]["url"],
                service.__dict__["utils"]["export-type"],
            )

        except KeyError:
            typer.secho(
                f"An error occured: Make sure you have export-type and url in your {name} file.",
                bold=True,
                fg=typer.colors.RED,
            )
            exit()

        service.concurrent_query_asyncio(
            url=toml_url, granularity=granularity or "daily"
        )

        service.export(export_type=export_type, url=toml_url, command=name)


@query_app.command("delete")
def delete_query():
    """
    Delete a query.
    """

    selected = create_selector(
        key="toml_name", message="Select a query to delete.", choices=create_toml_list()
    )

    query_deleter(filename=selected)
    return


@query_app.command("show")
def show_query():
    """
    Show details from selected query.
    """

    selected = create_selector(
        key="toml_name",
        message="Select a query to list details.",
        choices=create_toml_list(),
    )
    query_lister(filename=selected)
