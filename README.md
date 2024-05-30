# Blender Addon Reload Addon

An addon for [Blender](https://blender.org) that allows reloading addons while developing them without having to restart Blender.

## Installation

It is recommended to use the provided Reloader addon to install and reload development addons. The Reloader addon can be installed by executing `reload_addons.py` file under Blender's python interpreter:

```sh
blender -b -P reload_addons.py
```

## Usage

This addon provides two commands, "Reload All Addons" and "Reload Enabled Addons" which can be accessed from the Blender menu in the topbar under System, or through the tool search bar. This will search the user addons directory (default `~/src/Blender`, configurable in Preferences -> Addons -> Reload Addons) for addon sources, install them and reload them in Blender's interpreter.