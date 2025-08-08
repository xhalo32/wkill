#!/usr/bin/env python3
import argparse, subprocess, sys, os, signal
from typing import Optional, Tuple
import i3ipc
from i3ipc import Connection, Con, Rect

def debug_print(msg: str, verbose: bool) -> None:
    if verbose:
        print("[DEBUG]", msg)

def get_click_coordinates(verbose: bool, pixel: bool = True) -> Optional[Tuple[int, int]]:
    slurp_cmd = ['slurp', '-p', '-b', '#00000000', '-c', '#ff0000ff'] if pixel \
        else ['slurp', '-b', '#00000000', '-c', '#ff0000ff']
    result = subprocess.run(slurp_cmd, capture_output=True, text=True)
    debug_print(f"slurp result: {result.stdout.strip()}", verbose)
    if result.returncode != 0 or not result.stdout.strip():
        print("Selection cancelled or error.")
        return None
    if pixel:
        coords, dimension = result.stdout.strip().split(' ')
        coords = coords.split(',')
        x, y = map(int, coords)
    else:
        coords = result.stdout.strip().split(' ')
        x, y = map(int, coords[0].split(','))
    debug_print(f"Click coordinates: x={x}, y={y}", verbose)
    return x, y

def get_focused_workspace(tree: Con, verbose: bool) -> Optional[Con]:
    focused: Optional[Con] = tree.find_focused()
    debug_print(f"Focused node: id={focused.id if focused else 'None'}, name={focused.name if focused else 'None'}, type={focused.type if focused else 'None'}", verbose)
    node = focused
    while node and node.type != 'workspace':
        node = node.parent
    if node:
        debug_print(f"Focused workspace: id={node.id}, name={node.name}", verbose)
    else:
        debug_print("No focused workspace found.", verbose)
    return node

def print_rect(node: Con) -> str:
    r: Rect = node.rect
    return f"x={r.x}, y={r.y}, w={r.width}, h={r.height}"

def window_contains_point(node: Con, x: int, y: int, verbose: bool) -> bool:
    rect: Rect = node.rect
    debug_print(f"Checking node id={node.id}, name={node.name}, type={node.type}, rect={print_rect(node)}, app_id={node.app_id}", verbose)
    return (
        rect.x <= x < rect.x + rect.width and
        rect.y <= y < rect.y + rect.height and
        node.type in ('con', 'floating_con') and
        node.ipc_data.get('visible') and
        (node.app_id or node.name)
    )

def find_topmost_window_under_cursor(workspace: Con, x: int, y: int, verbose: bool) -> Optional[Con]:
    debug_print(f"Floating nodes in workspace '{workspace.name}': {len(workspace.floating_nodes)} found", verbose)
    # Check floating windows first (topmost last in stacking order)
    for floating in reversed(workspace.floating_nodes):
        debug_print(f"Floating node id={floating.id}, name={floating.name}, type={floating.type}, rect={print_rect(floating)}", verbose)
        if window_contains_point(floating, x, y, verbose):
            debug_print(f"Matched FLOATING node id={floating.id}, name={floating.name}", verbose)
            return floating
        for desc in floating.descendants():
            debug_print(f"  Descendant id={desc.id}, name={desc.name}, type={desc.type}, rect={print_rect(desc)}", verbose)
            if window_contains_point(desc, x, y, verbose):
                debug_print(f"Matched FLOATING CHILD node id={desc.id}, name={desc.name}", verbose)
                return desc
    # If no floating window found, check tiled windows
    for node in workspace.descendants():
        if window_contains_point(node, x, y, verbose):
            debug_print(f"Matched TILED node id={node.id}, name={node.name}", verbose)
            return node
    debug_print("No window found under cursor.", verbose)
    return None


def get_pid(node: Con, verbose: bool) -> Optional[int]:
    pid = node.pid
    debug_print(f"Window id={node.id} name={node.name} app_id={node.app_id} pid={pid}", verbose)
    return pid

def kill_window(win: Con, dry_run: bool, verbose: bool, nice: bool) -> None:
    pid = get_pid(win, verbose)
    if pid is None:
        print("Could not find PID for the selected window.")
        return
    debug_print(f"Killing window id={win.id}, name={win.name}, app_id={win.app_id}, pid={pid}, dry_run={dry_run}, nice={nice}", verbose)
    if dry_run:
        print(f"[DRY-RUN] Would {'nicely ' if nice else ''}kill process {pid} ({win.name or win.app_id})")
        return
    try:
        if nice:
            win.command('kill')
        else:
            os.kill(pid, signal.SIGKILL)
    except Exception as e:
        print(f"Error killing process {pid}: {e}")

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Kill the window under the cursor on your focused Sway workspace."
    )
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose debug output")
    parser.add_argument('--pixel', dest='pixel', action='store_true', default=True,
                        help="Use single-pixel selection with slurp (default: enabled)")
    parser.add_argument('--no-pixel', dest='pixel', action='store_false',
                        help="Use rectangle selection with slurp")
    parser.add_argument('--dry-run', action='store_true', help="Show what would be killed, but do not kill")
    parser.add_argument('--nice', action='store_true', help="Politely ask the process to quit (SIGTERM instead of SIGKILL)")
    args = parser.parse_args()

    print("Click on a window to kill it (ESC to cancel)...")
    coords = get_click_coordinates(args.verbose, pixel=args.pixel)
    if not coords:
        return
    x, y = coords
    sway: Connection = i3ipc.Connection()
    tree: Con = sway.get_tree()
    workspace: Optional[Con] = get_focused_workspace(tree, args.verbose)
    if not workspace:
        print("Could not find the focused workspace.")
        return
    win: Optional[Con] = find_topmost_window_under_cursor(workspace, x, y, args.verbose)
    if win:
        print(f"{'[DRY-RUN] ' if args.dry_run else ''}{'Nicely ' if args.nice else ''}Killing window: {win.name or win.app_id}")
        kill_window(win, args.dry_run, args.verbose, args.nice)
    else:
        print("No window found under cursor in the focused workspace.")

if __name__ == '__main__':
    main()