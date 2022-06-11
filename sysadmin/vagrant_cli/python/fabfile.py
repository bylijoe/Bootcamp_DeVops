from fabric.api import *
import fabric

fabric.state.output['running'] = False
fabric.state.output['stdout'] = False

env.use_shell = False
env.skip_bad_hosts = True

env.hosts=['adminjgp@172.16.5.12']

def host_version():
    run('dis version', pty=False)

def hello():
	print("Hello world!")
