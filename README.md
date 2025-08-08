# `wkill` -- Sway kill window

Works like `xkill`: sends SIGKILL to selected window.

See `wkill --help` for options.

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
