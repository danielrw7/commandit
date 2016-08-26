import json, os.path

def json_load(filepath):
    return json.load(open(filepath))

def valid_filenames(filenames):
    return map(os.path.realpath, filter(os.path.exists, filenames))

def merge(res, *dicts):
    for source in dicts:
        for key, value in source.iteritems():
            if isinstance(value, dict):
                value = merge(res.setdefault(key, {}), value)
            res[key] = value

    return res

class JSONConfig:
    def __init__(self, filenames=[], allowDotNotation=False):
        self.filenames = filenames
        self.allowDotNotation = allowDotNotation
        self.reload()

    def set_config_list(self):
        self.config_list = []
        for filename in self.valid_filenames:
            try:
                self.config_list.append(self.file_contents[filename])
            except:
                pass

    def set_config_merged(self):
        self.config = merge({}, *self.config_list)

    def load_files(self, filenames=[]):
        map(self.load_file, filenames)

    def load_file(self, filename):
        try:
            self.file_contents[filename] = json_load(filename)
        except:
            pass

    def reload(self):
        self.valid_filenames = valid_filenames(self.filenames)
        self.file_contents = {}
        self.load_files(self.valid_filenames)
        self.set_config_list()
        self.set_config_merged()

    def get(self, key):
        if not isinstance(key, str):
            raise TypeError("Invalid parameter type for `key`")
        try:
            value = self.config
            if self.allowDotNotation:
                for part in key.split("."):
                    value = value[part]
            else:
                value = value[key]
            return value
        except:
            pass
