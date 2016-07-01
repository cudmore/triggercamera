# About
treadmill was created by [Robert H Cudmore][1].

## Development

### mkDocs

This documentation is written in markdown and a static site is generated with [mkDocs][25] using the [Cinder][26] theme. Previously I have used Jekyll which is amazing. Going with mkDocs to see if a simple site is acceptable.

When writing markdown, serve a mkDocs site locally with

```
cd docs/
mkdocs serve --dev-addr=0.0.0.0:8000 # serves built site on LAN IP
mkdocs serve # serves built site on localhost at 127.0.0.1:8000

mkdocs build #generates the site into docs/site/
```

Deploy to github gh-pages by follow for [deployment instructions][27].

`mkdocs gh-deploy` will use the gh-pages branch of repository specified in `mkdocs.yml`

```
# this will deploy to github gh-pages specified in mkdocs.yml
cd docs #should have mkdocs.yml file
mkdocs gh-deploy --clean 

#site is then available at
http://cudmore.github.io/treadmill
```

### Tweak Cinder

Use 'pip show mkdocs' to figure out where your cinder files are

>> pip show mkdocs
>> /home/cudmore/anaconda2/lib/python2.7/site-packages


### Deploy to Github gh-pages

Following the [mkDocs][4] help, deploy to github. Again, I am doing this on OSX. Not doing this on Debian because I do not have git/github properly configured.

>> mkdocs build --clean
>> mkdocs gh-deploy --clean


### Generate a single PDF from mkDocs site

Use [mkdocs-pandoc][2] to convert the mkdocs site into a single pdf. This creates a table of contents and appends all .md files using [pandoc][3] as a backend.

```
cd docs
mkdocs2pandoc > mydocs.pd
pandoc --toc -f markdown+grid_tables+table_captions -o mydocs.pdf mydocs.pd   # Generate PDF
pandoc --toc -f markdown+grid_tables -t epub -o mydocs.epub mydocs.pd         # Generate EPUB
```

I found it easy to do this on OSX using the pandoc installer. I did not get this working on Debian.

[1]: http://robertcudmore.org
[2]: https://github.com/jgrassler/mkdocs-pandoc
[3]: http://pandoc.org
[4]: http://www.mkdocs.org/user-guide/deploying-your-docs/
[25]: http://www.mkdocs.org
[26]: http://sourcefoundry.org/cinder/
[27]: https://mkdocs.readthedocs.org/en/stable/user-guide/deploying-your-docs/