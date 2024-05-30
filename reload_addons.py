import bpy
import os
import subprocess
import sys
from pathlib import Path
import shutil

# Not part of bpy API, but can still be used
import addon_utils

bl_info = {
    "name": "Reload Addons",
    "author": "JoeJoeTV, John Kanji",
    "description": "Adds the ability to update an in-development addon from a source directory and reload it without restarting blender",
    "version": (1, 1, 0),
    "blender": (4, 0, 0),
    "location": "SpaceBar Search -> Reload All Addons",
    "category": "Development",
    "support": "COMMUNITY",
}


def reload_addons(op, only_enabled=True):
    """Installs and reloads addons from source path set in the addon preferences
    
    Arguments:
        op: Addon operator used for outputting messages to Blender info panel
        [only_enabled]: Whether only enabled addons should be tried for reloading
    """

    preferences = bpy.context.preferences
    addon_prefs = preferences.addons[__name__].preferences
    user_addons_path = Path(addon_prefs.source_dir)

    if not user_addons_path.is_dir():
        op.report({'ERROR'}, f"The specified source directory path ({str(user_addons_path)}) is not a directory or doesn't exist!")
        return

    blender_addons_path = Path(bpy.utils.script_path_user())/'addons'

    # get list of all *user* installed addons and the enabled ones
    addons = [m.__name__ for m in addon_utils.modules() if (str(blender_addons_path) in m.__file__)]
    enabled_addons = [a.module for a in bpy.context.preferences.addons if a.module in addons]

    if only_enabled:
        addons = enabled_addons

    for a in addons:
        addon_path = None

        if (user_addons_path / f"{a}.py").is_file():
            addon_path = user_addons_path / f"{a}.py"
        elif (user_addons_path / a / "__init__.py").is_file():
            addon_path = user_addons_path / a
        else:
            # If there is no python module as a file or directory, we can't install/reload addon, so try next one
            op.report({'DEBUG'}, f"No source for addon '{a}' found in source path.")
            continue
        
        # Save preferences of addon, since they get reset when disabling and re-enabling
        addon_prefs = {}

        if bpy.context.preferences.addons[a].preferences:
            addon_prefs = dict(bpy.context.preferences.addons[a].preferences.items())

        op.report({'DEBUG'}, f"Copying source code for addon '{a}'...")

        try:
            if addon_path.is_file():
                shutil.copy2(addon_path, blender_addons_path / f"{a}.py")
            elif addon_path.is_dir():
                shutil.copytree(addon_path, blender_addons_path / a, dirs_exist_ok=True)
            else:
                op.report({'ERROR'}, f"Addon source is neither file not directory! How did you get here?")
        except (EnvironmentError, IOError) as e:
                op.report({'ERROR'}, f"Error while copying source code for addon '{a}'")
                continue

        op.report({'DEBUG'}, f"Reloading addon '{a}'...")

        bpy.ops.preferences.addon_refresh()

        if a in enabled_addons:
            status = bpy.ops.preferences.addon_disable(module=a)

            if 'FINISHED' not in status:
                op.report({'ERROR'}, f"Error while disabling addon '{a}'!")
                continue
        
        mods = []
        for mod_name, mod in sys.modules.items():
            if a in mod_name:
                mods.append(mod_name)
        for mod in mods:
            del sys.modules[mod]
        
        status = bpy.ops.preferences.addon_enable(module=a)

        if 'FINISHED' not in status:
            op.report({'ERROR'}, f"Error while enabling addon '{a}'!")
            continue
        
        # Restore preferences
        if addon_prefs:
            for p, v in addon_prefs.items():
                bpy.context.preferences.addons[a].preferences[p] = v

        op.report({'INFO'}, f"Updated and reloaded addon '{a}'.")


class ReloadEnabledAddons(bpy.types.Operator):
    """Reload Addons"""
    bl_idname = "reload_addons.enabled"
    bl_label = "Reload Enabled Addons"

    def execute(self, context):
        reload_addons(op=self)
        return {'FINISHED'}


class LoadAddons(bpy.types.Operator):
    """Reload Addons"""
    bl_idname = "reload_addons.load"
    bl_label = "Reload All Addons"

    def execute(self, context):
        reload_addons(only_enabled=False, op=self)
        return {'FINISHED'}


class ReloadAddonsPrefs(bpy.types.AddonPreferences):
    bl_idname = __name__
    source_dir: bpy.props.StringProperty(
        name="Source Directory",
        description="The directory containing the source of the addons to reload as python files or directories containing each a python module for the addon",
        subtype="DIR_PATH",
        default=str(Path.home()/'src'/'Blender')
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Choose the directory to be scanned for addons.")
        layout.prop(self, "source_dir")


def draw_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(ReloadEnabledAddons.bl_idname, text=ReloadEnabledAddons.bl_label)
    layout.operator(LoadAddons.bl_idname, text=LoadAddons.bl_label)

def register():
    bpy.utils.register_class(ReloadEnabledAddons)
    bpy.utils.register_class(LoadAddons)
    bpy.utils.register_class(ReloadAddonsPrefs)
    bpy.types.TOPBAR_MT_blender_system.append(draw_menu)


def unregister():
    bpy.utils.unregister_class(ReloadEnabledAddons)
    bpy.utils.unregister_class(LoadAddons)
    bpy.utils.unregister_class(ReloadAddonsPrefs)
    bpy.types.TOPBAR_MT_blender_system.remove(draw_menu)


if __name__ == "__main__":
    script_path = Path(__file__)
    bpy.ops.preferences.addon_install(filepath=str(script_path))
    print(f'Installed reload_addons addon for Blender')
