# -*- mode: ruby -*-
# vi: set ft=ruby :


Vagrant.configure("2") do |config|

  config.vm.box = "ubuntu/trusty64"
  config.vm.network "forwarded_port", guest: 80, host: 8000   # Nginx
  config.vm.network "forwarded_port", guest: 8001, host: 8001 # Supervisor
  config.vm.network "forwarded_port", guest: 8002, host: 8002 # Logs

  config.vm.provider :virtualbox do |vb|
    vb.memory = "1024"
    vb.name = "goodfootclub"
  end

  config.vm.synced_folder ".", "/vagrant", disabled: true
  config.vm.synced_folder ".", "/home/vagrant/api"
  config.vm.synced_folder "../web/dist", "/home/vagrant/web/dist", create: true

  config.vm.provision "ansible_local", run: "always" do |ansible|
    ansible.provisioning_path = "/home/vagrant/api"
    ansible.playbook = "config/site.yml"
    # Uncomment the line below to get debug output
    # ansible.verbose = "vv"
  end
end
