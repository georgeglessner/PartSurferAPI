import requests
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from collections import defaultdict
from flask import Flask, request
from flask_restful import Resource, Api, abort, reqparse

app = Flask(__name__)
api = Api(app)


class Parts(Resource):
    def get(self, name):
        # Grab the page
        response = requests.get(
            "https://partsurfer.hpe.com/Search.aspx?searchText={}".format(name)
        )

        # Find component BOMS
        selection = (
            Selector(response=response)
            .xpath(
                "//table//tr[contains(@class, 'RowStyle')]//span[contains(@id, 'ctl00_BodyContentPlaceHolder_gridCOMBOM')]//text()"
            )
            .getall()
        )

        # Initialize dictionary and variables
        results = defaultdict(list)
        index = 0
        hpid = 0

        # Only grab part and description
        for entry in selection:
            if index == 0:
                results[hpid].append({"Part": entry})
            if index == 1:
                results[hpid].append({"Description": entry})
            if index == 2:
                hpid += 1
                index = -1
            index += 1

        return {"results": results}


# File paths and params
api.add_resource(Parts, "/hpe/part/<string:name>")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
