import json

class PropertyFile:

    def __init__(self, ostream):
        self.properties = []
        self.file = ostream
        for i in ostream.readlines():
            if i.startswith("#"):
                pass
            else:
                d = i.strip().split("=")
                if d[1] == '':
                    self.properties.append(PropertyItem(d[0], None))
                elif d[1].isnumeric():
                    self.properties.append(PropertyItem(d[0], int(d[1])))
                elif d[1] == 'true':
                    self.properties.append(PropertyItem(d[0], True))
                elif d[1] == 'false':
                    self.properties.append(PropertyItem(d[0], False))
                else:
                    self.properties.append(PropertyItem(d[0], d[1]))

    def __repr__(self):
        d = []
        for i in self.properties:
            d.append(f"{i.key}={i.value}")
        if len(d) > 16:
            for i in range(len(d) - 6):
                d.pop(3)
            d.insert(3, "...")
        return "PropertyFile(" + ", ".join(d) + ")"

    def put(self, key, value):
        for i in self.properties:
            if i.key == key:
                i.value = value
                break
        else:
            self.properties.append(PropertyItem(key, value))

    def save(self):
        f = open(self.file.name, "w")
        for i in self.properties:
            if isinstance(i.value, str):
                f.write(i.key + "=" + i.value)
            elif i.value == None:
                f.write(i.key + "=")
            else:
                f.write(i.key + "=" + json.dumps(i.value))
            f.write("\n")
        f.close()
        self.file.close()

    def close(self):
        self.file.close()
        
class PropertyItem:

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __repr__(self):
        return f"PropertyItem({self.key}, {self.value}: {self.value.__class__.__name__})"

class PropertyComment:
    pass
