## Real-time Vehicle Data Processing Pipeline

### Enter into flink consumers shell

```bash
docker-compose exec -it data-streamer bash 
```

### Submit a flink job in the flink cluster

```bash
/flink/bin/flink run -py /taskscripts/data-streamer.py --jobmanager jobmanager:8081 --target local
```
