# msapp

Python Microservices App for testing and learning.

```sh
## TESTING app via k8s NodePort SVC
alphasvc=$(minikube service alpha --url)
for i in {1..10}; do
  curl -s ${alphasvc}/ | jq '.'
  sleep 0.2
done
```