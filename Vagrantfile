#     -*- mode: ruby -*-
#     vi: set ft=ruby :

Vagrant.configure("2") do |config|
    machines = [
      "es1.local",
      "es2.local",
      "es3.local",
      "ms1.local",
      "ms2.local",
      "dir1.local",
      "dir2.local",
      "backupserver.local"
    ]
  
    ssh_pub_key = File.readlines("#{Dir.home}/.ssh/id_ed25519.pub").first.strip
  
    machines.each_with_index do |machine_name, index|
      config.vm.define machine_name do |machine|
        config.vm.provision "shell" do |s|
          s.inline = <<-SHELL
            echo #{ssh_pub_key} >> /home/vagrant/.ssh/authorized_keys
            echo #{ssh_pub_key} >> /root/.ssh/authorized_keys
          SHELL
        end

        machine.vm.box = "fedora/42-cloud-base"
        machine.vm.box_url = "https://mirror.karneval.cz/pub/linux/fedora/linux/releases/42/Cloud/x86_64/images/Fedora-Cloud-Base-Vagrant-libvirt-42-1.1.x86_64.vagrant.libvirt.box"
        machine.vm.hostname = machine_name
        machine.vm.provider "libvirt" do |libvirt|
            libvirt.cpus = 2
            if machine_name.start_with?("es")
                libvirt.memory = 4096
            else
                libvirt.memory = 2048
            end
        end
      end
    end
  end
  
  
  
  
  
  
  


