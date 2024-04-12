import click
import requests


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
    default="simpeg,discretize,pydiso,geoana,aurora,pymatsolver",
    show_default=True,
    help="List of repositories",
)
@click.option(
    "--ignore",
    default="quantifiedcode-bot",
    show_default=True,
    help="Ignore this contributors, don't add them to the collage",
)
@click.option(
    "--extend-ignore",
    default=None,
    show_default=True,
    help="Extend the list of ignored contributors",
)
@click.option(
    "--include",
    default=None,
    show_default=True,
    help="Include these contributors to the collage",
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
def cli(
    image,
    organization,
    repositories,
    ignore,
    extend_ignore,
    include,
    ncols,
    dpi,
    fontsize,
    gh_username,
    gh_token,
):
    from ._collage import get_contributors, get_authors, generate_figure  # lazy imports

    # Sanitize inputs
    repositories = [r.strip() for r in repositories.split(",")]

    if ignore is None:
        ignore = set()
    else:
        ignore = set([c.strip() for c in ignore.split(",")])
    if extend_ignore is None:
        extend_ignore = set()
    else:
        extend_ignore = set([c.strip() for c in extend_ignore.split(",")])
    ignore_contributors = ignore | extend_ignore  # union of the two sets

    if include is None:
        include = set()
    else:
        include = set([c.strip() for c in include.split(",")])

    # Get contributors
    contributors = []
    for repo in repositories:
        contributors += get_contributors(organization, repo, gh_username, gh_token)
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
    contributors -= ignore_contributors  # remove contributors that should be ignored

    # Add required ones
    contributors |= include

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
