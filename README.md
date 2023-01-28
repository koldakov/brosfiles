# About The Project

File storage.
This project is focused on deploying on Google cloud.

## Installation

1. `python -m venv .venv`
2. `source .venv/bin/activate`
3. `pip install -r requirements.txt`

<p align="right">(<a href="#top">back to top</a>)</p>

## Usage

Bootstrap libraries won't be added to the project. Run `bash bin/download_bootstrap` to download bootstrap.

### Development

1. Create .env (`cp .env.template .env`) file with related environment variables
2. `python manage.py runserver` or `bash entrypoint.sh`
3. `bash entrypoint.sh` requires `BF_LOCAL_RUN` to be set, see [this](entrypoint.sh)
4. To run with Google cloud DB see [this](https://cloud.google.com/python/django/appengine#run-locally)

<p align="right">(<a href="#top">back to top</a>)</p>

### AWS

#### Deploy the project

1. aws ecr get-login-password --region [REGION] | docker login --username AWS --password-stdin [ECR_DOCKER_URI].[REGION].amazonaws.com/[ECR_REPOSITORY_NAME]
2. docker tag [DOCKER_IMAGE]:latest [ECR_DOCKER_URI].[REGION].amazonaws.com/[ECR_REPOSITORY_NAME]
3. docker push [ECR_DOCKER_URI].[REGION].amazonaws.com/[ECR_REPOSITORY_NAME]

#### Configure AWS

1. Instructions won't be provided
2. Later terraform code will be included

### Google cloud

1. See [this](https://cloud.google.com/python/django/appengine)
2. To deploy: `bash bin/deploy` (gcloud and wget are needed).
3. Bootstrap should be placed to `base/static/bootstrap/` (deploy command includes this step),
libraries can't be downloaded from Google engine.
4. To resolve the CORS issues:
    - cp configurations/cors.json.template configurations/cors.json with needed values
    - gcloud storage buckets update gs://bucket-name --cors-file=configurations/cors.json
5. Google Cloud Storage:
    - To create key see [this](https://cloud.google.com/iam/docs/creating-managing-service-account-keys#iam-service-account-keys-create-console)
    - Set path of this key to GOOGLE_APPLICATION_CREDENTIALS see [.env.template](.env.template)

#### Important

GAE not supported after `e7c71b8320f3470606fb7e747caa745851aa9dd6` commit.
Later GAE related code will be fully removed.

<p align="right">(<a href="#top">back to top</a>)</p>

## Testing

To run unit tests:
1. `export DEBUG=True`
2. `python manage.py test`

## Migrations

For migrations, add `BF_ADMIN_USERNAME` and `BF_ADMIN_PASSWORD` to virtual environment to create admin user.

## Notes

### Methodology

1. Do a lot, break a lot
2. There are no difficult tasks, only interesting

### Important

1. Quality
2. Security
3. Google first

### Not important
1. "GIT history

## Visitor counter

<img src="https://profile-counter.glitch.me/aivgithub/count.svg" />
