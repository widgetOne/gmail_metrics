source utils/env.sh
docker build -t gmail_metrics .
docker run  -a STDOUT -a STDERR --net host -p 5432:5432 -p 80:80 -e METRICS_SQL_AUTH=$METRICS_SQL_AUTH gmail_metrics



