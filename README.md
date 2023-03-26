## Infrastructure Governance Dashboard

A panel application running on the bigbang server.

The application uses [Caddy](https://caddyserver.com/) as the webserver. This is already installed on caddy as a host (systemd) service.

Currently the docker containers are deployed manually on the server, there isn't a continuous deployment pipeline from github to the server.
This will probably require a paid dockerhub acccount.


### Steps to build image locally and deploy on the server

- ~~podman and docker can be used interchangeably~~
- Currently the images are hosted on my dockerhub account (mriduls). To push these images to a personal dockerhub account you would need to change the name of the image while building them locally.
- Make sure you are in the `images` directory.
- These dashboard image build will fail! As I have not pushed the pickle files to github. Contact me to get these files.

To build the dashboard image:

```
docker build --platform linux/amd64 -t mriduls/dashboard_bigbang -f dashboard/Dockerfile dashboard/
```

To build the login service image:

```
docker build --platform linux/amd64 -t mriduls/login_service -f login_service/Dockerfile login_service/
```

Push both of these images to dockerhub (make sure you are logged into the right container registry account)

```
docker push mriduls/dashboard_bigbang
docker push mriduls/login_service
```

Once you have pushed these images, ssh into the bigbang server and start these 2 services with the right env variables.

To start the login service
```
docker run -p 8000:80 -e BOKEH_SECRET_KEY={see below} \
-e BOKEH_SIGN_SESSIONS=True \
-e LOGIN_DASHBOARD_URL=https://{dashboard_url}/dashboard \
-e LOGIN_USERNAME={select_a_username} \
-e LOGIN_PASSWORD={select_a_password} \
mriduls/login_service:latest
```

To start the dashboard service

```
docker run -e BOKEH_SECRET_KEY={see below} \
-e BOKEH_SIGN_SESSIONS=True \
-e BOKEH_ALLOW_WS_ORIGIN={dashboard_url} \
-p 5006:5006 mriduls/dashboard_bigbang:latest
```

To "protect" the bokeh server, we use signed sessions so you need to generate a bokeh secret key by doing `bokeh secret`. You can run this command in any environment just make sure it matches the bokeh version in the images (2.4.3)

The Caddyfile in this repository also shows the config used to set the reverse proxies to the docker containers.


##### TODO
- [ ] Write about pickling of archives
- [ ] Use docker-compose to make deploying a bit more cleaner
- [ ] There is a vendored copy of bigbang in this repo which needs to be removed when it's possible to install it from conda/pip easily. The micromamba image wasn't working well with doing a git install.
