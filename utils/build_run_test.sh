source utils/env.sh
docker build -t gmail_metrics .
# docker run  -ai  -p 5432:5432 -p 80:80 -d -e METRICS_SQL_AUTH=$METRICS_SQL_AUTH gmail_metrics
docker run  -a STDOUT -a STDERR  -p 5432:5432 -p 80:80 -e METRICS_SQL_AUTH=$METRICS_SQL_AUTH gmail_metrics
