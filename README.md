Cuz Docker Commander sounded cooler.

### Setup
    $ source activate
    $ builder_build
    $ gitlab_up 192.168.1.3
    
Get your token from http://192.168.1.3:10080/profile/account
    
    $ dc_up http://192.168.1.3:10080/api/v3/projects 3sBLwmXgcjyFm-vSMxnvdc_up
    
Setup some projects and add a .gitlab-ci.yml file


### Usage
    $ curl http://192.168.1.3:5000/dc/ls
    $ curl http://192.168.1.3:5000/dc/builds
    $ curl http://192.168.1.3:5000/dc/start/foo
    $ curl http://192.168.1.3:5000/dc/status/foo
    $ curl http://192.168.1.3:5000/dc/stop/foo
