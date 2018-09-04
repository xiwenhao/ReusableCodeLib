from flask import Flask, request, make_response
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import json, os
from functools import wraps

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'




app.route("/stop", methods=["GET"])
def stop_service():
    print "try exit"

    os.kill(os.getpid(), 9)


schema = {
    "type": "object",
    "required": ["id", "vm"],
    "properties": {
        "id": {"type": "string"},
        "vm": {"type": "string", "pattern": "^instance-([A-Za-z0-9]{1,})$"}
    }
}

# def test_wrap(func):
#     def wrap(*args, **kwargs):
#         print "in wrap", request.data
#         # return func(*args, **kwargs)
#         return make_response("error")
#     return wrap


def check_json(func):
    # @wraps(func)
    def wrapper(*args, **kwargs):
        data = request.get_json()
        if request.path == "/test":
            # 区分路由验证不同的json
            print "view /test"
        try:
            validate(data, schema)
            print "pass json check"
            return func(*args, **kwargs)
        except ValidationError as e:
            print "deny, undesirable json"
            # 装饰器返回响应 不会再执行正常的处理函数
            return make_response("error json")
    return wrapper


@app.route("/test", methods=["POST"], endpoint="test")
@check_json
def tes():
    t = request.get_json()
    print type(t)
    print "t111111111111", t
    return make_response("ok")



if __name__ == '__main__':
    app.run()
