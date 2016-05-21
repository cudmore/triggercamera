##PlatformIO

    platformio run --target upload
    
    platformio run --target clean
    
    platformio serialports monitor -p /dev/ttyACM0 -b 115200 #a serial port monitor
    
## mkDocs

    pip install mkdocs
    pip install mkdocs-cinder

    mkdocs serve
    mkdocs serve --dev-addr=0.0.0.0:8000 # serves built site on LAN IP
    
* `mkdocs new [dir-name]` - Create a new project.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs help` - Print this help message.

### Deploy to github

mkdocs gh-deploy will use the gh-pages branch of repository specified in mkdocs.yml

	# this will deploy to github gh-pages specified in mkdocs.yml
	cd tiggercamera #should have mkdocs.yml file
	mkdocs build --clean
	mkdocs gh-deploy --clean 
	#site is then available at
	http://cudmore.github.io/triggercamera

### Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.
