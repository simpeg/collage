# collage: build image of SimPEG contributors

## Install

Install it with pip directly from the repo:

```sh
pip install git+https://github.com/simpeg/collage
```

## How to use

Run the `collage` command to generate the image, passing the path to the output
image as argument. For example:

```sh
collage image.png
```

Explore the available options with `collage --help`.

## Examples

### April 2024

Running this helped to generate a nice looking and updated version of the
SimPEG contributors:

```sh
collage --extend-ignore "thibaut-kobold,cgohlke" --include "leonfoks" --ncols 8 image.png
```

## License

Released under the [MIT License](LICENSE).
