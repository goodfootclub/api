# Good Foot Club Api

Back end for the goodfoot.club project

**Master:**
[![Build Status](https://travis-ci.org/goodfootclub/api.svg?branch=master)](https://travis-ci.org/goodfootclub/api)
[![codecov](https://codecov.io/gh/goodfootclub/api/branch/master/graph/badge.svg)](https://codecov.io/gh/goodfootclub/api)

**Develop:**
[![Build Status](https://travis-ci.org/goodfootclub/api.svg?branch=develop)](https://travis-ci.org/goodfootclub/api)
[![codecov](https://codecov.io/gh/goodfootclub/api/branch/develop/graph/badge.svg)](https://codecov.io/gh/goodfootclub/api)

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
