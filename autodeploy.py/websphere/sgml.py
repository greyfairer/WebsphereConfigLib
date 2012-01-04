import sgmllib

class DataParser(sgmllib.SGMLParser):
    def __init__(self, verbose=0):
        sgmllib.SGMLParser.__init__(self, verbose)
        self.data = None

    def handle_data(self, data):
        if len(data.strip()) > 0:
            if self.data is None:
                self.data = data
            else:
                self.data = self.data + " " + data


def extractSgmlData(lines):
    result = []
    p = DataParser()
    for line in lines:
        p.feed(line)
        if p.data is not None:
            result.append(p.data)
            p.data = None
    return result            



