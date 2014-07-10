#!/usr/bin/env python

# by fishcried(wangtq@neunn.com) 2014.07.03

import urllib2
import sys
import json
import argparse
import logging
import logging.handlers
import os
from xml.dom import minidom

log = logging.getLogger(__name__)

def requestjson(uri,values):
    data = json.dumps(values)

    log.debug("Send data: %s", data)

    req = urllib2.Request(uri, data, {'Content-type': 'application/json-rpc'})
    response = urllib2.urlopen(req, data)
    data_get = response.read()
    output = json.loads(data_get)

    log.debug("Receive data: %s", output)

    try:
        msg = output['result']
    except:
        msg = output['error']['data']
        quit()
    
    return output

def login(uri, usr, passwd):
    data = {'jsonrpc':'2.0',
            'method':'user.login',
            'params':{
                'user':usr,
                'password':passwd
                },
            'id':'0'
            }
    auth =  requestjson(uri, data)['result']
    log.info("Log in %s by (%s: %s)success",uri, usr, passwd)
    return auth

def template_get(name, uri, auth):
    data = {'jsonrpc':'2.0',
            'method':'template.get',
            'params':{
                'output':"templateid",
                'filter':{'host':name}
                },
            'auth':auth,
            'id':'1'
            }
    output = requestjson(uri,data)

    try:
        tid = output['result'][0]['templateid']
    except:
        log.error("Get  template %s failed",name)
        return None
    else:
        log.info("Get  template %s success",name)
        return tid

def template_delete(tid, uri, auth):
    data = {'jsonrpc':'2.0',
            'method':'template.delete',
            'params':[
                tid,
                ],
            'auth':auth,
            'id':'1'
            }
    output = requestjson(uri,data)

    try:
        tid = output['result']['templateids'][0]
    except:
        log.error("Delete  template %s failed", tid)
        return None
    else:
        log.info("Delete  template %s success", tid)
        return tid

def host_get(hostname, uri, auth):
    host_list = []
    data = {'jsonrpc':'2.0',
            'method':'host.get',
            'params':{
                'output':["hostid","host"],
                'filter':{'host':hostname}
                },
            'auth':auth,
            'id':'1'
            }
    output = requestjson(uri,data)
    try:
        hid = output['result'][0]['hostid']
    except:
        log.error("Get  host %s failed", hostname)
        return None
    else:
        log.info("Get  host %s success", hostname)
        return hid

def host_delete(hid, uri, auth):
    data = {'jsonrpc':'2.0',
            'method':'host.delete',
            'params':[
                hid,
                ],
            'auth':auth,
            'id':'1'
            }
    output = requestjson(uri,data)

    try:
        hid = output["result"]["hostids"][0]
        log.info("Delete %s success", hid)
    except:
        log.info("Delete %s failed", hid)
        return None
    finally:
        return hid

def host_create(uri, auth, hostname, ip, groupid, templateid):
    if ip and  groupid and templateid:
        data = {'jsonrpc':'2.0',
                'method':'host.create',
                'params':{
                    "host":hostname,
                    "interfaces":[{
                        "type":1,
                        "main":1,
                        "useip":1,
                        "ip": ip,
                        "dns":"",
                        "port":"10050"
                        }],
                    "groups": [
                        { "groupid": str(groupid) }
                        ],
                    "templates": [
                        {
                            "templateid": str(templateid),
                            }
                        ],
                    },
                'auth':auth,
                'id':'3'
                }
        output = requestjson(uri,data)

        res = output['result']
        hid = res['hostids']
        try:
            hid = res['hostids']
        except:
            log.error("Create host %s failed" ,hostname)
            return None
        else:
            log.info("Create host %s success" ,hostname)
            return hid

def hgroup_get(uri, auth, groupname):
    if not groupname:
        log.error("groupname is Null")
        return None

    data = {'jsonrpc':'2.0',
            'method':'hostgroup.get',
            'params':{
                "output":"extend",
                "filter": {
                    "name": [groupname]
                    },
                },
            'auth':auth,
            'id':'4'
            }
    output = requestjson(uri,data)

    try:
        groupids = output['result'][0]['groupid']
    except:
        log.error("Get hostgroup %s failed",groupname)
        return None
    else:
        log.info("Get hostgroup %s success",groupname)
        return groupids

def hgroup_create(uri, auth, groupname):
    if not groupname:
        log.error("groupname is Null")
        return None

    data = {'jsonrpc':'2.0',
            'method':'hostgroup.create',
            'params':{
                "name":groupname
                },
            'auth':auth,
            'id':'4'
            }
    output = requestjson(uri,data)

    res = output['result']

    try:
        groupid = res['groupids'][0]
    except:
        log.error("Create hostgroup %s failed", groupname)
        return None
    else:
        log.info("Create hostgroup %s success", groupname)
        return groupid

def get_host_graphs(hostid, uri, auth):
    data = {'jsonrpc':'2.0',
            'method':'graph.get',
            'params':{
                "output":"extend",
                "hostids":hostid,
                "sortfiled":"name",
                },
            'auth':auth,
            'id':'5'
            }
    output = requestjson(uri,data)
    tmp = sorted(output['result'],key= lambda x:x['name'])
    res = tmp

    gids = []
    for l in res:
        gids.append(l['graphid'])

    return gids

def screen_get(name, uri, auth):
    data = {'jsonrpc':'2.0',
            'method':'screen.get',
            'params':{
                "output":"extend",
                },
            'auth':auth,
            'id':'5'
            }
    output = requestjson(uri,data)
    res = output['result']

    for screen in res:
        if screen['name'] == name:
            return screen['screenid']

    return None

def screen_delete(sid, uri, auth):
    data = {'jsonrpc':'2.0',
            'method':'screen.delete',
            'params':[
                sid,
                ],
            'auth':auth,
            'id':'5'
            }
    output = requestjson(uri,data)
    res = output['result']
    log.info("Delete screen %s success", sid)

    try:
        id = res['screenids'][0]
    except:
        log.error("Delete %s failed", sid)
        return None
    finally:
        log.info("Delete %s success", sid)
        return id

def screen_create(uri, auth, screen_name, graphids, columns):
    columns = int(columns)
    if len(graphids) % columns == 0:
        vsize = len(graphids) / columns
    else:
        vsize = (len(graphids)/columns) + 1

    data = {'jsonrpc':'2.0',
            'method':'screen.create',
            'params':[{
                "name":screen_name,
                "hsize":columns,
                "vsize":vsize,
                "screenitems":[]
                }],
            'auth':auth,
            'id':6
            }

    x = 0
    y = 0
    index = 0
    for i in graphids:
        x = index % columns
        y = index / columns
        
        data['params'][0]['screenitems'].append(
                {"resourcetype": 0,
                    "resourceid":  i,
                    "rowspan": 0,
                    "colspan": 0,
                    "x": x,
                    "y": y,
                    })
        index = index + 1

    try:
        output = requestjson(uri, data)
        id  = output['result']['screenids']
    except Exception as e:
        log.error("Create screen %s failed",screen_name)
        return None
    finally:
        log.info("Create screen %s Success",screen_name)
        return id

def init_log(args):
    if args.quie:
        level = logging.WARN
    if args.debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    log.setLevel(level)
    if not os.path.exists("log"):
        os.mkdir("log")
    fh = logging.FileHandler(os.path.join('log','add_host.log'))
    fh.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    log.addHandler(fh)
    log.addHandler(ch)

def config_import(uri, auth, file):
    with open(file, 'r') as fp:
        content = fp.read()

    data = {'jsonrpc':'2.0',
            'method':'configuration.import',
            'params':{
                "format": "xml",
                "rules": {
                    "hosts" : {
                        "createMissing": "false",
                        "updateExisting": "false",
                        },
                    "appplications" : {
                        "createMissing": "true",
                        "updateExisting": "true",
                        },
                    "graphs" : {
                        "createMissing": "true",
                        "updateExisting":"true",
                        },
                    "groups" : {
                        "createMissing": "true",
                        "updateExisting":"true",
                        },
                    "items" : {
                        "createMissing": "true",
                        "updateExisting":"true",
                        },
                    "templates" : {
                        "createMissing": "true",
                        "updateExisting":"true",
                        },
                    },
                "source":str(content)
                },
            'auth':auth,
            'id':'4'
            }

    output = requestjson(uri,data)
    res = output['result']

    if res:
        log.info("Import config %s success" ,file)
    else:
        log.error("Import config %s failed" ,file)
    return

def main():
    user = 'Admin'
    passwd  = 'zabbix'

    uri = 'http://' + server + '/zabbix/api_jsonrpc.php'
    auth = login(uri, user, passwd)

    # add hostgroup
    gid = hgroup_get(uri, auth, hostgroup)
    if not gid:
        gid = hgroup_create(uri, auth, hostgroup)

    tid = template_get(template_name, uri, auth)
    if tid:
        log.warning("Template %s exist, delete it", template_name)
        template_delete(tid, uri, auth)

    # import template
    config_import(uri, auth, templatefile)
    tid = template_get(template_name, uri, auth)


    # 3 create screen for each hosts
    with open(hostsfile, 'r') as fp:
        lines = fp.readlines()

        lineno = 1
        for line in  lines:
            lineno += 1

            # skip comment line or empty line
            content = line.lstrip()
            if len(content) == 0 or content[0] == '#':
                continue

            name, ip = tuple(line.split())
            if not name or not ip:
                log.warning("Bad lin[%d] in %s", lineno -1, hostsfile)
                continue

            log.debug("Create host %s %s", name,ip)
            hid = host_get(name, uri, auth)
            if hid:
                log.warning("Host %s exists, delete it", name)
                host_delete(hid, uri, auth)
            hid = host_create(uri,auth, name, ip, gid, tid);
            if hid:
                gid_list = get_host_graphs(hid, uri, auth)
                log.debug("Graphs of host %s - %s", name, gid_list)
                sid = screen_get('screen-'+name, uri, auth)
                if sid:
                    log.info("Should delete %s (%s)", 'screen-'+name, sid)
                    screen_delete(sid, uri, auth)
                screen_create(uri, auth, 'screen-' + name, gid_list, columns)
        
        log.info("Finish")

def get_template_name(file):

    dom = minidom.parse(file)
    root = dom.documentElement

    template = root.getElementsByTagName("template")
    t_name = ""
    for t in template:
        tt = t.getElementsByTagName("name")
        if tt: 
            t_name = tt[0].childNodes[0].nodeValue
            log.info("Get template name %s from %s", t_name, file)
            break
    return t_name

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Auto config zabbix server. \
            1 auto add hosts to zabbix server.\
            2 applay the template to each agents.  \
            3 auto create screen(\"screen-$hostname\" for each agent.")
    parser.add_argument('-f', '--hostfile', dest='hostsfile', type=str, help="file contain hosts' name and ip address", required=True)
    parser.add_argument('-T', '--template', dest='templatefile', type=str, default=os.path.join("conf","template.xml"), help="templates xml file", required=False)
    parser.add_argument('-c', '--columns', dest='columns', default=3, type=int, help="number of columns in the screen", required=False)
    parser.add_argument('-S', '--ip', dest='server', type=str, help="zabbix server ip", required=True)
    parser.add_argument('-g', '--groupname', dest='groupname', default="yhr_group", type=str, help="hostgroup name", required=False)
    parser.add_argument("-d", "--debug", help="Display debug messages", required=False)
    parser.add_argument("-q", "--quie", help="Display only error or warn messages", required=False)


    args = parser.parse_args()

    init_log(args)

    log.debug("args:%s", args)

    server = args.server
    hostsfile = args.hostsfile
    hostgroup = args.groupname
    columns = args.columns
    templatefile = args.templatefile
    template_name = get_template_name(templatefile)

    main()
