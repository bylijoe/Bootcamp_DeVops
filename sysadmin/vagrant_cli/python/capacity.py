import datetime
import time
from typing import FrozenSet
import requests  
import json
import sys
from elasticsearch import Elasticsearch

# Global Variables

# Prometheus sources
PROMETHEUS = 'http://master-prometheus-acme.pro.acme.internal'

# Elastic server & index prefix
esclo = Elasticsearch([{'host': 'elsticsearch-server-acme.internal', 'port': 9200}])
index_prefix="capacity-planning"

# Set time ranges
duration=14
today = datetime.datetime.today()
first_day = today - datetime.timedelta(days=duration)
start_epoch=str(int(first_day.timestamp()))
end_epoch=str(int(today.timestamp()))
step='900'
debug=False


def get_cpu_idle(p, s, t):
      query = f'100 - (avg(rate(node_cpu_seconds_total{{team="{t}",project="{p}",mode="idle",service=~"{s}"}}[{duration}d])) by (service)) *100'
      if debug: 
            print(query)
            print(prometheus)
      response =requests.get(prometheus + '/api/v1/query', params={'query': query }) 
      return float(response.json()['data']['result'][0]['value'][1])


def get_avg_load_average(p, s, t):
      metric = f'(node_load5{{team="{t}",project="{p}",service=~"{s}"}}[{duration}d])'
      query = f'avg(avg_over_time({metric}))'
      if debug: 
            print(query)
            print(prometheus)
      response =requests.get(prometheus + '/api/v1/query', params={'query': query }) 
      if debug:  print(response.text)
      return float(response.json()['data']['result'][0]['value'][1])

def get_max_load_average(p, s, t):
      metric = f'(node_load5{{team="{t}",project="{p}",service=~"{s}"}}[{duration}d])'
      query = f'avg(max_over_time({metric}))'
      if debug: 
            print(query)
            print(prometheus)
      response =requests.get(prometheus + '/api/v1/query', params={'query': query }) 
      if debug: print(response.text)
      return float(response.json()['data']['result'][0]['value'][1])

def get_memory_usage(p, s, t):
      totalMem = f'(node_memory_MemTotal_bytes{{team="{t}",project="{p}",service=~"{s}"}}[{duration}d])'
      freeMem =  f'(node_memory_MemFree_bytes{{team="{t}",project="{p}",service=~"{s}"}}[{duration}d])'
      query = f'avg(avg_over_time{totalMem})-avg(avg_over_time{freeMem})'
      if debug: 
            print(query)
            print(prometheus)
      response =requests.get(prometheus + '/api/v1/query', params={'query': query }) 
      if debug:  print(response.text)
      return float(response.json()['data']['result'][0]['value'][1])


def tx_bytes(p, s, t):
      txBytes = f'(node_network_transmit_bytes_total{{device!~"lo.*",team="{t}",project="{p}",service=~"{s}"}}[{duration}d])'
      query = f'avg(rate{txBytes})'
      if debug: 
            print(query)
            print(prometheus)
      response =requests.get(prometheus + '/api/v1/query', params={'query': query }) 
      if debug:  print(response.text)
      return float(response.json()['data']['result'][0]['value'][1])

def rx_bytes(p, s, t):
      rxBytes = f'(node_network_receive_bytes_total{{device!~"lo.*",team="{t}",project="{p}",service=~"{s}"}}[{duration}d])'
      query = f'avg(rate{rxBytes})'
      if debug: 
            print(query)
            print(prometheus)
      response =requests.get(prometheus + '/api/v1/query', params={'query': query }) 
      if debug:  print(response.text)
      return float(response.json()['data']['result'][0]['value'][1])

def filesystem_free_bytes(p, s, t):
      excludedMountPoints = ['/run.*', '/boot', '/tmp', '/', '/var']
      exclusion = ''
      for mp in excludedMountPoints:
            exclusion += f'mountpoint!~"{mp}",'
      fs_free = f'(node_filesystem_free_bytes{{{exclusion} team="{t}",project="{p}",service=~"{s}"}}[{duration}d])'
      query = f'avg(avg_over_time{fs_free})'
      if debug: 
            print(query)
            print(prometheus)
      response =requests.get(prometheus + '/api/v1/query', params={'query': query }) 
      if debug:  print(response.text)
      if len(response.json()['data']['result'])>0:
            return float(response.json()['data']['result'][0]['value'][1])
      else:
            return 0.0

def read_iops(p, s, t):
      readIops = f'(node_disk_reads_completed_total{{device=~"[a-z]*[a-z]",team="{t}",project="{p}",service=~"{s}"}}[{duration}d])'
      query = f'avg(rate{readIops})'
      if debug: 
            print(query)
            print(prometheus)
      response =requests.get(prometheus + '/api/v1/query', params={'query': query }) 
      if debug:  print(response.text)
      return float(response.json()['data']['result'][0]['value'][1])
  
def write_iops(p, s, t):
      writeIops = f'(node_disk_writes_completed_total{{device=~"[a-z]*[a-z]",team="{t}",project="{p}",service=~"{s}"}}[{duration}d])'
      query = f'avg(rate{writeIops})'
      if debug: 
            print(query)
            print(prometheus)
      response =requests.get(prometheus + '/api/v1/query', params={'query': query }) 
      if debug:  print(response.text)
      return float(response.json()['data']['result'][0]['value'][1])

def getPreviousMonthDoc(p,s,t):
      #p --> project, s --> service, t --> team
      date_i = (datetime.datetime.utcnow()-datetime.timedelta(days=16)).strftime('%Y-%m-%dT%H:%M:%S.%f')
      date_f = (datetime.datetime.utcnow()-datetime.timedelta(days=14)).strftime('%Y-%m-%dT%H:%M:%S.%f')
      prev_month = esclo.search(index=f"{index_prefix}-*", body={
        "query": {
      "bool": {
      "filter": [
        {
          "bool": {"filter": [{"bool": {"should": [{"match_phrase": {"team.keyword": f"{t}"}}]}},
        {
              "bool": {"should": [{"match_phrase": {"service.keyword": f"{s}"}}]}},
        {
              "bool": {"should": [{"match_phrase": {"project.keyword": f"{p}"}}]}},
        {
          "range": {"timestamp": {"gte": f"{date_i}Z","lte": f"{date_f}Z"}}}]}}]}}})
      
      #print(p,s,t)
      if len(prev_month['hits']['hits'])>0:
            return prev_month['hits']['hits'][0]['_source']
      else:
            j = {
            'avg_load': 0,
            'max_load': 0,
            'cpu': 0,
            'memory': 0,
            'net_rx': 0,
            'net_tx': 0,
            'fs_free': 0,
            'iops_r': 0,
            'iops_w': 0}
            return j
      
def calculateTrend(curr, prev):
      #print(curr, prev)
      try:
            #print(((curr/prev)-1)*100)
            return (((curr/prev)-1)*100)
      except:
            return 0

def buildDoc(p,s,t):
      if debug:
            print(prometheus)
      prev_month=getPreviousMonthDoc(p,s,t)
      avg_load=get_avg_load_average(p, s, t)
      max_load=get_max_load_average(p, s, t)
      cpu=get_cpu_idle(p, s, t)
      memory=get_memory_usage(p, s, t)
      net_rx=rx_bytes(p, s, t)
      net_tx=tx_bytes(p, s, t)
      fs_free=filesystem_free_bytes(p, s, t)
      iops_r=read_iops(p, s, t)
      iops_w=write_iops(p, s, t)

      print('all values gathered')

      j = {
            'timestamp': (datetime.datetime.utcnow()).strftime('%Y-%m-%dT%H:%M:%S.%f'),
            'service': f'{s}',
            'project': f'{p}',
            'team': f'{t}',
            'avg_load': avg_load,
            'max_load': max_load,
            'cpu': cpu,
            'memory': memory,
            'net_rx': net_rx,
            'net_tx': net_tx,
            'fs_free': fs_free,
            'iops_r': iops_r,
            'iops_w': iops_w,
            'trend_avg_load': calculateTrend(avg_load,prev_month['avg_load']),
            'trend_max_load': calculateTrend(max_load,prev_month['max_load']),
            'trend_cpu': calculateTrend(cpu,prev_month['cpu']),
            'trend_memory': calculateTrend(memory,prev_month['memory']),
            'trend_net_rx': calculateTrend(net_rx,prev_month['net_rx']),
            'trend_net_tx': calculateTrend(net_tx,prev_month['net_tx']),
            'trend_fs_free': calculateTrend(fs_free,prev_month['fs_free']),
            'trend_iops_r': calculateTrend(iops_r,prev_month['iops_r']),
            'trend_iops_w': calculateTrend(iops_w,prev_month['iops_w'])
      }      
      
      return j



def main():
      global prometheus
      print('Setting default PROMETHEUS server')
      prometheus=PROMETHEUS

      index = f"{index_prefix}-{datetime.datetime.now().strftime('%Y')}"

      with open('services.json') as f:
        services= json.load(f)

      for t in services['teams']:
            print(t['team'])                  

            for p in t['projects']:
                  for s in p['services']:
                        project=p['name']
                        service=s
                        team=t['team']
                        print(team,project,service,prometheus)
                        doc=buildDoc(project, service, team)

                        # save data on elasticsearch
                        print('Saving data on elasticsearch')
                        esclo.index(index=index,body=doc)

                        # curl -X GET elsticsearch-server-acme.internal:9200/capacity-planning-2021/_search?pretty
                  


# Start program
if __name__ == "__main__":
    sys.exit(main())
