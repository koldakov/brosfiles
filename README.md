# About The Project

File storage.
This project is focused on deploying on AWS.

## Installation

1. `python -m venv .venv`
2. `source .venv/bin/activate`
3. `pip install -r requirements.txt`

<p align="right">(<a href="#top">back to top</a>)</p>

## Usage

Bootstrap libraries won't be added to the project. Run `bash bin/download_vendor` to download vendor libs.

### Development

1. Export `.env.template` with related environment variables
2. `python manage.py runserver` or `bash entrypoint.sh`

<p align="right">(<a href="#top">back to top</a>)</p>

### AWS

#### Deploy the project

1. aws ecr get-login-password --region [REGION] | docker login --username AWS --password-stdin [ECR_DOCKER_URI].[REGION].amazonaws.com/[ECR_REPOSITORY_NAME]
2. docker tag [DOCKER_IMAGE]:latest [ECR_DOCKER_URI].[REGION].amazonaws.com/[ECR_REPOSITORY_NAME]
3. docker push [ECR_DOCKER_URI].[REGION].amazonaws.com/[ECR_REPOSITORY_NAME]

#### Configure AWS

1. Instructions won't be provided
2. Later terraform code will be included

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

## Stripe

For a webhook you need to configure stripe settings in a dashboard.

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
