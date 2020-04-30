import sys
import inspect
import pkgutil
import importlib
import setuptools


def is_plugin(obj):
    if (inspect.isclass(obj)
            and issubclass(obj, BasePlugin)
            and obj is not BasePlugin):
        return True
    return False


def find_plugins_ep(pkgs=None):
    if pkgs is None:
        pkgs = setuptools.find_packages()
    modules = set()
    for pkg in pkgs:
        modules.add(pkg)
        pkg_path = pkg.replace(".", "/")
        for _, name, is_pkg in pkgutil.iter_modules([pkg_path]):
            if not is_pkg:
                modules.add(pkg + '.' + name)
    plugins_ep = []
    for module in modules:
        for ep in iter_module_ep(module):
            plugins_ep.append(ep)
    return plugins_ep


def iter_module_ep(module):
    module_obj = importlib.import_module(module)
    plugins = inspect.getmembers(module_obj, is_plugin)
    for plugin_name, plugin in plugins:
        yield "{0} = {1.__module__}:{0}".format(plugin_name, plugin)


class BasePlugin:
    pass


class Plugin1_1(BasePlugin):

    def run(self):
        print("In project.Plugin1_1")


def list_():
    from .plugins import list_
    list_()


def run(plugin):
    from .plugins import run
    run(plugin)


def discover():
    from .plugins import discover
    discover()


def add_dist(dist_name):
    from .plugins import add_dist
    try:
        add_dist(dist_name)
    except ValueError as e:
        print("ERROR: ", e)


def add_module(dist_name, module_name):
    from .plugins import add_module
    try:
        add_module(dist_name, module_name)
    except ValueError as e:
        print("ERROR: ", e)


def reload_module(module):
    from .plugins import reload_module
    try:
        reload_module(module)
    except ValueError as e:
        print("ERROR: ", e)


def reload_plugin(plugin):
    from .plugins import reload_plugin
    try:
        reload_plugin(plugin)
    except ValueError as e:
        print("ERROR: ", e)


def help():
    print("Available commands:")
    print(" list (l) - list available plugins")
    print(" run <plugin> (r <plugin>) - run a plugin")
    print(" discover (d)- discover plugins"
          " (necessary after: adddist, addmod, relmod)")
    print(" adddist <distribution> - add distribution"
          " (necessary after installation)")
    print(" addmod <distribution> <module> - add module to a distribution")
    print(" relmod <module> (rmod <module>) - reload a module")
    print(" relplug <module> (rplug <plugin>) - reload a plugin")
    print(" quit (q) - quit the program")


def main():
    while True:
        text = input("Type a command (or '?' to get help): ")
        text = text.strip()
        tokens = text.split()
        if len(tokens) == 0:
            continue
        cmd = tokens[0]
        if cmd == "?":
            help()
        elif cmd in ("list", "l"):
            list_()
        elif cmd in ("run", "r"):
            try:
                plugin = tokens[1]
            except IndexError:
                print("Missing argument, type '?' to get help")
                continue
            run(plugin)
        elif cmd in ("discover", "d"):
            discover()
        elif cmd in ("adddist"):
            try:
                dist = tokens[1]
            except IndexError:
                print("Missing argument, type '?' to get help")
                continue
            add_dist(dist)
        elif cmd in ("addmodule", "addmod"):
            try:
                dist = tokens[1]
                module = tokens[2]
            except IndexError:
                print("Missing argument, type '?' to get help")
                continue
            add_module(dist, module)
        elif cmd in ("relmodule", "relmod", "rmod"):
            try:
                module = tokens[1]
            except IndexError:
                print("Missing argument, type '?' to get help")
                continue
            reload_module(module)
        elif cmd in ("relplugin", "relplug", "rplug"):
            try:
                plugin = tokens[1]
            except IndexError:
                print("Missing argument, type '?' to get help")
                continue
            reload_plugin(plugin)
        elif cmd in ("quit", "q"):
            sys.exit()
        else:
            print("Unrecognized command, type '?' to get help")
        print()


if __name__ == '__main__':
    main()
