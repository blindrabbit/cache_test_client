from flask import Flask
import psutil as ps
import mysql.connector
from mysql.connector import Error
import peewee as pw
from peewee import *
from datetime import datetime
import requests
import time
import os
import socket
from os.path import exists
import subprocess

def create_connection_db(database,user, password, host, port): 
    myDB = pw.MySQLDatabase(database,user=user,passwd=password, host=host,port=port)
    return myDB


db = create_connection_db('odb','root2', "root2", '10.50.1.122', 3306)


class BaseModel(Model):
    class Meta:
        database = db


class CacheNodesTest(BaseModel):
    id_cache_nodes_test = AutoField(primary_key=True)
    node_type = CharField(max_length=100) #client / proxy
    node_address = CharField(max_length=100) #IP xxx.xxx.xxx.xxx

    class Meta:
        table_name = 'cachenodestest'


class ComputeNodeData(BaseModel):
    id_compute_node_data = AutoField(primary_key=True)
    compute_node_data_date = DateTimeField()
    compute_node_data_cpu_percent = FloatField()
    compute_node_data_memory_percent = FloatField()
    
    class Meta:
        table_name = 'computenodedata'


class Services(BaseModel):
    id_service = AutoField(primary_key=True)
    name = CharField(max_length=100)
    token = CharField(max_length=100)
    creation_date = DateField()
    test_mode = BooleanField(default=False)

    class Meta:
        table_name = 'service'

db.create_tables([ComputeNodeData, CacheNodesTest])

def runcmd(cmd, verbose = False, *args, **kwargs):

    process = subprocess.Popen(
        cmd,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        text = True,
        shell = True
    )
    std_out, std_err = process.communicate()
    if verbose:
        print(std_out.strip(), std_err)
    pass


def is_testing_enable():
    service_id = 1
    try:
        is_testing = (Services
                                .select()
                                .where(Services.id_service == service_id))
        var = is_testing.dicts().get()
        if var['test_mode']:
            return True
        else:
            return False

    except Exception as error:
        print("error", error)
        return False


def hello():
    file_exists = exists('/etc/squid/squid.conf')
    if file_exists:
        cache_node = CacheNodesTest.create(
            node_type="proxy",
            node_address=socket.gethostbyname(socket.gethostname())
        )
    else:
        cache_node = CacheNodesTest.create(
            node_type="client",
            node_address=socket.gethostbyname(socket.gethostname())
        )
    return '<h1>Hello, World!!!</h1>'


def cache_test():

    while True:
        if is_testing_enable():
            try:
                cache_proxy = CacheNodesTest.select().where(CacheNodesTest.node_type == 'proxy').get()
                runcmd("wget -e use_proxy=yes -e http_proxy=http://"+cache_proxy.node_address+":3128 -r -np http://download.cirros-cloud.net/0.5.2/", verbose = True)
                return 'Execução do wget finalizada.'
            except Exception as error:
                return 'Erro na execução do wget.'
        else:
            print('Aguardando teste inicializar...')            
            time.sleep(1)


    return 'True'

var = hello()
print(var)

var2 = cache_test()
print(var2)