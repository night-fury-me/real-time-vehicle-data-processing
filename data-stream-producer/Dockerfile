FROM wurstmeister/kafka:latest

ARG POETRY_VER=1.6.1

# Update and install necessary packages
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
       vim python3 python3-pip python3-venv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip install poetry==$POETRY_VER \
    && mkdir -p /taskscripts

WORKDIR /taskscripts

COPY grpc_server.py vehicle_data_pb2_grpc.py vehicle_data_pb2.py pyproject.toml ./

# Install dependencies using Poetry
RUN poetry export -f requirements.txt -o requirements.txt --without-hashes \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -f requirements.txt

# Run the gRPC server (if applicable)
# CMD ["python3", "grpc_server.py"]
