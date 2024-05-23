from flask import Flask, render_template, request, jsonify, send_from_directory
import subprocess
import os
import time
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    emails = request.form['emails']
    job_id = subprocess.check_output(['uuidgen']).decode('utf-8').strip()  # Gerando um job_id aleatório
    subprocess.Popen(['python3.6', 'webscraping_ligacoes.py', job_id, emails])
    save_job_id(job_id)  # Salvando o job ID
    socketio.emit('update_job_ids', {'job_ids': read_job_ids()})
    return f"Job ID {job_id} iniciado para os e-mails: {emails}"

@app.route('/job_ids')
def get_job_ids():
    job_ids = read_job_ids()
    job_data = []
    for job_id in job_ids:
        log_file_path = f'saves/{job_id}.txt'
        if os.path.exists(log_file_path):
            created_at = time.ctime(os.path.getctime(log_file_path))
            job_data.append({'job_id': job_id, 'created_at': created_at})
        else:
            job_data.append({'job_id': job_id, 'created_at': '🕖'})
    return jsonify({'job_ids': job_data})


@app.route('/latest_log')
def get_latest_log():
    return jsonify({'log_content': 'Nenhum log disponível.'})

@app.route('/log/<job_id>')
def get_log_by_job_id(job_id):
    log_file = f"{job_id}_log_{time.strftime('%Y-%m-%d')}.log"
    log_path = os.path.join(os.path.dirname(__file__), 'logs', log_file)
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            log_content = f.read()
        return jsonify({'log_content': log_content})
    else:
        return jsonify({'log_content': 'Log file not found'})

@app.route('/download/<job_id>')
def download_file(job_id):
    directory = os.path.join(os.path.dirname(__file__), 'saves')
    filename = f"{job_id}.txt"
    return send_from_directory(directory, filename, as_attachment=True)

@socketio.on('join_job')
def on_join(data):
    job_id = data['job_id']
    join_room(job_id)
    emit_log_for_job(job_id)

@socketio.on('leave_job')
def on_leave(data):
    job_id = data['job_id']
    leave_room(job_id)

def save_job_id(job_id):
    with open('jobids.txt', 'a') as f:
        f.write(job_id + '\n')

def read_job_ids():
    if os.path.exists('jobids.txt'):
        with open('jobids.txt', 'r') as f:
            return f.read().splitlines()
    else:
        return []

def emit_log_for_job(job_id):
    log_file = f"{job_id}_log_{time.strftime('%Y-%m-%d')}.log"
    log_path = os.path.join(os.path.dirname(__file__), 'logs', log_file)
    while True:
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                log_content = f.read()
            socketio.emit('update_log', {'log_content': log_content}, room=job_id)
        socketio.sleep(1)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)