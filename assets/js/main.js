import $ from 'jquery'
import _ from 'lodash'

function log (message) {
  const container = $('#log')[0]
  $('<p/>').text(message).appendTo(container)
  container.scrollTop = container.scrollHeight
}

// Input editors

const jinja2Editor = window.ace.edit('jinja2')
const contextEditor = window.ace.edit('context')
contextEditor.getSession().setMode('ace/mode/yaml')

// TODO don't send unless value changed

$('#jinja2').on('keyup', _.debounce((e) => {
  sock.send(JSON.stringify({jinja2: jinja2Editor.getValue()}))
}, 200))

$('#context')
.on('keyup', _.debounce((e) => {
  sock.send(JSON.stringify({context: contextEditor.getValue()}))
}, 200))
// Keep navbar pills from being clickable, I just want the styling
.prev().find('a').on('click', false)

// WebSocket

var sock
try {
  sock = new window.WebSocket('ws://' + window.location.host + '/ws')
} catch (err) {
  sock = new window.WebSocket('wss://' + window.location.host + '/ws')
}

sock.onopen = function () {
  log('Connection to server started')
  $('#context, #jinja2').keyup()
}

sock.onmessage = function (event) {
  try {
    const data = JSON.parse(event.data)
    if ('error' in data) {
      log(data.error)
    } else if ('render' in data) {
      $('#output').text(data.render)
    } else if ('context_type' in data) {
      if (data.context_type === 'json') {
        $('#context-json').attr('class', 'active')
        $('#context-yaml').attr('class', 'disabled')
      } else if (data.context_type === 'yaml') {
        $('#context-json').attr('class', 'disabled')
        $('#context-yaml').attr('class', 'active')
      } else {
        $('#context-json').attr('class', 'disabled')
        $('#context-yaml').attr('class', 'disabled')
      }
    } else {
      log(event.data)
    }
  } catch (e) {
    log(event.data)
  }
}

sock.onclose = function (event) {
  if (event.wasClean) {
    log('Clean connection end')
  } else {
    log('Connection broken')
  }
}

sock.onerror = function (error) {
  log(error)
}
