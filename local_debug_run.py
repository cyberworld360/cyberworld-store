from app import app

if __name__ == '__main__':
    # run with debug True to see tracebacks in console
    app.debug = True
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
