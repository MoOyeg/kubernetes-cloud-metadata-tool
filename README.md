# kubernetes-cloud-metadata-tool

Simple Tool to collect metadata from Cloud Provider Metadata URL's so app's can query.

## How it works and what it does

Tool runs as a daemonset on every worker node on the cluster. At the moment it determines the correct cloud and collects pre-configured metrics from that cloud.The daemonset runs on the host network of the nodes. To leverage security built in Openshift/Kubernetes pods that want to get metadata should only reach out to the tool pods running on the same node.

To access the service you can use:

- Access Pod endpoints directly.  
  Get the Node Name from the downwardAPI and call the port of the tool(presently set at 8080, but can be reconfigured).

- Access Kubernetes Service with Topology Awareness.  
   1  Create a Kubernetes service and use "internalTrafficPolicy: Local" on the service. Requires enable feature-request <https://kubernetes.io/docs/concepts/services-networking/service-traffic-policy/>.  
   2  Create a Kubernetes service and use "topologyKeys: kubernetes.io/hostname" on the service. Requires enable feature-request <https://kubernetes.io/docs/concepts/services-networking/service-topology/>.

## How to run

### Openshift  

- Git clone this repo  
  ```git clone https://github.com/MoOyeg/kubernetes-cloud-metadata-tool.git```

- Change directory into cloned repo and Create Namespace metadata-service  
  ```oc create -f ./deploy/namespace.yaml```

- Create BuildConfig to create image  
  ```oc create -f ./deploy/buildconfig.yaml -n metadata-service```

- Create privileged Service Account  
  ```oc create -f ./deploy/privileged-sa.yaml -n metadata-service```

- Add Privileged scc to privileged-sa  
  ```oc create -f ./deploy/clusterrolebinding-scc.yaml -n metadata-service```

- Add edit permissions to privileged-sa  
  ```oc create -f ./deploy/rolebinding-privileged.yaml -n metadata-service```

- Create Daemonset, replace image with internal built image  
  ```cat ./deploy/daemonset.yaml | sed 's*<image-replace>*image-registry.openshift-image-registry.svc:5000/metadata-service/kubernetes-cloud-metadata-tool:latest*' | oc create -f - -n metadata-service```

- To run a sample  
  ```oc create -f ./deploy/test-pod.yaml -n metadata-service && while [ $(oc get pod/test-metadata-pod -n metadata-service -o jsonpath="{.status.phase}") != "Succeeded" ];do echo "Waiting For Pod to Complete" && sleep 1;done && echo -e "\n" && oc logs -f pod/test-metadata-pod -n metadata-service && echo -e "\n"; oc delete pod/test-metadata-pod -n metadata-service```

### Kubernetes  

- Git clone this repo  
  ```git clone https://github.com/MoOyeg/kubernetes-cloud-metadata-tool.git```

- Change directory into cloned repo and Create Namespace metadata-service  
  ```oc create -f ./deploy/namespace.yaml```

- Build Dockerfile with any tool you choose .e.g  
  ```podman build ./ -t metadata-tool```

- Push image to repository of choice

- Create privileged Service Account  
  ```oc create -f ./deploy/privileged-sa.yaml -n metadata-service```

- Create Pod Security Policy(Note this PSP is very expansive, don't use on Prod, also PSP's are deprecated - <https://kubernetes.io/blog/2021/04/06/podsecuritypolicy-deprecation-past-present-and-future/>  
  ```oc create -f ./deploy/psp-metadata.yaml```

- Create psp cluster-role  
  ```oc create -f ./deploy/psp-clusterrole.yaml```

- Create psp cluster-roleBinding  
  ```oc create -f ./deploy/psp-clusterrolebinding.yaml```

- Add edit permissions to privileged-sa  
  ```oc create -f ./deploy/rolebinding-privileged.yaml -n metadata-service```

- Create Daemonset, replace image with your own built image,also nodeselector might be different in your case  
  ```cat ./deploy/daemonset.yaml | sed 's*<image-replace>*quay.io/mooyeg/metadata-tool:latest*' | sed 's*node-role.kubernetes.io/worker*node-role.kubernetes.io/node*' | oc create -f - -n metadata-service```

- To run a sample  
  ```oc create -f ./deploy/test-pod.yaml -n metadata-service && while [ $(oc get pod/test-metadata-pod -n metadata-service -o jsonpath="{.status.phase}") != "Succeeded" ];do echo "Waiting For Pod to Complete" && sleep 1;done && echo -e "\n" && oc logs -f pod/test-metadata-pod -n metadata-service && echo -e "\n"; oc delete pod/test-metadata-pod -n metadata-service```

## TODO  

- Tool should allow apps provide the exact query as a parameter for data of interest from cloud provider.
