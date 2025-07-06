import sys
import os
import subprocess
import getpass
from sqlalchemy import create_engine, text
import click
import geopandas as gpd
import webbrowser


def wsl_to_windows_path(wsl_path):
    return 

def open_browser(path):
    # Checks if this is run from wsl, otherwise runs like normal.
    if os.path.exists('/proc/version'):
        with open('/proc/version', 'r') as f:
            if 'microsoft' in f.read().lower() or 'wsl' in f.read().lower():

                # First translate to windows-style path
                result = subprocess.run(['wslpath', '-w', path], 
                          capture_output=True, text=True)
                win_path = result.stdout.strip()
                
                # Then open THAT path
                subprocess.run([
                    'cmd.exe', '/c', 'start', '""',
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    '--new-window',
                    '--profile-directory=Default',
                    win_path
                ])
                return
    
    # Regular Linux - use webbrowser module
    webbrowser.get('google-chrome').open(win_path)


@click.command()
@click.option("-c", "--command", "query", help="SQL query to execute")
@click.option("-f", "--file", "filename", help="File containing SQL query")
# @click.option("-F", "--data-file", "data_file", help="Filename of datafile to display.")
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
    "-h",
    "--host",
    "host",
    default="127.0.0.1",
    help="Hostname for connection (defaults to localhost)",
)
@click.option(
    "-p",
    "--port",
    "port",
    default='5432',
    help="Port name for connection (defaults to 5432)",
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
    "--cmap", "cmap", default='magma', help="Colormap from matplotlib for variable coloring"
)
def main(query, filename, database, username, host, port, geom_col, variable, cmap):
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
        f"postgresql+psycopg://{username}@{host}:{port}/{database}"
    )

    with engine.connect() as db:
        table = gpd.read_postgis(text(query), db, geom_col=geom_col)

    map_ = table.explore(column=variable, cmap=cmap, tiles='CartoDB positron')

    path = "/tmp/cartviz.html"

    map_.save(path)
    open_browser(path)


if __name__ == "__main__":
    main()
