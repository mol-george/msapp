# msapp

Python Microservices App for testing and learning.

* based on:
  - https://hub.docker.com/r/tiangolo/uwsgi-nginx-flask/ -> https://hub.docker.com/r/tiangolo/uwsgi-nginx/
  - https://github.com/tiangolo/uwsgi-nginx-flask-docker
* `msapp` has two versions: v1, v2
* the only difference between versions is the deployment `VERSION` env passed
* the deployments can pass `venv` that that control the behavior of the application:
  - `VERSION`: decides the 'version' of the application - actually the only difference between versions
  - `NEXT_APP`: decide if the app is attempting to make GET requests to another app
* the app propagates any `x-` headers but it only returns to GET requests:
  - X-Request-Id
  - X-Dark-Header (somehow header case gets modified by request python library)



```sh
## deploying the app
k apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: alpha
  name: alpha
spec:
  replicas: 2
  selector:
    matchLabels:
      app: alpha
  template:
    metadata:
      labels:
        app: alpha
    spec:
      containers:
        - image: molgeorge/msapp:v1
          name: msapp
          volumeMounts:
            - name: downward
              mountPath: /etc/downward
      volumes:
        - name: downward
          downwardAPI:
            items:
              - path: "labels"
                fieldRef:
                  fieldPath: metadata.labels
---
apiVersion: v1
kind: Service
metadata:
  labels:
    app: alpha
  name: alpha
spec:
  ports:
  - name: "80"
    port: 80
  selector:
    app: alpha
EOF

```
---

**NOTE:**
The instructions bellow are the original instructions to deploy the app but currently they do not work.
They do not work because:
* I aimplemented [The Downward API](https://kubernetes.io/docs/tasks/inject-data-application/downward-api-volume-expose-pod-information/#the-downward-api) via a volume and volumeMount [here](https://github.com/mol-george/msapp/blob/72824cef78566f4fdf632a63a8aafe96f1f7f1d1/app/main.py#L73)
* the reason to implement this was for the app to return info about the pod is running on and also to control the app via labels, however I have not updated the _yet_ the original instructions
* the app does not handle gracefully if the path does not exists (i.e. the volume and its mount are not in place)

A better way to deploy and test the app is via [helm](https://gitlab.com/mol-george-notes/istio/-/tree/main/demos)

---
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
docker build -t molgeorge/msapp:v1 .
docker push molgeorge/msapp:v1
docker image rm molgeorge/msapp:v1

## CONTAINER
docker run -d --name alpha -p 80:80 molgeorge/msapp:v1
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
k create deployment alpha --image=molgeorge/msapp:v1 --replicas=2 $do | k neat | yq eval . - > dep.yaml
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
* fix instructions to take into account the take into account the "The Downward API" implementation i.e. create volume and volumeMount, or update them to use helm
* fix [app](https://github.com/mol-george/msapp/blob/72824cef78566f4fdf632a63a8aafe96f1f7f1d1/app/main.py#L73) to handle path inexistance gracefully e.g. using [`pathlib `Path` module](https://stackoverflow.com/questions/82831/how-do-i-check-whether-a-file-exists-without-exceptions)
* generate name for microservices if not provided github.com/goombaio/namegenerator
* implement makefile
* describe project in Yaml
* implement grpc between microservices
* make use of virtual clusters
* uses cases for other istio implementations e.g. external services
