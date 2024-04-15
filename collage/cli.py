import os
import click
import requests

IGNORE = set(["quantifiedcode-bot"])


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("image", type=click.File("wb"))
@click.option(
    "--organization",
    "-o",
    default="simpeg",
    show_default=True,
    help="GitHub organization",
)
@click.option(
    "--repositories",
    "-r",
    multiple=True,
    default=["simpeg", "discretize", "pydiso", "geoana", "aurora", "pymatsolver"],
    show_default=True,
    help="List of repositories",
)
@click.option(
    "--ignore",
    "-i",
    multiple=True,
    default=None,
    show_default=True,
    help="Ignore this contributor from the collage.",
)
@click.option(
    "--add",
    "-a",
    multiple=True,
    default=None,
    show_default=True,
    help="Add this contributor to the collage.",
)
@click.option(
    "--ncols",
    default=7,
    show_default=True,
    help="Number of columns used in the collage picture",
)
@click.option(
    "--dpi",
    default=72,
    show_default=True,
    help="DPI for the output image.",
)
@click.option(
    "--fontsize",
    default=18,
    show_default=True,
    help="Fontsize for contributors names.",
)
@click.option(
    "--gh-username",
    default=None,
    show_default=True,
    help="GitHub username to use with the token.",
)
@click.option(
    "--gh-token",
    default=None,
    show_default=True,
    help="GitHub token for the passed GitHub username.",
)
@click.option(
    "--contributors-per-page",
    default=1000,
    show_default=True,
    help=(
        "Number of contributors that will be requested to GitHub. "
        "Make sure this number is higher than the amount of contributors to "
        "the repository."
    ),
)
def cli(
    image,
    organization,
    repositories,
    ignore,
    add,
    ncols,
    dpi,
    fontsize,
    gh_username,
    gh_token,
    contributors_per_page,
):
    from ._collage import get_contributors, get_authors, generate_figure  # lazy imports

    # Get default list of ignored contributors from the global variable or from
    # an env variable
    if (key := "COLLAGE_IGNORE") in os.environ:
        default_ignore = set([c.strip() for c in os.environ[key].split(",")])
    else:
        default_ignore = IGNORE

    # Sanitize inputs
    repositories = [r.strip() for r in repositories]

    if ignore is None:
        ignore = set()
    else:
        ignore = set([c.strip() for c in ignore])
    ignore |= default_ignore  # union of the two sets

    if add is None:
        add = set()
    else:
        add = set([c.strip() for c in add])

    # Get contributors
    contributors = []
    for repo in repositories:
        contributors += get_contributors(
            organization,
            repo,
            gh_username,
            gh_token,
            contributors_per_page=contributors_per_page,
        )
    contributors = set(contributors)

    # Get authors
    authors = []
    for repo in repositories:
        try:
            new_authors = get_authors(organization, repo)
        except requests.HTTPError as e:
            click.echo(e, err=True)
        else:
            authors += new_authors
    authors = set(authors)

    # Put them together
    contributors |= authors  # union of the two sets

    # Remove unwanted ones
    contributors -= ignore  # remove contributors that should be ignored

    # Add required ones
    contributors |= add

    # Sort them with a case-insensitive manner
    contributors = list(contributors)
    contributors.sort(key=lambda s: s.lower())

    # Verbose
    click.echo("\nCollected contributors:")
    click.echo("-----------------------")
    for contributor in contributors:
        click.echo(f"- {contributor}")

    # Generate image
    click.echo("\nGenerating image...")
    fig = generate_figure(contributors, ncols=ncols, title_fontsize=fontsize)

    # Save image
    fig.savefig(image, dpi=dpi, bbox_inches="tight", pad_inches=0.1)
    click.echo(f"\nDone! 🎉 Collage image saved in '{image.name}'.")
