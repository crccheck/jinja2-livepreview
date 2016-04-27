from unittest import TestCase, mock

from web import WebSocketHandler


class WebSocketHandlerTests(TestCase):
    def setUp(self):
        super().setUp()
        self.request = mock.Mock()
        self.view = WebSocketHandler(self.request)
        self.view.ws = mock.Mock()

    def test_send_sends_json(self):
        self.view.send({'foo': 'bar'})
        self.view.ws.send_str.assert_called_once_with('{"foo": "bar"}')

    def test_process_context_deals_with_null(self):
        self.view.process_context('')

        self.assertEqual(self.view.context, {})
        self.assertEqual(self.view.context_type, None)

    def test_process_context_deals_with_json(self):
        self.view.process_context('{}')

        self.assertEqual(self.view.context, {})
        self.assertEqual(self.view.context_type, 'json')

    def test_process_context_deals_with_bad_json(self):
        self.view.process_context('{foo}')

        self.assertEqual(self.view.context, {})
        self.assertEqual(self.view.context_type, 'json')
        self.assertIn('error-context-json', self.view.ws.send_str.call_args[0][0])

    def test_process_context_deals_with_yaml(self):
        self.view.process_context('foo: bar')

        self.assertEqual(self.view.context, {'foo': 'bar'})
        self.assertEqual(self.view.context_type, 'yaml')

    def test_process_context_deals_with_bad_yaml(self):
        self.view.process_context(':')

        self.assertEqual(self.view.context, {})
        self.assertEqual(self.view.context_type, 'yaml')
        self.assertIn('error-context-yaml', self.view.ws.send_str.call_args[0][0])

    def test_process_context_deals_with_yaml_not_hash(self):
        self.view.process_context('- foo\n- bar')

        self.assertEqual(self.view.context, {})
        self.assertEqual(self.view.context_type, 'yaml')
        self.assertIn('Context is not a hash', self.view.ws.send_str.call_args[0][0])

    def test_render_to_user_works_with_defaults(self):
        self.view.render_to_user()
        self.view.ws.send_str.assert_called_once_with('{"render": ""}')

    def test_render_to_user_renders(self):
        self.view.jinja2 = '{{ foo }}'
        self.view.context = {'foo': 'bar'}

        self.view.render_to_user()
        self.view.ws.send_str.assert_called_once_with('{"render": "bar"}')

    def test_render_to_user_handles_bad_template(self):
        self.view.jinja2 = '{{ foo }'

        self.view.render_to_user()
        self.assertIn('error-jinja2', self.view.ws.send_str.call_args[0][0])
