# Running service 

.env-file in root

```
SPOTIFY_CLIENT_ID=<spotify_client_id>
SPOTIFY_CLIENT_SECRET=<spotify_client_secret>
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/callback


```

```
podman build -t now-playing .
podman run -p 8000:8000 --env-file .env now-playing
```


# Testin API with rest-client

in browser: 

```
localhost:8000/login
```

capture the access_token, store in .env file in rest-client folder for testing with now-playing.rest

```
access_token = <token>
```