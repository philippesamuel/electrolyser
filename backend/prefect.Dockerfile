FROM prefecthq/prefect:3-latest

# install curl
RUN apt-get update && apt-get install -y curl