FROM mambaorg/micromamba:1.3.1-bullseye

COPY --chown=$MAMBA_USER:$MAMBA_USER env.yaml /tmp/env.yaml

RUN micromamba install --yes --file /tmp/env.yaml && \
    micromamba clean --all --yes

ARG MAMBA_DOCKERFILE_ACTIVATE=1

ENV PATH "$MAMBA_ROOT_PREFIX/bin:$PATH"

WORKDIR /code
COPY ./dashboard.py /code/dashboard.py
COPY ./preload_archive.pickle /code/preload_archive.pickle
COPY ./preload_list.pickle /code/preload_list.pickle
COPY ./bigbangvendorgraph.py /code/bigbangvendorgraph.py
COPY ./bigbang /code/bigbang

USER root
RUN python -m pip install -e /code/bigbang/

CMD ["panel", "serve","--warm", "dashboard.py", "--session-ids", "external-signed", "--port", "5006"]
