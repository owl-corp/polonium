FROM --platform=linux/amd64 python:3.10-slim

# Define Git SHA build argument for sentry
ARG git_sha="development"
ENV GIT_SHA=$git_sha

# Install project dependencies
WORKDIR /bot
COPY main-requirements.txt ./
RUN pip install -r main-requirements.txt

# Copy the source code in last to optimize rebuilding the image
COPY . .

ENTRYPOINT ["python"]
CMD ["-m", "bot"]
