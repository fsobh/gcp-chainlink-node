## Introduction:
This guide will establish the needed security systems for high availability which is security hardened: 

(1) OpenVPN Access Server VM, 

(2) Bastion-Host which will SSH into Chainlink Nodes behind VPN with no external ip's from local client,

(3) Main VM prepared for Chainlink Node installment process, 

(4) Failover VM prepared for Chainlink Node installment process,

(5) Load Balancer

## [0] Requirements:
(1) GCP account with billing account

(2) Project to login to

(3) Google cloud SDK on local machine/client

## [1] OpenVPN Access Server
### 1.1 Create OpenVPN Access Server VM
To start a preloaded vm with openVPN access server vm pre-sized & preloaded, login to your GCP project.
In the left hand hamburger menu: Marketplace > Search Marketplace > openVPN access server > Launch

![photo_2022-02-19_06-50-44](https://user-images.githubusercontent.com/99776898/154805941-270d2a3a-5708-40a3-926b-4f9ff9f14482.jpg)

Once the VM is created, GCP will redirect to the Deployment Manager > Newly Created OpenVPN Access Server.
### 1.2 Login to Admnin Portal of the OpenVPN Access Server VM
Open the Admin URL on the right hand side, and login with the default Admin User: "openvpn" and associated randomly generated password.

![photo_2022-02-19_07-10-06](https://user-images.githubusercontent.com/99776898/154806648-3bdd7fcb-89d8-40dd-9fd2-3fb8e071f703.jpg)

### 1.3 Create VPN User Information
On the left menu, navigate to User Management > User Permissions:
Create a new user by entering the username, and associated password through "more settings". Then hit the "save settings" button at the bottom and then the "Update Running Server" button at the top. 

![image](https://user-images.githubusercontent.com/99776898/154807167-4613aa94-d1ee-43b5-b0b5-fb7c9f9d014e.png)

### 1.4 Download OpenVPN User Certificate
Access the non-admin portal of the openVPN access server hyperlink just above the admin hyperlink, or changing the port from (943=admin) to (443=admin): ```https://<vpn-access-server-external-ip>:443/```

Under Available Connection Profiles, click Yourself (user-locked profile) to download the openVPN user certificate ```client.ovpn``` file.

![photo_2022-02-19_07-34-14](https://user-images.githubusercontent.com/99776898/154807624-39427a5c-124b-432f-a5c9-60c5b3388454.jpg)


## [2] Create Bastion-Host VM 
### 2.1 Configuartion of Bastion-Host VM options
This VM instance will only be used to ssh through IAP to other VM's which will be otherwise inaccessible after configuration through standard ssh methods.

Instance name: ```bastionhost```

For this example, the zone: ```us-west1-b```

Machine Type: 2 Cores & 4 GB RAM

Static external ip

Access scopes > set access for each API > compute engine read&write

### 2.2 Login to google cloud SDK 
```
gcloud auth login
gcloud config set project project-name
```
### 2.3 Set Firewall to allow ssh through IAP
```
gcloud compute firewall-rules create allow-ssh-ingress-from-iap --network default --direction INGRESS --action allow --rules tcp:22 --source-ranges  35.235.240.0/20 --project project-name

```
### 2.4 Establish VPN connection to OpenVPN Access Server & Test internet connectivity 

```
gcloud compute ssh bastionhost --project "project-name" --zone "us-west1-b" --tunnel-through-iap
sudo apt install apt-transport-https
sudo wget https://swupdate.openvpn.net/repos/openvpn-repo-pkg-key.pub
sudo apt-key add openvpn-repo-pkg-key.pub
sudo wget -O /etc/apt/sources.list.d/openvpn3.list https://swupdate.openvpn.net/community/openvpn3/repos/openvpn3-bionic.list
sudo apt update
sudo apt install openvpn3 -y
```
Upload ```client.opvn``` file to VM from local machine

```
openvpn3 session-start --config /home/username/client.ovpn
```

Confirm connection in openvpn access server GUI: Status > Current Users


## [3] Main VM for Chainlink Node
### 3.1 Create NAT gateway to allow access to public internet with no external ip option
```
gcloud compute routers create nat-router-us-west1 --network default --region us-west1
gcloud compute routers nats create nat-config --router-region us-west1 --router nat-router-us-west1 --nat-all-subnet-ip-ranges --auto-allocate-nat-external-ips
```
### 3.2 Create Main VM

Instance name: ```node```

For this example, the zone: ```us-west1-b```

Machine Type: 4 Cores & 8 GB RAM

Static internal ip, no external ip, allow http & https connections

Access scopes > set access for each API > compute engine read&write

### 3.3 SSH from bastion-host VM to Main-VM
```
gcloud compute ssh node --project "project-name" --zone "us-west1-b" --tunnel-through-iap
```
Test internet connectivity
```
curl example.com
```
### 3.3 Establish VPN connection to OpenVPN Access Server & Test internet connectivity 
```
sudo apt install apt-transport-https
sudo wget https://swupdate.openvpn.net/repos/openvpn-repo-pkg-key.pub
sudo apt-key add openvpn-repo-pkg-key.pub
sudo wget -O /etc/apt/sources.list.d/openvpn3.list https://swupdate.openvpn.net/community/openvpn3/repos/openvpn3-bionic.list
sudo apt update
sudo apt install openvpn3 -y
```
Upload ```client.opvn``` file to VM from local machine

```
openvpn3 session-start --config /home/username/client.ovpn
```

Confirm connection in openvpn access server GUI: Status > Current Users

## [4] Failover VM for Chainlink Node
### 4.1 Create NAT gateway to allow access to public internet with no external ip option
```
gcloud compute routers create nat-router-us-central1-a --network default --region us-central1
gcloud compute routers nats create nat-config --router-region us-central1 --router nat-router-us-central1-a --nat-all-subnet-ip-ranges --auto-allocate-nat-external-ips
```
### 4.2 Create Failover VM

Instance name: ```failover-node```

For this example, the zone: ```us-central1-a```

Machine Type: 4 Cores & 8 GB RAM

Static internal ip, no external ip, allow http & https connections

Access scopes > set access for each API > compute engine read&write

### 4.3 SSH from bastion-host VM to Main-VM
```
gcloud compute ssh failover-node --project "project-name" --zone "us-central1-a" --tunnel-through-iap
```
Test internet connectivity
```
curl example.com
```
### 4.4 Establish VPN connection to OpenVPN Access Server & Test internet connectivity 
```
sudo apt install apt-transport-https
sudo wget https://swupdate.openvpn.net/repos/openvpn-repo-pkg-key.pub
sudo apt-key add openvpn-repo-pkg-key.pub
sudo wget -O /etc/apt/sources.list.d/openvpn3.list https://swupdate.openvpn.net/community/openvpn3/repos/openvpn3-bionic.list
sudo apt update
sudo apt install openvpn3 -y
```
Upload ```client.opvn``` file to VM from local machine
```
openvpn3 session-start --config /home/username/client.ovpn
```

Confirm connection in openvpn access server GUI: Status > Current Users

## [5] Load Balancer
### 5.1 Open the firewall
```
gcloud compute firewall-rules create allow-lb-and-healthcheck --source-ranges 130.211.0.0/22,35.191.0.0/16 --target-tags http-tag --allow tcp:80
```

### 5.2 Reserve external IP address for load balancer
```
gcloud compute addresses create lb-ip-cr --ip-version=IPV4 --global
gcloud compute addresses create lb-ipv6-cr --ip-version=IPV6 --global
```
### 5.3 Create Instance groups and add instances
```
gcloud compute instance-groups unmanaged create us-resources-w --zone us-west1-b
gcloud compute instance-groups unmanaged add-instances us-resources-w --instances node --zone us-west1-b
gcloud compute instance-groups unmanaged create us-resources-c --zone us-central1-a
gcloud compute instance-groups unmanaged add-instances us-resources-c --instances failover-node --zone us-central1-a
```
### 5.4 For each instance group, define an HTTP service and map a port name to the relevant port:
```
gcloud compute instance-groups unmanaged set-named-ports us-resources-w --named-ports http:80 --zone us-west1-b
gcloud compute instance-groups unmanaged set-named-ports us-resources-c --named-ports http:80 --zone us-central1-a
```

### 5.5 Create health check
```
gcloud compute health-checks create http http-basic-check --port 80
```

### 5.6 Create backend service
```
gcloud compute backend-services create web-map-backend-service --protocol HTTP --health-checks http-basic-check --global
```

### 5.7 Add your instance groups as backends to the backend services:
```
gcloud compute backend-services add-backend web-map-backend-service --balancing-mode UTILIZATION --max-utilization 0.8 --capacity-scaler 1 --instance-group us-resources-w --instance-group-zone us-west1-b --global
gcloud compute backend-services add-backend web-map-backend-service --balancing-mode UTILIZATION --max-utilization 0.8 --capacity-scaler 1 --instance-group us-resources-c --instance-group-zone us-central1-a --global
```

### 5.8 Set host and path rules
```
gcloud compute url-maps create web-map --default-service web-map-backend-service
gcloud compute target-http-proxies create http-lb-proxy --url-map web-map
```
### 5.9 Configure the frontend
```
gcloud compute addresses list
gcloud compute forwarding-rules create http-cr-rule --address ipv4-address --global --target-http-proxy http-lb-proxy --ports 80
gcloud compute forwarding-rules create http-cr-ipv6-rule --address ipv6-address --global --target-http-proxy http-lb-proxy --ports 80
```

### 5.10 Get the IP addresses of your global forwarding rules, and make a note of them for the next step:
```
gcloud compute forwarding-rules list
```

### 5.11 Test the IPv4 & IPv6 Connections
```
curl http://ipv4-address
curl -g -6 "http://[ipv6-address]/"
```


## References
(1) https://openvpn.net/cloud-docs/openvpn-3-client-for-linux/

(2) https://cloud.google.com/architecture/building-internet-connectivity-for-private-vms#console_1
