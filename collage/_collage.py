"""
Functions to build the collage of contributors
"""
import re
import numpy as np
import matplotlib.pyplot as plt
import requests
from PIL import Image
from urllib import request


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


def generate_figure(contributors, ncols=7, title_fontsize=18):
    # Rows and columns size
    n_rows = int(np.ceil(len(contributors) / ncols))
    figsize = (4 * ncols, 4 * n_rows)

    # Make the figure
    fig, axes = plt.subplots(n_rows, ncols, figsize=figsize)
    for ax in axes.ravel():
        ax.set_axis_off()
    for contributor, ax in zip(contributors, axes.ravel()):
        url = f"https://github.com/{contributor}.png"
        image = np.array(Image.open(request.urlopen(url)))
        ax.imshow(image)
        ax.set_title(contributor, fontsize=title_fontsize)
    return fig
