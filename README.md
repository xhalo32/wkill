# `wkill` -- Sway kill window

Works like `xkill`: sends SIGKILL to selected window.

See `wkill --help` for options.

## Installation

1. Add this repository as a dependency to your [npins](https://github.com/andir/npins)-based NixOS system:

    ```sh
    npins add github xhalo32 wkill --branch main
    ```

    > Flake support might be added once flakes are stable.

1. Add the following overlay to your pkgs:
    
    ```nix
    (final: prev: {
        wkill = (import sources.wkill { pkgs = prev; }).packages.wkill;
    })
    ```

    > Passing `pkgs = prev` introduces dependency injection meaning that `wkill` will use the dependency versions from your nixpkgs.
    > If there are breaking changes in the dependencies, drop the dependency injection to use an older nixpkgs that works.

1. In your home-manager configuration, add:

    ```nix
    "${mod}+k" = "exec ${pkgs.wkill}/bin/wkill";
    ```

    under `wayland.windowManager.sway.keybindings`.

1. Rebuild your configuration, reload sway and try it out!

## Alternatives

If you don't want to use `wkill`, you can try these alternatives:

- To simply kill the currently focused window, you can use

    ```sh
    kill -9 $(swaymsg -t get_tree | jq '.. | select(.focused? == true) | .pid')
    ```

    Bind that to your preferred key, e.g. in `~/.config/sway/config` add

    ```
    bindsym Mod4+Ctrl+Shift+q exec kill -9 $(swaymsg -t get_tree | jq '.. | select(.focused? == true) | .pid')
    ```
