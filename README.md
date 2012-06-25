texts.annotateit.org
====================

This is a really simple application that stores text documents and presents them for annotation by [AnnotateIt](http://annotateit.org).

Can you guess [where it lives?](http://texts.annotateit.org)


dev
---

    pip install honcho -r requirements.dev.txt
    honcho -f Procfile.dev start


prod
----

    git remote add heroku git@heroku.com:texts.git
    git push heroku master