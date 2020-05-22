from flask import Flask, request, render_template, url_for
import optparse
import os

from FTPClient import PevFTPclient

app = Flask(__name__)


'''
@description: To solves the problem of Flask static resource caching without updating accompanied with dated_url_for
'''
@app.context_processor
def inject_url():
    data = {
        "url_for": dated_url_for,
    }
    return data


def dated_url_for(endpoint, **values):
    filename = None
    if endpoint == 'static':
        filename = values.get('filename', None)
    if filename:
        file_path = os.path.join(app.root_path, endpoint, filename)
        # 取文件最后修改时间的时间戳，文件不更新，则可用缓存
        values['v'] = int(os.stat(file_path).st_mtime)
        return url_for(endpoint, **values)



"""
@description: Main page;
@Note: To contact WEB with client service; we adopt an ugly method;
       WEB->client: global Client class object; call the object's function directly
       client->WEB: global FILE object; read from it directyly
       TODO: better it
"""
@app.route('/')
def my_form():
    stdFile.seek(0)
    text = stdFile.read()
    # print(stdFile)
    # print(text)
    # TODO:Optimize the parameter transmission method
    return render_template('index.html', username=username, host=host, port=port, text=text)


"""
@description: Main page;deal with post;
"""
@app.route('/', methods=['POST'])
def my_form_post():
    if request.method == 'POST':
        global FTPClient
        query = request.form['query']
        try:
            FTPClient.run(query)
        except Exception:
            pass
        stdFile.seek(0)
        text = stdFile.read()
        print(str.strip(query))
        # print(text)
        if query == "quit":
            FTPClient = None
        return render_template('index.html', username="Peviroy", host="127.0.1.1", port=8899, text=text)


def initFTPClient(host, port, username, password, stdFile):
    clientThread = PevFTPclient(host, port, username, password, stdOut=stdFile)
    return clientThread


def getConsoleContext(consoleContextFile):
    consoleContextFile.seek(0)
    return consoleContextFile.read()


if __name__ == '__main__':
    global stdFile
    global FTPClient
    global username
    global host
    global port

    parser = optparse.OptionParser()
    parser.add_option('-s', '--server',
                      dest='server',
                      help='ftp server ip address')
    parser.add_option('-P', '--port',
                      type='int',
                      dest='port',
                      help='ftp server ip port')
    parser.add_option('-p', '--password',
                      dest='password',
                      help='password')
    parser.add_option('-u', '--username',
                      dest='username',
                      help='username')
    options, args = parser.parse_args()

    stdFile = open("Text2.txt", "w+")
    FTPClient = initFTPClient(
        options.server, options.port, options.username, options.password, stdFile)
    username = options.username
    port = options.port
    host = options.server
    app.run(host='0.0.0.0', port=8080)
