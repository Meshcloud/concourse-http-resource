# HTTP Resource

Versions via HTTP GET/PUT to an arbitrary http URL.

## Source Configuration

* `index`: *Required.* Index URL to GET, can return arbitrary text. Typically contains a directory listing with html anchor tags pointing to each individual file.

* `regex`: *Required.* The regex used to extract available files from `index`. Typically used to extract the `href=` attribute value of a directory listing. The regex must contain a capture group, which is used to extract the version number (typically a filename).

* `uri_template`: *Required* The URI used to download a file. The string is interpolated using Python's `string.format` and can expand the `{version}` placeholder. This template is typically closely matched to the regex you use to extract files from the `index`. 

* `ssl_verify`: *Optional.* Verify SSL. Default value is `true`.

* `debug`: *Optional.* Log debug information on resource execution.

## Behavior

### `check`: Extract files from the index

Files will be found via the pattern configured by `regex`. The files
will be ordered by the version extracted from the first capture group (using [LooseVersion](http://epydoc.sourceforge.net/stdlib/distutils.version.LooseVersion-class.html)). Each filename is returned to concourse as an individual `version`.

If an existing version is specified to `check`, only files with a higher version number will be returned.


### `in`: Fetch an object from the index.

Places the following files in the destination:

* `(filename)`: The filename under which to store the downloaded resource. The string is interpolated using Python's `string.format` and can expand the `{version}` placeholder.

* `version`: The version identified in the file name.


### `out`: Upload an object to the bucket.

*Not implemented.*

## Developing
Run `make test` to ensure the resource works. The tests depend on https://httpbin.org/ to generate sample http responses. 

