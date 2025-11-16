# TLS Certificate Bundle

Generate certificates before starting docker-compose:

1. Define instance metadata (`certs/instances.yml`):

```
elasticsearch:
  dns: ["elasticsearch", "localhost"]
  ip: ["127.0.0.1"]
kibana:
  dns: ["kibana", "localhost"]
logstash:
  dns: ["logstash", "localhost"]
filebeat:
  dns: ["filebeat", "localhost"]
```

2. Create a Certificate Authority and node certificates:

```
cd certs
ELASTIC_IMAGE=docker.elastic.co/elasticsearch/elasticsearch:8.8.2
# Create CA
docker run --rm -v $(pwd):/certs $ELASTIC_IMAGE \
  bash -c "cd /certs && bin/elasticsearch-certutil ca --pem --silent --out ca.zip"
unzip ca.zip
# Create certs from instances.yml
cat > instances.yml <<'INST'
elasticsearch:
  dns: ["elasticsearch", "localhost"]
  ip: ["127.0.0.1"]
kibana:
  dns: ["kibana", "localhost"]
logstash:
  dns: ["logstash", "localhost"]
filebeat:
  dns: ["filebeat", "localhost"]
INST

docker run --rm -v $(pwd):/certs $ELASTIC_IMAGE \
  bash -c "cd /certs && bin/elasticsearch-certutil cert --pem --in instances.yml --ca-cert ca/ca.crt --ca-key ca/ca.key --out certs.zip --silent"
unzip certs.zip
```

3. Copy files expected by docker-compose:
   - `ca/ca.crt`
   - `elasticsearch/elasticsearch.crt` & `.key`
   - `kibana/kibana.crt` & `.key`
   - `logstash/logstash.crt` & `.key`
   - `filebeat/filebeat.crt` & `.key`

Rename/move them into the root of this folder so that docker-compose can mount:

```
cp ca/ca.crt ./ca.crt
cp elasticsearch/elasticsearch.crt ./elasticsearch.crt
cp elasticsearch/elasticsearch.key ./elasticsearch.key
cp kibana/kibana.crt ./kibana.crt
cp kibana/kibana.key ./kibana.key
cp logstash/logstash.crt ./logstash.crt
cp logstash/logstash.key ./logstash.key
cp filebeat/filebeat.crt ./filebeat.crt
cp filebeat/filebeat.key ./filebeat.key
```

The same CA file is reused by Filebeat and Logstash when verifying TLS connections.
