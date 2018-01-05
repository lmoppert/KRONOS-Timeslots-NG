#!/bin/bash
sudo chown www-data:www-data $PROJECT_PATH/.*
sudo chown www-data:www-data $PROJECT_PATH/* -R
sudo chown www-data:www-data $PROJECT_PATH/.hg/* -R
sudo chown www-data:www-data /var/www/static/coverage -R

sudo chmod g+rw $PROJECT_PATH/* -R
