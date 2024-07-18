from flask import Flask, request
from flask_restful import Resource, Api

# 读取当前目录下的文件以加载敏感配置
import os
import sys
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 获取环境变量设置配置文件
if 'CICDMETA_ENV' in os.environ:
    if os.environ['CICDMETA_ENV'] == 'prod':
        config_name = "config_prod.json"
    elif os.environ['CICDMETA_ENV'] == 'dev':
        config_name = "config_dev.json"
else:
    config_name = "config_dev.json"

with open(config_name, 'r') as f:
    config = json.load(f)
# 读取特定 section 的特定 key 的值
VERSION = config.get('version') or "no config"

app = Flask(__name__)
api = Api(app)

def lane_http_header(request):
    custom_header_kv = request.headers
    ret = {}
    for each_key in ['X-ENV','X-USER-ID', 'X-REQUEST-ID']:
        value = custom_header_kv.get(each_key)
        if value:
            ret[each_key] = value
    return ret

# Test资源
class ConfigResource(Resource):
    def get(self):
        values = VERSION
        custom_header_dict = lane_http_header(request)
        ret = {"version": values}
        ret['route_my_custom_header'] = custom_header_dict
        ret['my_all_headers_see_lane_inject'] = request.headers
        return ret

    def post(self):
        key = request.json['key']
        value = request.json['value']
        with open(config_name, 'r') as f:
            config = json.load(f)
        config[key] = value
        with open(config_name, 'w') as f:
            f.write(json.dumps(config))
        return {k: v for k, v in config.items()}


api.add_resource(ConfigResource, '/config')


if __name__ == '__main__':
    app.run(debug=True)
