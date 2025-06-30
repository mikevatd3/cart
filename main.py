import sys
import getpass
from sqlalchemy import create_engine, text
import click
import geopandas as gpd
import webbrowser


@click.command()
@click.option("-c", "--command", "query", help="SQL query to execute")
@click.option("-f", "--file", "filename", help="File containing SQL query")
@click.option(
    "-d", "--database", "database", help="Database to run query against"
)
@click.option(
    "-U",
    "--username",
    "username",
    default=getpass.getuser(),
    help="Database username (defaults to current user)",
)
@click.option(
    "-g",
    "--geom-col",
    "geom_col",
    default="geom",
    help="Output geometry column name (defaults to 'geom')",
)
@click.option(
    "-v", "--variable", "variable", default=None, help="Variable to set color"
)
@click.option(
    "--cmap", "cmap", default=None, help="Colormap from matplotlib for variable coloring"
)
def main(query, filename, database, username, geom_col, variable, cmap):
    if query:
        pass
    elif filename:
        with open(filename, "r") as f:
            query = f.read()
    elif not sys.stdin.isatty():
        query = sys.stdin.read()
    else:
        click.echo("Error: Provide query via -c, -f, or stdin", err=True)
        sys.exit(1)

    engine = create_engine(
        f"postgresql+psycopg://{username}@edw:5432/{database}"
    )

    with engine.connect() as db:
        table = gpd.read_postgis(text(query), db, geom_col=geom_col)

    map_ = table.explore(column=variable, cmap=cmap)

    path = "/tmp/cartviz.html"

    map_.save(path)
    webbrowser.open(path)


if __name__ == "__main__":
    main()
