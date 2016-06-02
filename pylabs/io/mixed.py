import json, pandas, datetime, dateutil.parser


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'to_json'):
            return obj.to_json(orient='records')
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def listOfDictsToJson(data, fpath):
    with open(fpath, 'w') as fp:
        json.dump(data, fp, cls=JSONEncoder)

def listOfDictsFromJson(fpath):
    toplevel = json.load(open(fpath))
    assert isinstance(toplevel, list)
    outlist = []
    for item in toplevel:
        item['data'] = pandas.read_json(item['data'])
        item['date'] = dateutil.parser.parse(item['date']).date()
        outlist.append(item)
    return outlist
