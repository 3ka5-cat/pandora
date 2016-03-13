# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from tornado import gen
from tornado_json.exceptions import APIError
from tornado_json.gen import coroutine
from tornado_json.requesthandlers import APIHandler
from tornado_json import schema


class BoxesHandler(APIHandler):

    @schema.validate(
        output_schema={
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["id", "loc", "title", "address"],
                "properties": {
                    "id": {"type": "integer"},
                    "loc": {"type": "object"},
                    "address": {"type": "string"},
                    "title": {"type": "string"},
                }
            }
        },
        output_example={
            "id": 21379,
            "loc": {
                "type": "Point",
                "coordinates": [
                    29.88487365167069,
                    50.058326259638775
                ]
            },
            "address": "Fastov, Chelyuskintsev str, 98",
            "title": "Dubravushka-club",
        }
    )
    @coroutine
    def get(self):
        """ Returns list of nearest boxes. """
        # TODO: catch ValueError and raise proper 400 exception with data about error instead of 500
        lon = float(self.get_query_argument("lon"))
        lat = float(self.get_query_argument("lat"))
        distance = int(self.get_query_argument("distance", 5000))
        limit = int(self.get_query_argument("limit", 20))
        offset = int(self.get_query_argument("offset", 0))

        cursor = self.db_conn.places.find({
            "loc": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    },
                    "$maxDistance": distance
                }
            },
            "box": {"$exists": True}
        },
            {"_id": 0, "box": 0}).skip(offset).limit(limit)

        res = yield cursor.to_list(length=limit)

        raise gen.Return(res)


class BoxQuestionHandler(APIHandler):

    @schema.validate(
        output_schema={
            "type": "object",
            "additionalProperties": False,
            "required": ["id", "box"],
            "properties": {
                "id": {"type": "integer"},
                "box": {"type": "object"},
            },
        },
        output_example={
            "id": 5125,
            "box": {
                "question": "Who developed theory of relativity"
            },
        }
    )
    @coroutine
    def get(self, box_id):
        """ Returns question for box specified by id. """
        box_id = int(box_id)
        res = yield self.db_conn.places.find_one({"id": box_id,
                                                  "box": {"$exists": True}},
                                                 {"_id": 0, "id": 1, "box.question": 1})
        raise gen.Return(res)

    @schema.validate(
        input_schema={
            "type": "object",
            "properties": {
                "answer": {"type": "string"},
            }
        },
        input_example={
            "answer": "Albert Einstein",
        },
        output_schema={
            "type": "object",
            "additionalProperties": False,
            "required": ["opened"],
            "properties": {
                "opened": {"type": "boolean"},
                "oneOf": [
                    {"message": {"type": "string"}},
                    {"title": {"type": "string"}}
                ]
            }
        },
        output_example={
            "opened": False,
            "message": "Too late, box is gone"
        },
    )
    @coroutine
    def post(self, box_id):
        """ Tries to open box specified by id. """
        # TODO: move from int id to mongo id, resolve issue with json serialization
        box_id = int(box_id)
        answer = self.body["answer"]
        place = yield self.db_conn.places.find_one({"id": box_id,
                                                    "box": {"$exists": True}},
                                                   {"_id": 0, "id": 1, "box.answer": 1, "box.title": 1})
        if not place:
            # TODO: raise proper 404 exception with message about not found box
            raise APIError(404)
        elif place["box"]["answer"].lower() == answer.lower():
            title = place["box"]["title"]
            result = yield self.db_conn.places.update(
                {"id": place["id"], "box": {"$exists": True}},
                {"$unset": {"box": 1}}
            )
            if result["updatedExisting"]:
                res = {"opened": True, "title": title}
            else:
                res = {"opened": False, "message": "Too late, box is gone"}
        else:
            res = {"opened": False, "message": "Wrong answer"}

        raise gen.Return(res)
