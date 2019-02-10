import configparser

config = configparser.ConfigParser(allow_no_value=True)
config.read("printer.ini")

not_print = config.get("DEFAULT", "notPrint").split("\n")


class Printer(object):
    """docstring for Printer."""

    def __init__(self):
        super(Printer, self).__init__()

    def prnt(self, name, node, other=None):
        if name not in not_print:
            print("{} {}".format(name, [*node]))
            print("{} len {}".format(name, len(node)))
            if other:
                [print("{} {}").format(name, val) for val in other]
