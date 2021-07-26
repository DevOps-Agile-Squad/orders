# -*- mode: ruby -*-
# vi: set ft=ruby :

############################################################
# NYU: CSCI-GA.2820-001 DevOps and Agile Methodologies
# Instructor: John Rofrano
############################################################
Vagrant.configure(2) do |config|
    config.vm.box = "ubuntu/focal64"
    config.vm.hostname = "ubuntu"

    # set up network ip and port forwarding
    config.vm.network "forwarded_port", guest: 5000, host: 5000, host_ip: "127.0.0.1"
    config.vm.network "private_network", ip: "192.168.33.10"

    # Windows users need to change the permission of files and directories
    # so that nosetests runs without extra arguments.
    # Mac users can comment this next line out
    config.vm.synced_folder ".", "/vagrant", mount_options: ["dmode=775,fmode=664"]

    ######################################################################
    # Provider for VirtualBox
    ######################################################################
    config.vm.provider "virtualbox" do |vb|
      # Customize the amount of memory on the VM:
      vb.memory = "1024"
      vb.cpus = 1
      # Fixes some DNS issues on some networks
      vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
    end

    ############################################################
    # Provider for Docker on Intel or ARM (aarch64)
    ############################################################
    config.vm.provider :docker do |docker, override|
      override.vm.box = nil
      # Chromium driver does not work with ubuntu so we use debian
      override.vm.hostname = "debian"
      docker.image = "rofrano/vagrant-provider:debian"
      docker.remains_running = true
      docker.has_ssh = true
      docker.privileged = true
      docker.volumes = ["/sys/fs/cgroup:/sys/fs/cgroup:ro"]
      # Uncomment to force arm64 for testing images on Intel
      # docker.create_args = ["--platform=linux/arm64"]
    end

    ######################################################################
    # Copy some files to make developing easier
    ######################################################################

    # Copy your .gitconfig file so that your git credentials are correct
    if File.exists?(File.expand_path("~/.gitconfig"))
      config.vm.provision "file", source: "~/.gitconfig", destination: "~/.gitconfig"
    end

    # Copy your ssh keys for github so that your git credentials work
    if File.exists?(File.expand_path("~/.ssh/id_rsa"))
      config.vm.provision "file", source: "~/.ssh/id_rsa", destination: "~/.ssh/id_rsa"
    end

    # Copy your ~/.vimrc file so that vi looks the same
    if File.exists?(File.expand_path("~/.vimrc"))
      config.vm.provision "file", source: "~/.vimrc", destination: "~/.vimrc"
    end

    ############################################################
    # Create a Python 3 environment for development work
    ############################################################
    config.vm.provision "shell", inline: <<-SHELL
      echo "****************************************"
      echo " INSTALLING PYTHON 3 ENVIRONMENT..."
      echo "****************************************"
      # Install Python 3 and dev tools
      apt-get update
      apt-get install -y git tree wget vim python3-dev python3-pip python3-venv apt-transport-https python3-selenium
      apt-get upgrade python3

      # Need PostgreSQL development library to compile on arm64
      apt-get install -y libpq-dev

      # Install Chromium Driver
      apt-get install -y chromium-chromedriver

      # Create a Python3 Virtual Environment and Activate it in .profile
      sudo -H -u vagrant sh -c 'python3 -m venv ~/venv'
      sudo -H -u vagrant sh -c 'echo ". ~/venv/bin/activate" >> ~/.profile'

      # Install app dependencies in virtual environment as vagrant user
      sudo -H -u vagrant sh -c '. ~/venv/bin/activate && pip install -U pip && pip install wheel'
      sudo -H -u vagrant sh -c '. ~/venv/bin/activate && cd /vagrant && pip install -r requirements.txt'
    SHELL

    ######################################################################
    # Setup a Bluemix and Kubernetes environment
    ######################################################################
    config.vm.provision "shell", inline: <<-SHELL
      echo "\n************************************"
      echo " Installing IBM Cloud CLI..."
      echo "************************************\n"
      # Install IBM Cloud CLI as Vagrant user
      sudo -H -u vagrant sh -c '
      wget -O bluemix-cli.tar.gz https://clis.cloud.ibm.com/download/bluemix-cli/1.4.0/linux64 && \
      tar xzvf bluemix-cli.tar.gz && \
      cd Bluemix_CLI/ && \
      ./install && \
      cd .. && \
      rm -fr Bluemix_CLI/ bluemix-cli.tar.gz && \
      ibmcloud cf install
      '

      # Show completion instructions
      sudo -H -u vagrant sh -c "echo alias ic=/usr/local/bin/ibmcloud >> ~/.bash_aliases"
      echo "\n************************************"
      echo "If you have an IBM Cloud API key in ~/.bluemix/apiKey.json"
      echo "You can login with the following command:"
      echo "\n"
      echo "ibmcloud login -a https://cloud.ibm.com --apikey @~/.bluemix/apiKey.json -r us-south"
      echo "ibmcloud target --cf -o <your_org_here> -s dev"
      echo "\n************************************"
      # Show the GUI URL for Couch DB
      echo "\n"
      echo "CouchDB Admin GUI can be found at:\n"
      echo "http://127.0.0.1:5984/_utils"    
    SHELL

    ######################################################################
    # Add PostgreSQL docker container
    ######################################################################
    # docker run -d --name postgres -p 5432:5432 -v psql_data:/var/lib/postgresql/data postgres
    config.vm.provision :docker do |d|
      d.pull_images "postgres:alpine"
      d.run "postgres:alpine",
         args: "-d --name postgres -p 5432:5432 -v psql_data:/var/lib/postgresql/data -e POSTGRES_PASSWORD=postgres"
    end

    ######################################################################
    # Add a test database after Postgres is provisioned
    ######################################################################
    config.vm.provision "shell", inline: <<-SHELL
      # Create testdb database using postgres cli
      echo "Pausing for 60 seconds to allow PostgreSQL to initialize..."
      sleep 60
      echo "Creating test database"
      docker exec postgres psql -c "create database testdb;" -U postgres
      # Done
    SHELL

  end
