import io
import os
import requests
import json
import yaml
from string import Template

from docker import Client
cli = Client(base_url='unix://var/run/docker.sock')

from flask import Flask
app = Flask(__name__)

API_URL = os.environ.get('URL')
API_TOKEN = os.environ.get('TOKEN') 


class Exception404(Exception):
    pass
    
@app.errorhandler(Exception404)
def not_found(error):
    return 'buildname not found', 404

def containerOr404(buildname):
  containers = cli.containers(all=True, filters={'label':'build='+buildname})
  if len(containers) != 1:
    raise Exception404()
  return containers[0]

def get_all_projects():
    data = requests.get(API_URL, headers={'PRIVATE-TOKEN': API_TOKEN}).json()
    projects = dict([(d['name'], d['web_url']) for d in data])
    return projects
    
def get_ci(url):
    ci = '/raw/master/.gitlab-ci.yml'
    r = requests.get(url+ci, headers={'PRIVATE-TOKEN': API_TOKEN}, allow_redirects=False)
    if r.status_code == 200:
      return yaml.load(r.text)

      
@app.route('/dc/ls')
def ls():
    containers = cli.containers(all=True, filters={'label':'build'})
    return json.dumps(dict([(c['Labels']['build'], c['Status']) for c in containers]), indent=4)  
    
  
@app.route('/dc/builds')
def builds():
    projects = get_all_projects()

    compat_projects = {}
    for name, url in projects.items():
      ci = get_ci(url)
      if ci:
        compat_projects[name] = url
    
    return json.dumps(compat_projects, indent=4)

    
@app.route('/dc/start/<buildname>')
def start(buildname):
    containers = cli.containers(all=True, filters={'label':'build='+buildname})
    if len(containers) > 0:
      return 'build already exists', 500
      
    projects = get_all_projects()  
    if not projects.get(buildname, None):
      return 'build does not exists', 404
      
    project_url = projects.get(buildname)
    ci = get_ci(project_url)
    if not ci:
      return 'build is not a ci', 403    

    command = Template(ci['build']['script'])
    container = cli.create_container(image=ci['image'], command=command.safe_substitute(ci['variables']), labels={'build':buildname})
    
    if container['Warnings']:
      return container['Id']+' failed to create', 500
    cli.start(container['Id'])
    return container['Id'] 

    
@app.route('/dc/stop/<buildname>')
def stop(buildname):
    container = containerOr404(buildname)
    cli.stop(container['Id'])
    cli.remove_container(container['Id'])
    return container['Id']   


@app.route('/dc/status/<buildname>')
def status(buildname):
    container = containerOr404(buildname)
    return container['Status']


@app.route('/marvel')
def marvel():
    return 'Stan Lee not found!', 404 

        
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
