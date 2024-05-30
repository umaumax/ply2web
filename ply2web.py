#!/usr/bin/env python3
import argparse
import sys
import tempfile

import pyvista as pv
from pyvista.trame.ui import plotter_ui
from trame.app import get_server
from trame.app.file_upload import ClientFile
from trame.ui.vuetify3 import SinglePageLayout
from trame.widgets import vuetify3


def main():
    parser = argparse.ArgumentParser(
        description='Serve a PLY point cloud file.')
    parser.add_argument(
        '--ply-file',
        default='',
        help='Path to the PLY file to visualize')
    parser.add_argument(
        '--spawn-host',
        action='store_true',
        help='Automatically spawn a GUI host app')
    parser.add_argument(
        '--port',
        type=int,
        default=38080,
        help='Bind port')
    parser.add_argument(
        '--bind',
        default='0.0.0.0',
        help='Bind host address')
    parser.add_argument(
        '--spawn-web',
        action='store_true',
        help='Automatically spawn a web browser')
    parser.add_argument(
        '--no-web-serve',
        action='store_true',
        help='Disable a web browser')
    parser.add_argument('-o', '--output-filepath', default='',
                        help='Valid file format are (.png)')
    args = parser.parse_args()

    pv.OFF_SCREEN = not args.spawn_host

    server = get_server()
    state, ctrl = server.state, server.controller

    pl = pv.Plotter()

    if args.ply_file:
        mesh = pv.read(args.ply_file)
        try:
            pl.add_mesh(mesh, scalars='RGB', rgb=True)
        except Exception as e:
            print(f"[WARN] {repr(e)}")
            pl.add_mesh(mesh)

    if args.output_filepath:
        pl.screenshot(args.output_filepath)

    if args.spawn_host:
        pl.show()
        # pl.close()
        sys.exit(0)

    @server.state.change("file_exchange")
    def handle(file_exchange, **kwargs):
        file = ClientFile(file_exchange)
        if file.content:
            print('[load]', file.info)
            bytes = file.content
            with tempfile.NamedTemporaryFile(suffix=file.name) as path:
                with open(path.name, 'wb') as f:
                    f.write(bytes)
                mesh = pv.read(path.name)
            try:
                pl.add_mesh(mesh, scalars='RGB', rgb=True, name=file.name)
            except Exception as e:
                print(f"[WARN] {repr(e)}")
                pl.add_mesh(mesh, name=file.name)
            pl.reset_camera()

    with SinglePageLayout(server) as layout:
        with layout.toolbar:
            vuetify3.VSpacer()
            vuetify3.VFileInput(
                show_size=True,
                small_chips=True,
                truncate_length=25,
                v_model=("file_exchange", None),
                density="compact",
                hide_details=True,
                style="max-width: 300px;",
            )
            vuetify3.VProgressLinear(
                indeterminate=True, absolute=True, bottom=True, active=("trame__busy",)
            )

        with layout.content:
            with vuetify3.VContainer(
                fluid=True, classes="pa-0 fill-height", style="position: relative;"
            ):
                view = plotter_ui(pl)
                ctrl.view_update = view.update
    if not args.no_web_serve:
        server.start(
            port=args.port,
            host=args.bind,
            open_browser=args.spawn_web)


if __name__ == '__main__':
    main()
