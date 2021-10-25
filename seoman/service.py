import sys
from datetime import datetime
from typing import IO, Any, Dict, List, Optional, Tuple, Union

import typer  # type: ignore
from click import progressbar  # type: ignore

from .exceptions import FolderNotFoundError
from .utils.date_utils import create_date, days_last_util, get_today
from .utils.export_utils import Export
from .utils.service_utils import create_body_list, path_exists, regenerate_credentials


class SearchAnalytics:
    """
    Class that handles all the events in Seoman.
    """

    def __init__(self, service, credentials) -> None:
        self.service = service
        self.credentials = credentials
        self.data: Union[Dict[Any, Any], Any] = {}
        self.body: Dict[Any, Any] = {
            "startRow": 0,
            "rowLimit": 25000,
        }
        self.utils: Dict[str, str] = {}

    def update_body(self, body: Dict[Any, Any]) -> None:
        """
        Updates the body, that we are going to use in the query
        """

        self.body.update(**body)

    @regenerate_credentials
    def concurrent_query_asyncio(self, url: str, granularity: str = None) -> None:
        """
        Run queries concurrently.
        """

        import asyncio

        from googleapiclient.errors import HttpError  # type: ignore

        bodies = create_body_list(self.body, granularity=granularity)
        extra_bodies = []

        async def con_query(body, query_type: str) -> None:
            start_row = 25000
            try:
                data = (
                    self.service.searchanalytics()
                    .query(siteUrl=url, body=body)
                    .execute()
                )
            except HttpError:
                await asyncio.sleep(2)
                try:
                    data = (
                        self.service.searchanalytics()
                        .query(siteUrl=url, body=body)
                        .execute()
                    )
                except HttpError:
                    pass

            try:
                self.data.setdefault("rows", []).append(data["rows"])

                if len(data["rows"]) > 24999 and query_type == "first":
                    new_body = body.copy()
                    new_body.update({"startRow": 24999})
                    extra_bodies.append(new_body)

            except (KeyError, UnboundLocalError):
                pass

        async def main(
            body_list: List[Dict[Any, Any]], message: str, query_type: str
        ) -> None:
            with progressbar(
                body_list,
                label=message,
                length=len(body_list),
                fill_char="█",
                empty_char=" ",
            ) as bod:
                for body in bod:
                    await con_query(body, query_type=query_type)

        asyncio.run(
            main(body_list=bodies, message="Fetching data", query_type="first"))

        if len(extra_bodies) >= 1:
            confirm_rows = typer.confirm(
                f"More than 25.000 rows found for {len(extra_bodies)} query, do you want to include them too?"
            )
            if confirm_rows:
                asyncio.run(
                    main(
                        body_list=extra_bodies,
                        message="Fetching more data",
                        query_type="second",
                    )
                )

    @regenerate_credentials
    def sites(self, url: Union[None, str] = None) -> None:
        """
        List all the web sites associated with the account.

        Info: https://developers.google.com/resources/api-libraries/documentation/webmasters/v3/python/latest/webmasters_v3.sites.html
        """

        if url:
            self.data.update(self.service.sites().get(siteUrl=url).execute())

        else:
            self.data.update(
                {
                    key: [
                        v for v in value if v["permissionLevel"] != "siteUnverifiedUser"
                    ]
                    for key, value in self.service.sites().list().execute().items()
                }
            )

    @regenerate_credentials
    def get_traffic(self, site: str = None, days: int = 30) -> None:
        """
        Get your site's traffic results by given days. [Default: 30]
        """
        import asyncio

        if site is None:
            self.sites()

            async def con_query(url, idx) -> None:
                self.data["siteEntry"][idx].update(
                    {
                        "impression": self.service.searchanalytics()
                        .query(siteUrl=url, body=days_last_util(days=days))
                        .execute()["rows"][0]
                    }
                )

            async def main() -> None:
                with progressbar(
                    self.data["siteEntry"],
                    label="Fetching data",
                    length=len(self.data["siteEntry"]),
                    fill_char="█",
                    empty_char=" ",
                ) as dat:
                    for idx, data in enumerate(dat):
                        await con_query(data["siteUrl"], idx)

            asyncio.run(main())

            self.data = sorted(
                list(self.data.values())[0],
                key=lambda x: (
                    x["impression"]["clicks"],
                    x["impression"]["impressions"],
                ),
                reverse=True,  # Sort data by descending order
            )

        else:
            self.data.update(
                {
                    "site": site,
                    "impression": self.service.searchanalytics()
                    .query(siteUrl=site, body=days_last_util(days=days))
                    .execute()["rows"][0],
                }
            )

    @regenerate_credentials
    def sitemaps(self, url: str, feedpath: Union[None, str] = None) -> None:
        """
        Lists the sitemaps-entries submitted for the given site.

        Info: https://developers.google.com/resources/api-libraries/documentation/webmasters/v3/python/latest/webmasters_v3.sitemaps.html
        """

        if url and feedpath:
            self.data.update(
                self.service.sitemaps().get(siteUrl=url, feedpath=feedpath).execute()
            )

        elif url:
            self.data.update(
                self.service.sitemaps().list(siteUrl=url).execute())

    def export(
        self, command: str, export_type: Optional[str] = None, url: str = None,
    ) -> None:
        """
        Specify the export type.
        """

        export_types = ["csv", "json", "tsv", "table"]

        if self.data == {"rows": []}:
            typer.secho(
                "Results are empty. Make sure you have the entered url and you have rights to run it.",
                fg=typer.colors.RED,
                bold=True,
            )
            sys.exit()

        export_data = Export(self.data)

        if command == ("sites" or "sitemaps") and export_type is None:
            export_data.export_to_table()

        elif export_type in ["CSV", "JSON", "TSV", "TABLE"]:
            export_type = export_type.lower()

        elif export_type == "csv":
            export_data.export_to_csv(
                filename=self._create_filename(
                    url=url, command=command, filetype=export_type
                )
            )

        elif export_type == "json":
            export_data.export_to_json(
                filename=self._create_filename(
                    url=url, command=command, filetype=export_type
                )
            )

        elif export_type == "tsv":
            export_data.export_to_tsv(
                filename=self._create_filename(
                    url=url, command=command, filetype="tsv")
            )

        elif export_type == "table":
            export_data.export_to_table()

        elif (
            export_type == "excel"
            or export_type == "xlsx"
            or export_type not in export_types
            or export_type is None
        ):
            export_data.export_to_excel(
                filename=self._create_filename(
                    url=url, command=command, filetype="xlsx"
                )
            )

    def _create_filename(self, url: Optional[str], command: str, filetype: str) -> str:
        """
        Creates a file name from timestamp, url and command.
        """

        from datetime import datetime

        def __clean_url(url: Optional[str]) -> str:
            for t in (
                ("https", ""),
                ("http", ""),
                (":", ""),
                ("sc-domain", ""),
                ("//", ""),
                ("/", "-"),
                ("--", "-"),
                (".", "-"),
                (",", "-"),
            ):
                if url is not None:
                    url = url.lower().replace(*t)

            return url or "query"

        def __create_name(file_exists: bool = False) -> str:
            from random import randint

            if not file_exists:
                return "-".join(
                    [
                        __clean_url(url),
                        command,
                        datetime.now().strftime(
                            "%d-%B-%Y-%H-%M") + f".{filetype}",
                    ]
                )

            return "-".join(
                [
                    __clean_url(url) or "sites",
                    command,
                    f"report-{randint(1,10000)}",
                    datetime.now().strftime("%d-%B-%Y-%H-%M") + f".{filetype}",
                ]
            )

        return (
            __create_name()
            if not path_exists(__create_name())
            else __create_name(file_exists=True)
            if not path_exists(__create_name(file_exists=True))
            else __create_name(file_exists=True)
        )

    def process_toml(self, filename: str) -> None:
        """
        Open and prepare toml files for querying.
        """

        from pathlib import Path

        import toml

        queries_path = Path.home() / ".queries"

        if not Path(queries_path).exists():
            typer.secho(
                "We couldn't find queries folder, make sure you are in the same directory.",
                fg=typer.colors.RED,
                bold=True,
            )

        if not filename.endswith(".toml"):
            if "." not in filename:
                filename = filename + ".toml"

        file_path = queries_path / filename
        with file_path.open("r") as file:
            query_file = toml.load(file)

        for key, value in query_file["query"].items():

            if key == "dimensions":
                if "all" in value:
                    self.update_body(
                        {"dimensions": ["date", "page",
                                        "query", "country", "device"]}
                    )
                else:
                    self.body.update(
                        {"dimensions": [dimension for dimension in value]})

            if key == "filters":
                self.body.update(
                    {
                        "dimensionFilterGroups": [
                            {
                                "filters": [
                                    {
                                        # Country
                                        "dimension": filters.split()[0],
                                        # Equals
                                        "operator": filters.split()[1],
                                        "expression": " ".join(
                                            filters.split()[2:]
                                        ),  # FRA
                                    }
                                    for filters in value
                                ]
                            }
                        ]
                    }
                )

            if key == "start-date":
                self.body.update({"startDate": value})

            if key == "end-date":
                self.body.update({"endDate": value})

            if key == "start-date":
                self.body.update({"startDate": value})

            if key == "search-type":
                self.body.update({"searchType": value})

            if key == "row-limit":
                self.body.update({"rowLimit": value})

            if key == "start-row":
                self.body.update({"startRow": value})

            if key == "export-type":
                self.utils.update({"export-type": value})

            if key == "url":
                self.utils.update({"url": value})
