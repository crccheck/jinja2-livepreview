import json

import aiohttp_jinja2
import ansible
import jinja2
import yaml
from aiohttp import web
from ansible.plugins.filter import core, ipaddr, mathstuff
from jinja2 import Environment
from jinja2.exceptions import TemplateError
from project_runpy import env


@aiohttp_jinja2.template('index.html')
async def index(request):
    return {
        'ansible_version': ansible.__version__,
        'jinja2_version': jinja2.__version__,
    }


class WebSocketHandler(web.View):
    context = {}
    j2_env = Environment()
    j2_template = ''
    _content_type = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.j2_env.filters = {
          # XXX this syntax breaks coverage line reporting
          **mathstuff.FilterModule().filters(),
          **ipaddr.FilterModule().filters(),
          **core.FilterModule().filters(),
        }

    @property
    def context_type(self):
        return self._content_type

    @context_type.setter
    def context_type(self, value):
        if value == self._content_type:
            return

        self._content_type = value
        self.send({'context_type': value})

    def send(self, data):
        self.ws.send_str(json.dumps(data))

    def process_context(self, context_str):
        if not context_str:
            self.context = {}
            self.context_type = None
            return

        if context_str.startswith('{'):
            self.context_type = 'json'
            try:
                self.context = json.loads(context_str)
            except Exception as e:
                self.send({
                    'error': '{}: {}'.format(e.__class__.__name__, e),
                    'state': 'error-context-json',
                })
        else:
            self.context_type = 'yaml'
            try:
                self.context = yaml.safe_load(context_str)
            except Exception as e:
                self.send({
                    'error': '{}: {}'.format(e.__class__.__name__, e),
                    'state': 'error-context-yaml',
                })

        if not isinstance(self.context, dict):
            self.context = {}
            self.send({
                'error': 'Context is not a hash',
                'state': 'error-context',
            })

    def render_to_user(self):
        try:
            out = self.j2_env.from_string(self.j2_template).render(**self.context)
        except TemplateError as e:
            self.send({
                'error': 'Invalid jinja2 {}'.format(e),
                'state': 'error-jinja2',
            })
        else:
            self.send({'render': out})

    async def get(self):
        ws = web.WebSocketResponse()
        await ws.prepare(self.request)
        self.ws = ws

        async for msg in ws:
            try:
                in_data = json.loads(msg.data)
            except TypeError as e:
                self.send({'error': 'Invalid message {}'.format(e)})

            if 'context' in in_data:
                self.process_context(in_data['context'].strip())

            if 'jinja2' in in_data:
                self.j2_template = in_data['jinja2']

            self.render_to_user()
        return ws


if __name__ == '__main__':
    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('public'))

    app.router.add_route('GET', '/', index)  # TODO try and see if add_static will work
    app.router.add_route('GET', '/ws', WebSocketHandler)
    app.router.add_static('/static', 'assets')

    web.run_app(
        app,
        port=env.get('PORT', 8080),
    )
