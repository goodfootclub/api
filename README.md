# Good Foot Club Api

## Requirements

For quick dev environment setup Vagrant config with Ansible provisioning is
available. Only requirements in this case are [Vagrant] and [VirtualBox].
For non Vagrant installation use `config/site.yml` (Ansible playbook) as a
reference

## Installation

Clone the project:

```bash
git clone git@github.com:goodfootclub/api.git
cd api
```

With [Vagrant] and [VirtualBox] installed:

```bash
vagrant up
```

Development server will be available at http://localhost:8000/


[Vagrant]: https://www.vagrantup.com/
[VirtualBox]: https://www.virtualbox.org/
