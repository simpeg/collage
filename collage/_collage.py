"""
Functions to build the collage of contributors
"""
import sys
import re
import numpy as np
import matplotlib.pyplot as plt
import requests


def get_contributors(organization, repository, github_username=None, github_token=None):
    url = f"https://api.github.com/repos/{organization}/{repository}/contributors"
    auth = None
    if github_username is not None and github_token is not None:
        auth = (github_username, github_token)
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    contributors = [entry["login"] for entry in response.json()]
    return contributors


def get_authors(organization, repo, authors_fname="AUTHORS.rst"):
    # Get content of authors file in repo
    url = (
        f"https://raw.githubusercontent.com/{organization}/{repo}/main/{authors_fname}"
    )
    response = requests.get(url)
    response.raise_for_status()
    # Get github handle of authors
    authors = re.findall("@([A-Za-z0-9-]+)", response.text)
    authors.sort()
    return authors


def generate_figure(contributors, ncols=7):
    # Rows and columns size
    n_rows = int(np.ceil(len(contributors) / ncols))
    figsize = (4 * ncols, 4 * n_rows)

    # Make the figure
    fig, axes = plt.subplots(n_rows, ncols, figsize=figsize)
    for ax in axes.ravel():
        ax.set_axis_off()
    for contributor, ax in zip(contributors, axes.ravel()):
        ax.imshow(plt.imread(f"https://github.com/{contributor}.png"))
        ax.set(title=contributor)
    return fig


def main():
    organization = "simpeg"
    repos = ["simpeg", "discretize", "pydiso", "geoana", "aurora", "pymatsolver"]
    ignore_contributors = ["quantifiedcode-bot", "thibaut-kobold", "cgohlke"]
    include_contributors = ["leonfoks"]

    # Get username and tokens from command line args
    github_username = sys.argv[1]
    github_token = sys.argv[2]

    # Get contributors
    contributors = []
    for repo in repos:
        contributors += get_contributors(
            organization, repo, github_username, github_token
        )

    # Get authors
    authors = []
    for repo in repos:
        try:
            new_authors = get_authors(organization, repo)
        except requests.HTTPError as e:
            print(e)
        else:
            authors += new_authors

    # Put them together
    contributors = list(set(contributors + authors))

    # Remove unwanted ones
    contributors = [c for c in contributors if c not in ignore_contributors]

    # Add required ones
    contributors += include_contributors

    # Sort them with a case-insensitive manner
    contributors.sort(key=lambda s: s.lower())

    fig = generate_figure(contributors)
    fig.savefig("SimPEG_Contributors.png", dpi=72, bbox_inches="tight", pad_inches=0.1)


if __name__ == "__main__":
    main()
