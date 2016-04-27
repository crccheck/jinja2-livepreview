import $ from 'jquery'

function log (message) {
  const container = $('#log')[0]
  $('<p/>').text(message).appendTo(container)
  container.scrollTop = container.scrollHeight
}

// Input editors

const jinja2Editor = window.ace.edit('jinja2')
const contextEditor = window.ace.edit('context')
contextEditor.getSession().setMode('ace/mode/yaml')

$('#jinja2').on('keyup', (e) => {
  sock.send(JSON.stringify({jinja2: jinja2Editor.getValue()}))
})

$('#context').on('keyup', (e) => {
  sock.send(JSON.stringify({context: contextEditor.getValue()}))
})

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
