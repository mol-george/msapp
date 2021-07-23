# msapp

Python Microservices App for testing and learning.

Based on:
* https://hub.docker.com/r/tiangolo/uwsgi-nginx-flask/ -> https://hub.docker.com/r/tiangolo/uwsgi-nginx/
* https://github.com/tiangolo/uwsgi-nginx-flask-docker

**Note:**
* `msapp` has two versions: v1, v2
* the only difference between versions is the deployment `VERSION` env passed
* the deployments can pass `venv` that that control the behavior of the application:
  - `VERSION`: decides the 'version' of the application - actually the only difference between versions
  - `NEXT_APP`: decide if the app is attempting to make GET requests to another app
* the app propagates any `x-` headers but it only returns to GET requests:
  - X-Request-Id
  - X-Dark-Header (somehow header case gets modified by request python library)

```sh
## APP STRUCTURE
 # tree microsvc -L 3
└── msapp
    ├── Dockerfile
    ├── app
    │   ├── main.py
    │   ├── requirements.txt
    │   └── venv
    └── k8s
        ├── alpha-dep-v1.yaml
        ├── alpha-dep-v2.yaml
        ├── alpha-svc.yaml
...
...

# --------------- DOCKER --------------- #
## REMOVE ALL DOCKER STOPPED CONTAINERS AND UNUSED IMAGES
docker system prune -a

## IMAGE (Dockerfile's dir)
docker build -t molgeorge/mssap:v1 .
docker push molgeorge/mssap:v1
docker image rm molgeorge/mssap:v1

## CONTAINER
docker run -d --name alpha -p 80:80 molgeorge/mssap:v1
docker container exec -it alpha sh
docker container ls
docker container stop alpha
docker container rm alpha

# --------------- PYTHON --------------- #
python3 -m venv venv
source venv/bin/activate
pip install -U <module>
pip freeze > requirements.txt
pip install -r requirements.txt
python main.py

# --------------- K8S --------------- #
k create deployment alpha --image=molgeorge/mssap:v1 --replicas=2 $do | k neat | yq eval . - > dep.yaml
k expose deployment alpha --type=NodePort --port=80 $do | k neat | yq eval . - > svc.yaml
k apply -f .

## TESTING app via k8s NodePort SVC
alphasvc=$(minikube service alpha --url)
for i in {1..10}; do
  curl -s ${alphasvc}/ | jq '.'
  sleep 0.2
done
```

## similar projects
* https://github.com/jetstack/field-istio-demo/tree/master/demos

## next
* generate name for microservices if not provided github.com/goombaio/namegenerator
* implement makefile
* describe project in Yaml
* implement grpc between microservices
* make use of virtual clusters
