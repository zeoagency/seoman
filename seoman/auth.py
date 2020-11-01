import collections.abc
import json
import sys
from pathlib import Path
from typing import IO, Any, Dict, List, Optional, Union

import typer  # type: ignore
from apiclient import discovery  # type: ignore
from google.oauth2.credentials import Credentials  # type: ignore
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore

from .exceptions import BrokenFileError
from .service import SearchAnalytics
from .utils import selector_utils


def authenticate(
    client_config: Union[str, Path] = None,
    credentials: Union[Any, Dict[str, Dict[str, str]]] = None,
    serialize: Union[str, Path] = None,
    flow: str = "web",
) -> SearchAnalytics:

    if not credentials:

        if isinstance(client_config, collections.abc.Mapping):

            auth_flow = InstalledAppFlow.from_client_config(
                client_config=client_config,
                scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
            )

        elif isinstance(client_config, str):
            try:
                auth_flow = InstalledAppFlow.from_client_secrets_file(
                    client_secrets_file=client_config,
                    scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
                )
            except FileNotFoundError:
                typer.secho(
                    "\nAuthentication failed ❌\nReason: client_secrets.json not found in your current directory.",
                    fg=typer.colors.RED,
                    bold=True,
                )
                sys.exit()

        else:
            raise BrokenFileError("Client secrets must be a mapping or path to file")

        if flow == "web":
            auth_flow.run_local_server()
        elif flow == "console":
            auth_flow.run_console()
        else:
            raise ValueError("Authentication flow '{}' not supported".format(flow))

        credentials = auth_flow.credentials

    else:

        if isinstance(credentials, str):
            try:
                with open(credentials, "r") as f:
                    credentials = json.load(f)
            except FileNotFoundError:
                typer.secho(
                    "\nAuthentication failed ❌\nReason: credentials.json not found in your current directory.",
                    fg=typer.colors.RED,
                    bold=True,
                )
                sys.exit()

        credentials = Credentials(
            token=credentials["token"],
            refresh_token=credentials["refresh_token"],
            id_token=credentials["id_token"],
            token_uri=credentials["token_uri"],
            client_id=credentials["client_id"],
            client_secret=credentials["client_secret"],
            scopes=credentials["scopes"],
        )

    service = discovery.build(
        serviceName="webmasters",
        version="v3",
        credentials=credentials,
        cache_discovery=False,
    )

    if serialize:

        if isinstance(serialize, str):

            serialized = {
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "id_token": credentials.id_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes,
            }

            with open(serialize, "w") as f:
                json.dump(serialized, f, indent=4)

        else:
            raise TypeError("`serialize` must be a path.")

    return SearchAnalytics(service, credentials)


def load_service(
    credentials: Optional[str] = f"{Path.cwd()}/credentials.json",
) -> SearchAnalytics:

    service = authenticate(credentials=credentials)
    return service


def get_authenticated(
    client_config: Optional[str] = f"{Path.cwd()}/client_secrets.json",
    serialize: Optional[str] = f"{Path.cwd()}/credentials.json",
) -> SearchAnalytics:

    path = Path.cwd().glob("*.json")

    # Files comes like PosixPath("/some/path.toml") we are converting it to just filename without extension
    files: Union[List[Path], List[str]] = [
        str(file).split("/")[-1].replace(".json", "") for file in path if file.is_file()
    ]

    cred_files = [file for file in files if str(file).startswith("client_secret")]

    if len(cred_files) == 1:
        client_config = str(cred_files[0]) + ".json"
    elif len(cred_files) > 1:
        client_config = (
            selector_utils.create_selector(
                key="config",
                message="More than 1 file found that starts with client_secret, select one.",
                choices=cred_files,
            )
            + ".json"
        )
    else:
        typer.secho(
            "nAuthentication failed ❌\nReason: We could not find the client_secrets in your current directory"
        )

    service = authenticate(client_config=client_config, serialize=serialize)
    typer.secho("Authentication complete ✅\n", fg=typer.colors.GREEN, bold=True)
    typer.secho(
        "seoman is brought to you by https://seo.do - world's most powerful rank tracker tool made by technical SEO's for large companies and agencies.",
        fg=typer.colors.BRIGHT_BLUE,
        bold=True,
    )
    return service
