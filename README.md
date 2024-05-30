# ply2web

## how to run
``` bash
$ ./ply2web.py

$ ./ply2web.py --help
usage: ply2web.py [-h] [--ply-file PLY_FILE] [--spawn-host] [--port PORT] [--bind BIND]
                  [--spawn-web] [--web-serve] [--animation] [--upside-down] [-o OUTPUT_FILEPATH]

Serve a PLY point cloud file.

optional arguments:
  -h, --help            show this help message and exit
  --ply-file PLY_FILE   Path to the PLY file to visualize
  --spawn-host          Automatically spawn a GUI host app
  --port PORT           Bind port
  --bind BIND           Bind host address
  --spawn-web           Automatically spawn a web browser
  --web-serve           Disable a web browser
  --animation           Set animation
  --upside-down         Rotate model to upside-down
  -o OUTPUT_FILEPATH, --output-filepath OUTPUT_FILEPATH
                        Valid file format are (.png, .svg, .pdf, .ps, .eps, .tex)
```

## TODO
* [ ] try to show view cones
* [ ] show help how to control (h or ? key toggle)
* [ ] terminate the host app when pressing Ctrl+C in the terminal upon startup.
* [ ] activate the host app window using `--spawn-host`
* [ ] add options (e.g. --background-color)
