<p align="center">
  <img src="assets/diagram.png" 
</p>
  
## ☁️ 30 Days DevOps Challenge - Converting Champions League Football Highlights with Docker, Terraform and Amazon Media Converter.   ☁️

This is part of the fourth project in the 30-day DevOps challenge! 

In this project, I built a containerized API management system for querying sports data by leveraging a Flask application within docker containers, to be deployed to an application load balancer (ALB) which will route the traffic of the API requests for getting Real-time Serie A Soccer League game schedules, along with the creation of our own set of requests of API through API gateway!


<h2>Environments and Technologies Used</h2>

  - Python
  - Amazon Elastic Container Service
  - Docker
  - RapidAPI
  - Github Codespaces for Environment
  - Terraform
  - IAM
  - Amazon Media Converter
  - S3 



  
<h2>Features</h2>  





<h2>Step by Step Instructions</h2>

***1. Set up IAM Roles***



***2. Repo and API configuration***

We will begin by setting up the environment and code that we will be utilizing. In this instance, we will use `Github Codespaces` to create a new workspace and do the commands from there. We will be setting up an account with RapidAPI for the Champions League Highlights.

You can set environemnt variables within the settings of Codespaces. 

The AWS credentials have the variables `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_DEFAULT_REGION` Respectively.


Finally, we will make sure our dependencies are installed properly.

```
pip install flask
pip install python-dotenv
pip install requests

```

We will proceed with installing the Docker CLI and Docker in Docker

```
curl -fsSL https://download.docker.com/linux/static/stable/x86_64/docker-20.10.9.tgz -o docker.tgz \
tar -xzf docker.tgz \
sudo mv docker/docker /usr/local/bin/ \
rm -rf docker docker.tgz
```

ctrl + p on Github Codespace > Add Dev Container Conf files > modify your active configuration > click on Docker (Docker-in-Docker)

![image](/assets/image1.png)


***(Optional): Local AWS CLI Setup***

NOTE: Keep in mind this is for a Linux environment, check the AWS documentation to install it in your supported OS.

   ```
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```
We then do `AWS configure` and enter our access and secret key along with the region. Output format set to JSON. With this command we will double check that our credentials are put in place for CLI:

```
aws sts get-caller-identity
```


***3. ***



***4. Creating the ECS Cluster***



***5. Creating a Task Definition***



 
***7. Configure API Gateway and Final Test***




***8. Cleanup***

We will be deleting the role and policies for clean up.

Run the Bash script on the repository to delete all of our resources created.

```
#!/bin/bash


```



<h2>Conclusion</h2>

In this project, I learned how to 
