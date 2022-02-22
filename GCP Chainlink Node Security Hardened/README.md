# GCP Chainlink Node with security and failover enabled

This guide is intended to work in conjunction with the OpenVPN Access Server guide which should be done before setup of the Chainlink node itself.

This guide operates a chainlink node ```v1.1.0``` (latest at time of writing) on Ethereum mainnet with failover which has TLS enabled, local Ethereum node with remote Ethereum node as failover.

## [0] Requirements
(1) VMs intended to run Chainlink node service has access to the internet

(2) postgreSQL Server setup with associated user and database

## [1] Setup basic Chainlink Node with local Ethereum Node

### 1.0 SSH into VM for Chainlink node service
Login via google cloud SDK
```
gcloud auth login
gcloud config set project project-id
gcloud compute ssh node --project "project-id" --zone "us-west1-b" --tunnel-through-iap -- -L 6688:localhost:6688
```
### 1.1 Update & Prepare VM for Chainlink node service
```
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install nano && sudo apt-get install apache2 -y
sudo service apache2 restart
curl -sSL https://get.docker.com/ | sh
sudo usermod -aG docker $USER
exit
```
### 1.2 Run and sync local Ethereum Node
```
docker run --name eth -d --restart unless-stopped -p 8546:8546 -v ~/.geth:/geth -it \
           ethereum/client-go --mainnet --ws --ipcdisable \
           --ws.addr 0.0.0.0 --ws.origins="*" --datadir /geth --syncmode full --rpc.gascap=0 --rpc.txfeecap=0
```
If concerned about disk usage, check total disk usage by
```
sudo df -h
```
### 1.3 Install Chainlink Node
Create local directory to hold chainlink data
```
mkdir ~/.chainlink
```
Create environment (.env) file
```
echo "ROOT=/chainlink
LOG_LEVEL=debug
ETH_CHAIN_ID=1
CHAINLINK_TLS_PORT=0
SECURE_COOKIES=false
ALLOW_ORIGINS=*" > ~/.chainlink/.env
```
Set Ethereum Client URL
```
ETH_CONTAINER_IP=$(docker inspect --format '{{ .NetworkSettings.IPAddress }}' $(docker ps -f name=eth -q))
echo "ETH_URL=ws://$ETH_CONTAINER_IP:8546" >> ~/.chainlink/.env
```
Set Database URL
```
echo "DATABASE_URL=postgresql://$USERNAME:$PASSWORD@$SERVER:$PORT/$DATABASE" >> ~/.chainlink/.env
```
Start the Chainlink node
```
cd ~/.chainlink && docker run -p 6688:6688 -v ~/.chainlink:/chainlink -it --env-file=.env smartcontract/chainlink:1.1.0 local n
```
Confirm keystore password, GUI email and associated password
Stop the Chainlink node services with keyboard command: ```<CTRL+C>```
### 1.4 Setup auto login process for Chainlink Node
```
echo "<GUI EMAIL>" > ~/.chainlink/.api
echo "password" >> ~/.chainlink/.api
echo "<keystore password>" > ~/.chainlink/.password
```
Test the auto login setup
```
cd ~/.chainlink && docker run -p 6688:6688 -v ~/.chainlink:/chainlink -it --env-file=.env smartcontract/chainlink:1.1.0 local n -p /chainlink/.password -a /chainlink/.api
```
Login to Chainlink node GUI:
http://localhost:6688
### 1.5 Enabling HTTPS Connections
Generate certificate and key
```
mkdir ~/.chainlink/tls
openssl req -x509 -out  ~/.chainlink/tls/server.crt  -keyout ~/.chainlink/tls/server.key \
  -newkey rsa:2048 -nodes -sha256 -days 365 \
  -subj '/CN=localhost' -extensions EXT -config <( \
   printf "[dn]\nCN=localhost\n[req]\ndistinguished_name = dn\n[EXT]\nsubjectAltName=DNS:localhost\nkeyUsage=digitalSignature\nextendedKeyUsage=serverAuth")
```
Update Chainlink node ```.env``` file 
```
echo "TLS_CERT_PATH=/chainlink/tls/server.crt
TLS_KEY_PATH=/chainlink/tls/server.key" >> .env
sed -i '/CHAINLINK_TLS_PORT=0/d' .env
sed -i '/SECURE_COOKIES=false/d' .env
```
Relog into the VM via Google Cloud SDK with updated port 6689
```
gcloud compute ssh node --project "project-id" --zone "us-west1-b" --tunnel-through-iap -- -L 6689:localhost:6689
```
Start Chainlink node with updated ports
```
cd ~/.chainlink && docker run --name node --restart=always -p 6689:6689  -d -v ~/.chainlink:/chainlink -it --env-file=.env smartcontract/chainlink:1.1.0 local n -p /chainlink/.password -a /chainlink/.api
```
Login to Chainlink node GUI:
https://localhost:6689

### 1.6 Setup Ethereum Node Failover
Pull the docker image
```
docker pull fiews/cl-eth-failover
```
Test eth-failover container connectivity with chainlink node with local ethereum node
```
docker run --name eth-failover -d fiews/cl-eth-failover ws://<eth-local-node-ip>:8546
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' eth-failover
>> <ip of eth-failover docker container>
```
Update ```ETH_URL``` field in Chainlink node ```.env``` file
```
ETH_URL=ws://<ip of eth-failover docker container>:4000/
```
Inspect output to ensure connectivity to eth-failover container 
```
cd ~/.chainlink && docker run --name node --restart unless-stopped -p 6689:6689 -v ~/.chainlink:/chainlink -it --env-file=.env smartcontract/chainlink:1.1.0 local n -p /chainlink/.password -a /chainlink/.api
```
Test eth-failover container connectivity with local node & failover remote node
```
docker run --name eth-failover -d fiews/cl-eth-failover ws://<eth-local-node-ip>:8546 wss://mainnet.infura.io/ws/v3/<address>
cd ~/.chainlink && docker run --name node -d --restart unless-stopped -p 6689:6689 -v ~/.chainlink:/chainlink -it --env-file=.env smartcontract/chainlink:1.1.0 local n -p /chainlink/.password -a /chainlink/.api
```
Disconnect ethereum local node to ensure failover works as intended
```
docker rm -f eth
docker logs --tail 100 <container-id of eth-failover container>
docker logs --tail 100 <container-id of chainlink node container>
```
Restart local ethereum node
```
docker run --name eth -d --restart unless-stopped -p 8546:8546 -v ~/.geth:/geth -it \
          ethereum/client-go --mainnet --ws --ipcdisable \
          --ws.addr 0.0.0.0 --ws.origins="*" --datadir /geth --rpc.gascap=0 --rpc.txfeecap=0
```

### 1.7 Deploy Chainlink Failover Node through Docker
Update ```.env``` database locking process
```
echo "DATABASE_LOCKING_MODE=lease" >> ~/.chainlink/.env
```
Run the failover Chainlink node to ensure uptime during updates/upgrades or fatal errors to the main Chainlink node container
```
cd ~/.chainlink && docker run --name failover_node --restart=always -p 6687:6689 -d -v ~/.chainlink:/chainlink -it --env-file=.env smartcontract/chainlink:1.1.0 local n -p /chainlink/.password -a /chainlink/.api
```
### 1.8 Backup Chainlink Node Gas Wallet
```
docker exec -it node /bin/bash
chainlink admin login
<GUI email>
<GUI password>
```
Get node public address
```
chainlink keys eth list
```
Export the key to chainlink node VM
```
chainlink keys eth export -p /chainlink/.password -o /chainlink/node_main_key.json <node wallet ethereum public address>
```
### 2.0 Basic Monitoring
Run docker containers with additional log options to output to GCP Logging
```
cd ~/.chainlink && docker run --log-driver=gcplogs --name node -d --restart unless-stopped -p 6689:6689 -v ~/.chainlink:/chainlink -it --env-file=.env smartcontract/chainlink:1.1.0 local n -p /chainlink/.password -a /chainlink/.api
```
The output of these logs can be found in the GCP GUI > Hamburger menu > Operations > Logging > VM Instance

Exporting & Inspecting the docker logs directly by locating the docker log file
```
docker inspect --format='{{.LogPath}}' node
```
Download this file using cloud storage solutions to your local machine, and inspection directly of the docker logs is possible

### 2.1 Advanced Monitoring
Please see the following link which uses Prometheus, Node Exporter, Loki, Promtail, and Grafana all with TLS. This enables a number of notification alerts such as email and telegram with high quality data visualization graphs of the chainlink node and vm machine.
https://github.com/Linkriver/Chainlink-Prometheus-Grafana-TLS-Monitoring

## References
(1) https://docs.chain.link/docs/running-a-chainlink-node/

(2) https://docs.chain.link/docs/run-an-ethereum-client/

(3) https://geth.ethereum.org/docs/interface/command-line-options

(4) https://docs.chain.link/docs/enabling-https-connections/

(5) https://docs.chain.link/docs/best-security-practices/

(6) https://docs.chain.link/docs/miscellaneous/

(7) https://docs.chain.link/docs/configuration-variables/

(8) https://github.com/Fiews/ChainlinkEthFailover

(9) https://github.com/Linkriver/Chainlink-Prometheus-Grafana-TLS-Monitoring

(10) https://linkriver.io/wp-content/uploads/2021/03/Chainlink_Node_Operations_Research_Paper.pdf
