web: gunicorn 'texts:create_app()' -b 0.0.0.0:$PORT -w 16 -k gevent -t 10 --name texts.annotateit.org --log-config logging.cfg