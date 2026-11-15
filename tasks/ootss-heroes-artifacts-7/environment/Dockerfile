FROM game-bench-harbor/runtime:20261115
USER root
COPY game/ /app/game/
COPY serve.py /app/serve.py
RUN mkdir -p /artifacts /logs/verifier
WORKDIR /workspace
CMD ["sleep", "infinity"]
