from typing import List


def searchtype() -> List[str]:
    return ["auto", "byPage", "byProperty"]


def dimensions() -> List[str]:
    return ["country", "query", "date", "device", "searchAppearance"]


def export_type() -> List[str]:
    return ["json", "csv", "table", "excel", "tsv"]


def month_complete() -> List[str]:
    return ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
