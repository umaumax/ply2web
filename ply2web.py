#!/usr/bin/env python3
import argparse
import sys
import tempfile
import json

import numpy as np
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
        '--web-serve',
        action='store_true',
        help='Disable a web browser')
    parser.add_argument(
        '--animation',
        action='store_true',
        help='Set animation')
    parser.add_argument(
        '--upside-down',
        action='store_true',
        help='Rotate model to upside-down')
    parser.add_argument('-o', '--output-filepath', default='',
                        help='Valid file format are (.png, .svg, .pdf, .ps, .eps, .tex)')
    args = parser.parse_args()

    pl = pv.Plotter(off_screen=not args.spawn_host)
    pl.set_background("#000000")

    if args.ply_file:
        mesh = pv.read(args.ply_file)
        if args.upside_down:
            mesh = mesh.rotate_x(180.0)
        try:
            pl.add_mesh(mesh, scalars='RGB', rgb=True)
        except Exception as e:
            print(f"[WARN] {repr(e)}")
            pl.add_mesh(mesh)
        print(mesh)
        print(f"boundary box diagonal length: {mesh.length}")
        points = mesh.points
        median_x = np.median(points[:, 0])
        median_y = np.median(points[:, 1])
        median_z = np.median(points[:, 2])
        median_point = (median_x, median_y, median_z)
        mean_x = np.mean(points[:, 0])
        mean_y = np.mean(points[:, 1])
        mean_z = np.mean(points[:, 2])

        mean_point = (mean_x, mean_y, mean_z)
        print("median point:", median_point)
        print("mean point:", mesh.center)
        print("center point:", mean_point)
        pl.add_text(
            f"filepath: {args.ply_file}\n# of points: {len(mesh.points)}\n median point: {median_point}",
            color='#FFFFFF',
            font_size=10)

        pl.camera.position = (
            mesh.center[0] + 0.0,
            mesh.center[1] + mesh.length * 2,
            mesh.center[2] + mesh.length * 2)
        pl.camera.focal_point = mesh.center
        pl.camera.up = (0.0, 0.0, 0.0)

    # plain
    if False:
        plain_mesh = pv.Plane(
            center=(
                0.0, -1.0, 0.0), direction=(
                0.0, 1.0, 0.0), i_size=10, j_size=10, i_resolution=100, j_resolution=100)
        plain_mesh.point_data.clear()
        pl.add_mesh(plain_mesh, show_edges=True)

        if mesh:
            pl.show_bounds(
                mesh=mesh,
                grid='front',
                color='#FFFFFF',
                location='outer',
                all_edges=True,
            )

    if args.output_filepath:
        if not args.animation:
            pl.screenshot(args.output_filepath)
        else:
            n_frames = 36

            fps = 9.0
            pl.open_gif(args.output_filepath, fps=fps)

            radius = mesh.length * 2
            focus = mesh.center
            for i in range(n_frames):
                angle = 2 * np.pi * i / n_frames
                x = focus[0] + radius * np.cos(angle)
                y = focus[1] + mesh.length * 2
                z = focus[2] + radius * np.sin(angle)
                position = (x, y, z)
                up = (0, 1, 0)
                pl.camera_position = [position, focus, up]

                pl.write_frame()
                continue

                rotated_mesh = mesh.copy().rotate_y(i * 360.0 / n_frames)
                pl.clear()
                try:
                    pl.add_mesh(rotated_mesh, scalars='RGB', rgb=True)
                except Exception as e:
                    print(f"[WARN] {repr(e)}")
                    pl.add_mesh(rotated_mesh)
                pl.write_frame()

            pl.close()
            return
    else:
        if args.animation:
            print("[WARN] Please set --output-filepath too.")

    if args.spawn_host:
        def print_cpos_callback():
            c = {
                "position": pl.camera.position,
                "focal_length": pl.camera.position,
                "up": pl.camera.up,
            }
            print("camera json")
            print(json.dumps(c))
            return

        pl.add_key_event("c", print_cpos_callback)

        def my_cpos_callback(*args):
            pl.add_text(f"camera.position: {pl.camera.position}\ncamera.focal_point: {pl.camera.focal_point}\ncamera.up: {pl.camera.up}",
                        color='#FFFFFF',
                        font_size=10, position='upper_right', name="cpos")
            return
        pl.track_click_position(callback=my_cpos_callback, side='left')

        pl.show_axes()
        pl.show(window_size=[1200 * 2, 800 * 2], auto_close=False)
        pl.close()
        sys.exit(0)

    server = get_server()
    state, ctrl = server.state, server.controller

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
                if args.upside_down:
                    mesh = mesh.rotate_x(180.0)
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
    if args.web_serve or args.spawn_web:
        server.start(
            port=args.port,
            host=args.bind,
            open_browser=args.spawn_web)

    if not args.web_serve and not args.output_filepath and not args.spawn_host:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
