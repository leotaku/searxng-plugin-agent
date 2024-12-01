FROM docker.io/searxng/searxng:latest
ARG PLUGIN="/tmp/searxng-plugin-agent"
RUN mkdir -p "$PLUGIN"
COPY pyproject.toml agent.py "$PLUGIN"
COPY settings.yml /etc/searxng/settings.yml
RUN python -m pip install --break-system-packages --no-cache "$PLUGIN"
