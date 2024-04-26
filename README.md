# Python Docker App

Containered wrapper for python apps (FastAPI, Panels) handling deployment and authentification (OAuth)

## Usage

### Development
```bash
git clone https://github.com/OpenSemanticWorld/python-docker-app myapp
cd myapp
cp .env.example .env
cp -R app/apps.example app/apps
```

Modify `pn_dashboard.py` as required and make sure `apps/__init__.py` populates the `serving` variable according to the example.

Run `python pn_dashboard.py` for local development. Supply an `accounts.pwd.yaml` file if needed.

You can also add an existing app as submodule in subfolder `app`:
```bash
git submodule add <repo> apps
```

### OAuth Registration
1. In your target OSL/OSW instance, go to `Special:OAuthConsumerRegistration` and select 'OAuth1a (`Special:OAuthConsumerRegistration/propose/oauth1a`).
1. Set the target domain of your app as OAuth-Callback-URL: 'https://{{`DOMAIN`}}'
1. Check 'Callback-URL as Prefix'
1. Add rights as needed
1. Save and note down (!) the Consumer-Token (=> `OAUTH_CLIENT_ID`) and Secret Token (=> `OAUTH_CLIENT_SECRET`)
1. Accept your client by navigating to
`Special:OAuthManageConsumers/proposed` or directly
`Special:OAuthManageConsumers/<OAUTH_CLIENT_ID>`

In your target OSL/OSW instance, make sure to copy `$wgSecretKey=...` from the `LocalSettings.php` file within the container to `/mediawiki/config/CustomSettings.php` because rebuilding the container otherwise creates new secret which invalidates existing OAuth secrets

### Docker Deployment
Requires a running [caddy-docker-proxy](https://github.com/OpenSemanticWorld/caddy-docker-proxy)

Fill out the `.env` file:
```env
DOMAIN=myapp.host.com # (Public) domain of your app
OAUTH_CLIENT_ID = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' # from the OAuth client registration process
OAUTH_CLIENT_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' # from the OAuth client registration process
APP_SESSION_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' # random string to encrypt session cookies
APP_JWT_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' hex key 128 Bit to sign JWTs
APP_JWE_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' hex key 128 Bit to encrypt JWTs
OSW_SERVER = 'https://my-osl.com' # target OSL/OSW instance
APP_HOST = '0.0.0.0' # fastapi host
APP_PORT = '80' # fastapi port (only exposed internally in the caddy network)
```

Run
```bash
docker compose build
```

To update a submodule, run
```bash
docker compose stop && git submodule update --remote --merge && cd apps && docker compose build && cd .. && docker compose up
```

