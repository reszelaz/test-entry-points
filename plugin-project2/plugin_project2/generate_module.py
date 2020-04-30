import sys


def generate_modules(nb):
    for module_idx in range(1, nb):
        with open("plugin_module{}.py".format(module_idx), "w") as f:
            f.write("from project import BasePlugin")
            for class_idx in range(1, 101):
                f.write("\n\n\nclass Plugin2_{}_{}(BasePlugin):\n\n".format(module_idx, class_idx))
                f.write("    def run(self):\n")
                f.write("        print(\"In plugin_project2.plugin_module{0}.Plugin2_{0}_{1}\")".format(module_idx, class_idx))


if __name__ == "__main__":
    nb = sys.argv[1]
    generate_modules(nb)
