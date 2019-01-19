import os, traceback, shutil, time,argparse, configparser

G_to_rem = []
clear_whites = False
ugl = "\n"

### Args
arg_parser = argparse.ArgumentParser("create_build_lua")
arg_parser.add_argument("-ugl","--ugglify", help="Replaces new lines with spaces", action="store_true")
arg_parser.add_argument("-clW", "--clearWhites", help="Removes excess whitespaces", action="store_true")
arg_parser.add_argument("-remG", "--removeGlobals", help="Removes defined globals, needs a file", action="store")
arg_parser.add_argument("-uC", "--useConfig", help="Use configuration file, needs a file", action="store")
arg_parser.add_argument("-svC", "--saveConfig", help="Save current params to config file", action="store")

### Config
config = configparser.ConfigParser(allow_no_value=True)

# Custom class to handle file reading
class FileHandler():
  def __init__(self, file, mode):
    self.name = file
    self.mode = mode

  def __enter__(self):
    self.file = open(self.name, self.mode)
    return self.file

  def __exit__(self, type, value, traceback):
    if value:
      traceback.print_tb(traceback)
    self.file.close()


def start_main(build_folder = "build"):
  build_folder = "/{}/".format(build_folder)
  CWD = os.getcwd()
  build_folder = os.path.realpath(CWD + build_folder)
  if not os.path.isdir(build_folder):
    os.mkdir(build_folder)
  else:
    shutil.rmtree(build_folder)
    time.sleep(2)
    os.mkdir(build_folder)
  for (dirpath, dirnames, filenames) in os.walk(CWD):
    for filename in filenames:
      curr_path = os.path.basename(dirpath)
      if dirpath != build_folder:
        if filename.endswith('.lua'):
          new_cwd = os.getcwd()
          print(dirpath)
          handle = FileHandler(os.path.join(dirpath, filename), "r")
          final_str = ""
          with handle as h:
            line = h.readline()
            final_str = final_str + check_and_return_line(line)
            while line:
              line = h.readline()
              final_str = final_str + check_and_return_line(line)
          if dirpath != CWD:
            final_path = os.path.join(build_folder, curr_path)
          else:
            final_path = build_folder
          if not os.path.isdir(final_path):
            os.mkdir(final_path)
          handle = FileHandler(final_path + "\\" + filename, "w")
          with handle as h:
            h.write(final_str)


def check_and_return_line(line):
  clr_line = None
  if clear_whites:
    clr_line = " ".join(line.split())
  else:
    clr_line = line.strip()
  if clr_line != "":
    #line_strt = clr_line.split()[0]
    for L_global in G_to_rem:
      if clr_line.startswith(L_global):
        if "{" in clr_line:
          print("Cant handle tables")
          return clr_line + ugl
        return ""
    if clr_line.startswith("--[[") and not clr_line.startswith("--"):
      print("cant handle block comments")
      return clr_line + ugl
    elif clr_line.startswith("--") and not clr_line.startswith("--[["):
      return ""
    else:
      to_index = None
      words = clr_line.split()
      for word in words:
        if word.strip() == "--":
          to_index = words.index(word)
      if to_index:
        words = words[:to_index]
        clr_line = " ".join(words)
        return clr_line + ugl
      else:
        return clr_line + ugl
  else:
    return ""

def check_and_set_args(args):
  if args.useConfig:
    if os.path.isfile(args.useConfig):
      config.read(args.useConfig)
      if config["DEFAULT"]["clearWhites"]:
        clear_whites = True
      if config["DEFAULT"]["removeGlobals"]:
        G_to_rem = config.get("DEFAULT", "toRem").split("\n")
      if config["DEFAULT"]["ugglify"]:
        ugl = " "
    else:
      raise FileNotFoundError
  if args.ugglify:
    ugl = " "
  if args.clearWhites:
    clear_whites = True
  if args.removeGlobals:
    if os.path.isfile(args.removeGlobals):
      conf = FileHandler(args.removeGlobals, "r")
      with conf as c:
        vals = c.read()
        G_to_rem = [val for val in vals.split()]
    else:
      raise FileNotFoundError
  if args.saveConfig:
    config["DEFAULT"] = {
      "clearWhites": clear_whites,
      "removeGlobals": args.removeGlobals,
      "uggliffy": args.ugglify,
      "toRem": G_to_rem
    }
    conf_file = FileHandler(args.saveConfig, "w")
    with conf_file as c:
      config.write(c)


if __name__ == "__main__":
  args = arg_parser.parse_args()
  check_and_set_args(args)
  
  #start_main()