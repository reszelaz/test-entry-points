import sys
import inspect
import importlib
import configparser
import pkg_resources

from project import is_plugin


class CaseSensitiveConfigParser(configparser.ConfigParser):
    optionxform = staticmethod(str)


discovered_plugins = {}
overridden_plugins = []
module_dist_map = {}
module_ep_map = {}

ws = pkg_resources.WorkingSet()


def discover():
    global discovered_plugins
    global overridden_plugins
    global module_dist_map
    global module_ep_map
    discovered_plugins = {}
    discovered_eps = {}
    overridden_plugins = []
    module_dist_map = {}
    module_ep_map = {}

    for ep in ws.iter_entry_points("project.plugins"):
        discovered_ep = discovered_eps.get(ep.name)
        if discovered_ep is not None:
            if ep.dist.project_name == "Project":
                overridden_plugins.append(ep.name)
                continue
            elif discovered_ep.dist.project_name == "project":
                overridden_plugins.append(ep.name)
            else:
                print("WARNING: two distributions provide {}".format(ep.name))
        try:
            ep_cls = ep.load()
        except ImportError as e:
            print("ERROR: ", e)
            continue
        except SyntaxError as e:
            print("SYNTAX ERROR in {0.module_name} "
                  "({0.dist.project_name})".format(ep))
            continue
        discovered_plugins[ep.name] = ep_cls
        discovered_eps[ep.name] = ep
        module_dist_map[ep.module_name] = ep.dist
        module_ep_map[ep.module_name] = ep

        # module = sys.modules.get(ep.module_name)
        # if module:
        #     importlib.reload(module)


def list_():
    for name, plugin in discovered_plugins.items():
        overridden = False
        if name in overridden_plugins:
            overridden = True
        print(name, plugin, overridden)


def run(plugin_name):
    try:
        plugin_cls = discovered_plugins[plugin_name]
    except KeyError:
        raise ValueError("{} is not a plugin".format(plugin_name))
    plugin_cls().run()


def add_dist(dist_name):
    try:
        dist = pkg_resources.get_distribution(dist_name)
    except pkg_resources.DistributionNotFound:
        raise ValueError("{} distribution not found".format(dist_name))
    global ws
    ws = pkg_resources.WorkingSet()
    ws.add(dist)


def _update_ep_file(dist, module_name, added_plugins, removed_plugins=None):
    if removed_plugins is None:
        removed_plugins = []
    config = CaseSensitiveConfigParser()
    sanitized_project_name = dist.project_name.replace("-", "_")
    # TODO: consider dist-info (wheels)
    ep_file = "{}/{}.egg-info/entry_points.txt".format(dist.location,
                                                       sanitized_project_name)
    config.read(ep_file)
    ep_config_map = config["project.plugins"]
    for plugin_name in removed_plugins:
        ep_config_map.pop(plugin_name)
    for plugin_name in added_plugins:
        ep_config_map[plugin_name] = "{}:{}".format(module_name, plugin_name)
    with open(ep_file, 'w') as configfile:
        config.write(configfile)


def add_module(dist_name, module_name):
    try:
        dist = pkg_resources.get_distribution(dist_name)
    except pkg_resources.DistributionNotFound:
        raise ValueError("{} distribution not found".format(dist_name))
    try:
        module = importlib.import_module(module_name)
    except ImportError as e:
        print("ERROR: ", e)
        return
    except SyntaxError:
        print("SYNTAX ERROR in {} ({})".format(module_name, dist))
        return
    added_plugins = _get_plugins(module)
    _update_ep_file(dist, module_name, added_plugins)
    if added_plugins:
        global ws
        ws = pkg_resources.WorkingSet()


def _get_plugins(module):
    plugin_names = set()
    for plugin_name, plugin in inspect.getmembers(module, is_plugin):
        plugin_names.add(plugin_name)
    return plugin_names


def reload_module(module_name):
    if module_name not in module_ep_map:
        raise ValueError("{} is not a plugin module".format(module_name))
    module = sys.modules.get(module_name)
    dist = module_dist_map[module_name]
    if module:
        old_plugins = _get_plugins(module)
        # remove module attrs just in case plugin classes were removed
        for attr in dir(module):
            if attr not in ('__name__', '__file__'):
                delattr(module, attr)
        try:
            module = importlib.reload(module)
        except ImportError as e:
            print("ERROR: ", e)
            return
        except SyntaxError:
            print("SYNTAX ERROR in {} ({})".format(module_name, dist))
            return
    new_plugins = _get_plugins(module)
    removed_plugins = old_plugins - new_plugins
    added_plugins = new_plugins - old_plugins
    _update_ep_file(dist, module_name, added_plugins, removed_plugins)
    if removed_plugins or added_plugins:
        global ws
        ws = pkg_resources.WorkingSet()


def reload_plugin(plugin_name):
    plugin = discovered_plugins.get(plugin_name)
    if plugin is None:
        raise ValueError("{} is not a plugin".format(plugin_name))
    module_name = plugin.__module__
    dist = module_dist_map[module_name]
    module = sys.modules.get(module_name)
    try:
        module = importlib.reload(module)
    except ImportError as e:
        print("ERROR: ", e)
        return
    except SyntaxError:
        print("SYNTAX ERROR in {} ({})".format(module_name, dist))
        return
    discovered_plugins[plugin_name] = getattr(module, plugin_name)
