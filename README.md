# Blender Addon Reload Addon

An addon for [Blender](https://blender.org) that allows reloading addons while developing them without having to restart Blender.

## Installation

The Reloader addon can be installed by installing the `reload_addons.py` file or the ZIP file found under Releases using the Blender GUI or executing `reload_addons.py` file under Blender's python interpreter:

```sh
blender -b -P reload_addons.py
```

## Usage

The addon can be used with the two commands it provides, "Reload All Addons" and "Reload Enabled Addons" which can be accessed from the Blender menu in the topbar under System, or through the tool search bar. This will search the user addons directory (default `~/src/Blender`, configurable in Preferences -> Addons -> Reload Addons) for addon sources (python modules), install them and reload them in Blender's interpreter.