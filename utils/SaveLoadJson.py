import json

class SaveLoadJson:
    def __init__(self):
        try:
            with open('../utils/jsonFile.json', 'r') as f:
                self.dict = json.load(f)
        except FileNotFoundError:
            self.dict = {}
            with open('../utils/jsonFile.json', 'w') as f:
                json.dump(self.dict, f)

    def setKey(self, key, value):
        self.dict[key] = value
        with open('../utils/jsonFile.json', 'w') as f:
            json.dump(self.dict, f)

    def getKey(self, key):
        if key in self.dict:
            return self.dict[key]
        else:
            return None

if __name__ == "__main__":
    slJson = SaveLoadJson()
    slJson.setKey("money", 1234)
    print(slJson.getKey("money"))
    print(slJson.dict)