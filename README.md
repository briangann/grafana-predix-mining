# Grafana + PREDIX.IO

Getting Started with Grafana and Predix.io Time Series

This example will send random data to predix time series for verifying everything is working correctly
The primary example is to send data about GPU mining systems running Linux.

## Sample Dashboards

* sgminer
  * ethereum data
  * equihash data
  * cryptonight data
  * others

* rocm-smi
  * GPU core/memclock, temperature, fanspeed, power consumption

* ambient sensor data (cpu fanspeed, temperatures)

* cyberpower pdu metrics
* tripplite pdu metrics

* crypto coin values/difficulty
* wallet values

** Future: tracking hardware with Predix Asset Service
** Future: storing/retrieving configuration files for sgminer
** Future: storing/retrieving gpu bios files

## Prerequisites

sign up for predix.io
instructions to install cf
instructions to install uaac

##### Script this
how to create services (script this!)
   UAA
   TimeSeries
   Logstash - TODO

how to deploy grafana --nostart
bind services to grafana

####
run the init script

### Getting params for datasource

### Sending Data

### Viewing Data

### Backups
how to use wizzy to backup everything

### Restoration
how to use wizzy to restore everything
  - will need to wrap this in a flask app

### Users/Other OAUTH2 integrations

# TODO
need script to display the params for the grafana datasource
need to fix the plugin to conform to grafana v4
need script to shove sample data into new timeseries instance

predixts_ingest needs to be parameterized/have a config

make a new predixomatic to pull data from sgminer?

