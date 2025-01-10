
def format_query_result(rows, column_names):
    """
    Transforms query result rows into a list of dictionaries based on column names.
    :param rows: List of tuples (query results).
    :param column_names: List of column names corresponding to the rows.
    :return: List of dictionaries representing the query result.
    """
    return [dict(zip(column_names, row)) for row in rows]

def format_single_query_result(row, column_names):
    """
    Transforms a single query result row into a dictionary based on column names.
    :param row: A tuple representing a single row (query result).
    :param column_names: List of column names corresponding to the row.
    :return: A dictionary representing the single query result.
    """
    if row is not None:
        return dict(zip(column_names, row))
    return None
