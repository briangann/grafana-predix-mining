#!/usr/bin/env python
"""
Bootstrap Predix TimeSeries Service
"""
import os
import logging
import json
import sys
import argparse
from pprint import pprint
# https://pypi.python.org/pypi/cloudfoundry-client/0.0.19
from cloudfoundry_client.client import CloudFoundryClient

global logger


def login(username, password):
    """
    get a client connection
    """
    target_endpoint = 'https://api.system.aws-usw02-pr.ice.predix.io'
    proxy = dict(
        http=os.environ.get('http_proxy', ''),
        https=os.environ.get('https_proxy', ''))
    cf_client = CloudFoundryClient(
        target_endpoint,
        proxy=proxy,
        skip_verification=True)
    cf_client.init_with_user_credentials(username, password)
    return cf_client


def show_apps(cf_client):
    """
    lists apps
    """
    for app in cf_client.apps:
        # pprint(app)
        app_name = app['entity']['name']
        logger.debug('Application: %s', app_name)


def get_application_guid(cf_client, space_guid, application_name):
    """
    get app guid
    """
    for app in cf_client.apps:
        if app['entity']['name'] == application_name and app['entity']['space_guid'] == space_guid:
            #pprint(app)
            return app['metadata']['guid']
    return None


def get_application_uri(cf_client, space_guid, application_name):
    """
    get app uri
    """
    for app in cf_client.apps:
        if app['entity']['name'] == application_name and app['entity']['space_guid'] == space_guid:
            #pprint(app)
            env = cf_client.apps.get_env(app['metadata']['guid'])
            uri = env['application_env_json']['VCAP_APPLICATION']['application_uris'][0]
            return uri
    return None


def get_trusted_issuer_id(cf_client, space_guid, application_name):
    for app in cf_client.apps:
        if app['entity']['name'] == application_name and app['entity']['space_guid'] == space_guid:
            issuerID = None
            try:
                #pprint(app)
                env = cf_client.apps.get_env(app['metadata']['guid'])
                #pprint(app['metadata']['guid'])
                # pprint(env['system_env_json']['VCAP_SERVICES']['predix-uaa'][0])
                # this can fail is the uaa has not been created and bound
                #pprint(env)
                issuerID = env['system_env_json']['VCAP_SERVICES']['predix-uaa'][0]['credentials']['issuerId']  # noqa
            except:
                pass
            return issuerID


def get_uaa_instance_uri(cf_client, space_guid, application_name):
    for app in cf_client.apps:
        if app['entity']['name'] == application_name and app['entity']['space_guid'] == space_guid:
            uaa_uri = None
            try:
                env = cf_client.apps.get_env(app['metadata']['guid'])
                print env
                # pprint(env['system_env_json']['VCAP_SERVICES']['predix-uaa'][0])
                uaa_uri = env['system_env_json']['VCAP_SERVICES']['predix-uaa'][0]['credentials']['uri']  # noqa
            except:
                pass
            return uaa_uri


def get_timeseries_zone_id(cf_client, application_name):
    for app in cf_client.apps:
        if app['entity']['name'] == application_name:
            env = cf_client.apps.get_env(app['metadata']['guid'])
            # pprint(env['system_env_json']['VCAP_SERVICES']['predix-timeseries'][0])
            zone_id = env['system_env_json']['VCAP_SERVICES']['predix-timeseries'][0]['credentials']['ingest']['zone-http-header-value']  # noqa
            return zone_id


def get_timeseries_service_config(cf_client, application_name):
    for app in cf_client.apps:
        if app['entity']['name'] == application_name:
            env = cf_client.apps.get_env(app['metadata']['guid'])
            service_config = env['system_env_json']['VCAP_SERVICES']['predix-timeseries'][0]  # noqa
            return service_config


def show_plans(cf_client):
    """
    show plans
    """
    for plan in cf_client.service_plans:
        pprint(plan)


def show_services(cf_client):
    """
    show services
    """
    for service in cf_client.services:
        #pprint(service)
        service_name = service['entity']['label']
        logger.debug('Service Name: %s', service_name)


def get_service_guid(cf_client, service_name):
    """
    get service guid
    """
    for service in cf_client.services:
        #pprint(service)
        if service['entity']['label'] == service_name:
            return service['metadata']['guid']


def get_service_plan_guid(cf_client, service_guid, plan_name):
    """
    get service plan guid
    """
    for plan in cf_client.service_plans:
        # pprint(service)
        if plan['entity']['service_guid'] == service_guid:
            if plan['entity']['name'] == plan_name:
                return plan['metadata']['guid']


def show_service_instances(cf_client):
    """
    show service instances
    """
    for service_instance in cf_client.service_instances:
        # pprint(service_instance)
        service_instance_name = service_instance['entity']['name']
        logger.debug('Service Instance: %s', service_instance_name)


def get_service_instance_guid(cf_client, name):
    """
    get service instance guid
    """
    for service_instance in cf_client.service_instances:
        if service_instance['entity']['name'] == name:
            try:
                return service_instance['metadata']['guid']
            except:
                return None


def show_spaces(cf_client):
    """
    show spaces
    """
    for space in cf_client.spaces:
        pprint(space)


def get_space_guid(cf_client, space_name):
    """
    get space guid for named space
    """
    for space in cf_client.spaces:
        if space['entity']['name'] == space_name:
            return space['metadata']['guid']
    return None

def space_exists(cf_client, space_name):
    """
    check if space exists
    """
    for space in cf_client.spaces:
        if space['entity']['name'] == space_name:
            return True
    return False


def create_space(c, space_name):
    command = 'cf create-space {}'.format(space_name)
    os.system(command)


def setup_logger():
    global logger
    # Setup our logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    channel = logging.StreamHandler(sys.stdout)
    channel.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        fmt='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')  # noqa
    channel.setFormatter(formatter)
    logger.addHandler(channel)

def push_grafana_app(client, app_name):
    # cd to cf-grafana and do a cf push
    os.chdir('cf-grafana')
    os.system('cf push --no-start {} -f manifest.yml'.format(app_name))

def start_grafana_app(client, app_name):
    os.system('cf start {}'.format(app_name))

def create_and_bind_timeseries(c, app_name):
    logger.debug("Creating new time series service")
    TIMESERIES_NAME = 'grafana-timeseries'
    ts_creation_params = {
        'trustedIssuerIds': [uaa_trusted_issuer_id]
    }
    try:
        logger.debug("Creating Time Series service instance")
        timeseries_instance = c.service_instances.create(
            space_guid,
            TIMESERIES_NAME,
            timeseries_service_plan_guid,
            ts_creation_params)
        timeseries_instance_guid = timeseries_instance['metadata']['guid']
        logger.debug("Binding to app")
        bind_timeseries = c.service_bindings.create(
            app_guid,
            timeseries_instance_guid)
    except:
        pass

def main():
    """
    Creates Predix services
    """
    parser = argparse.ArgumentParser(description='Predix Grafana Bootstrapper.')
    parser.add_argument('-u', '--username', required=True,
                        action='store', dest="predix_username",
                        help='Usename for API login')
    parser.add_argument('-p', '--password', required=True,
                        action='store', dest="predix_password",
                        help='Password for API login')
    parser.add_argument('-a', '--admin-client-secret',
                        action='store', dest="predix_uaa_admin_password",
                        default='replaceme',
                        help='Password for UAA admin account, default: replaceme')
    parser.add_argument('-c', '--grafana-client-secret',
                        action='store', dest="predix_uaa_client_password",
                        default='iseegraphs',
                        help='Password for UAA client account, default: iseegraphs')
    parser.add_argument('-i', '--ingestion-secret',
                        action='store', dest="predix_uaa_ingest_password",
                        default='ingestomatic',
                        help='Password for UAA client account, default: ingestomatic')
    parser.add_argument('-s', '--space',
                        action='store',
                        dest="predix_org_space",
                        default='grafana',
                        help='Organization space, default: grafana')

    args = parser.parse_args()

    # Setup our logger
    setup_logger()

    # login to cloud foundry
    c = login(args.predix_username, args.predix_password)

    if not space_exists(c, args.predix_org_space):
        create_space(c, args.predix_org_space)

    # get the guid
    space_guid = get_space_guid(c, args.predix_org_space)
    if space_guid is None:
        print "Failed to get space guid"
        exit(-1)

    # target the space
    command = 'cf target -s {}'.format(args.predix_org_space)
    os.system(command)

    logger.debug('Space GUID: %s', space_guid)

    #if not service_exists(c, 'predix-uaa'):
    #    create_uaa_service(c, 'predix-uaa')

    uaa_service_guid = get_service_guid(c, 'predix-uaa')
    logger.debug('Predix UAA Service GUID: %s', uaa_service_guid)
    uaa_service_plan_guid = get_service_plan_guid(c, uaa_service_guid, 'Free')
    logger.debug('Predix UAA Service Plan GUID: %s', uaa_service_plan_guid)

    # Steps for UAA/Predix/App creation
    # 1) Check if there is a service named "grafana-uaa"
    #     If not, create it with CF
    # 2) Check if there is an app bound to the UAA instance
    #     If not, CF push our API code, with no-start option
    #           cf push -nostart
    #           cf bind-service grafana grafana-uaa
    #
    UAA_NAME = 'grafana-uaa'
    APP_NAME = 'grafana'

    # Check if there is a grafana app already pushed to the space
    app_guid = get_application_guid(c, space_guid, APP_NAME)
    pushed_app = False
    if app_guid is None:
        # need to push our app first
        push_grafana_app(c, APP_NAME)
        pushed_app = True
        app_guid = get_application_guid(c, space_guid, APP_NAME)

    logger.debug('APP GUID: %s', app_guid)
    # get the application_uri for later
    application_uri = get_application_uri(c, space_guid, APP_NAME)
    # get the trustedIssuerId from the bound app
    uaa_trusted_issuer_id = get_trusted_issuer_id(c, space_guid, APP_NAME)
    logger.debug('UAA Trusted Issuer ID: %s', uaa_trusted_issuer_id)
    # Create our UAA Service
    creation_params = {
        'adminClientSecret': args.predix_uaa_admin_password
        }
    if uaa_trusted_issuer_id is None:
        try:
            logger.debug("No UAA found, creating one")
            uaa_instance = c.service_instances.create(
                space_guid,
                UAA_NAME,
                uaa_service_plan_guid,
                creation_params)
            uaa_instance_guid = uaa_instance['metadata']['guid']
        except:
            logger.debug("Failed to create UAA Instance, checking if existing service is not bound")
            os.system('cf bind-service grafana grafana-uaa')
            uaa_instance_guid = get_service_instance_guid(c, UAA_NAME)
            if uaa_instance_guid is None:
                print "not bound, something failed"
                exit(-1)
    else:
        uaa_instance_guid = get_service_instance_guid(c, UAA_NAME)

    logger.debug('UAA Service Instance GUID: %s', uaa_instance_guid)

    # now bind the uaa to the grafana app (it's ok to rebind, does not harm anything)
    try:
        logger.debug("Binding uaa to grafana app")
        bind_uaa = c.service_bindings.create(app_guid, uaa_instance_guid)
    except:
        pass

    # get the trustedIssuerId from the bound app
    uaa_trusted_issuer_id = get_trusted_issuer_id(c, space_guid, APP_NAME)
    logger.debug('UAA Trusted Issuer ID: %s', uaa_trusted_issuer_id)

    # now create a time series service instance
    timeseries_service_guid = get_service_guid(c, 'predix-timeseries')
    if timeseries_service_guid is None:
        # need to create and bind timeseries service
        create_and_bind_timeseries(c, APP_NAME)
    else:
        logger.debug('Predix Time Series Service GUID: %s', timeseries_service_guid)
        timeseries_service_plan_guid = get_service_plan_guid(c, timeseries_service_guid, 'Free')  # noqa
        logger.debug('Predix Time Series Service Plan GUID: %s', timeseries_service_plan_guid)  # noqa

    TIMESERIES_NAME = 'grafana-timeseries'

    ts_creation_params = {
        'trustedIssuerIds': [uaa_trusted_issuer_id]
    }

    try:
        logger.debug("Creating Time Series service instance")
        timeseries_instance = c.service_instances.create(
            space_guid,
            TIMESERIES_NAME,
            timeseries_service_plan_guid,
            ts_creation_params)
        timeseries_instance_guid = timeseries_instance['metadata']['guid']
    except:
        logger.debug("Getting Time Series service instance")
        timeseries_instance_guid = get_service_instance_guid(c, TIMESERIES_NAME)

    logger.debug('Time Series Service Instance GUID: %s', timeseries_instance_guid)

    try:
        bind_timeseries = c.service_bindings.create(
            app_guid,
            timeseries_instance_guid)
    except:
        pass

    # Inspect VCAP_SERVICES of our app to the get uaa_instance_url
    uaa_instance_uri = get_uaa_instance_uri(c, space_guid, APP_NAME)
    logger.debug('UAA Instance URI: %s', uaa_instance_uri)

    # Inspect VCAP_SERVICES of our app to get the TimeSeries data needed for the UAA Client

    #
    # get zone id from timeseries_instance_guid
    # Construct the zone info:
    #  timeseries.zones.<Predix-Zone-Id>.user
    #  timeseries.zones.<Predix-Zone-Id>.ingest

    timeseries_zone_id = get_timeseries_zone_id(c, APP_NAME)
    logger.debug('Time Series Zone ID: %s', timeseries_zone_id)

    timeseries_user_scope = 'timeseries.zones.{}.user'.format(timeseries_zone_id)
    timeseries_ingest_scope = 'timeseries.zones.{}.ingest'.format(timeseries_zone_id)  # noqa
    timeseries_query_scope = 'timeseries.zones.{}.query'.format(timeseries_zone_id)
    logger.debug('Time Series User Scope  : %s', timeseries_user_scope)
    logger.debug('Time Series Ingest Scope: %s', timeseries_ingest_scope)
    logger.debug('Time Series Query Scope : %s', timeseries_query_scope)

    tsconfig = get_timeseries_service_config(c, APP_NAME)
    # print out our ingest URI
    timeseries_ingest_uri = tsconfig['credentials']['ingest']['uri']
    logger.debug('Time Series Ingest URI: %s', timeseries_ingest_uri)

    # print out our query URI
    timeseries_query_uri = tsconfig['credentials']['query']['uri']
    logger.debug('Time Series Query URI : %s', timeseries_query_uri)

    #
    # This next part is still commandline, but we can print out the commandline!

    # OAUTH2 setup
    # we need a client created in our UAA service with this scope:
    #    predix-asset.zones.<service_instance_guid>.user
    #
    #  uaac target https://83a04ae4-47a7-470a-890b-aa1f6ec6d24d.predix-uaa.run.aws-usw02-pr.ice.predix.io
    #  uaac token client get admin  ( answer prompt )
    # create a client
    # see this for everything about scopes: https://github.com/GESoftware-CF/uaa/blob/master/docs/UAA-APIs.rst

    # uaac client add mynewclient --authorities "uaa.resource" \
    #   --scope "openid" --autoapprove "openid" \
    #   --authorized_grant_types "authorization_code,password,client_credentials,refresh_token"
    #   --secret iseegraphs
    # Next, add the zone to the client
    #  get our Asset Service GUID by running: cf env grafana-asset (the oauth-scope has the whole thing)
    #  "grafana-asset.zones.da62139d-4000-401e-bdf2-b69a25ee088d.user"

    # uaac client update grafana-client --authorities "uaa.resource,predix-asset.zones.da62139d-4000-401e-bdf2-b69a25ee088d.user"
    #print '###########RUN THIS MANUALLY ###################'
    #print 'uaac target {}'.format(uaa_instance_uri)
    #print 'uaac token client get admin'
    #print 'uaac client add mynewclient --authorities "uaa.resource,{},{},{}" --scope "openid" --autoapprove "openid" --authorized_grant_types "authorization_code,password,client_credentials,refresh_token" --secret iseegraphs'.format(timeseries_user_scope,timeseries_ingest_scope,timeseries_query_scope)
    #print 'uaac client add grafana-client --authorities "uaa.resource,{},{},{}" --scope "openid" --autoapprove "openid" --authorized_grant_types "password,client_credentials,refresh_token" --secret iseegraphs'.format(timeseries_user_scope,timeseries_ingest_scope,timeseries_query_scope)
    #print 'uaac client add ingestion-client --authorities "uaa.resource,{},{},{}" --scope "openid" --autoapprove "openid" --authorized_grant_types "password,client_credentials,refresh_token" --secret iseegraphs'.format(timeseries_user_scope,timeseries_ingest_scope,timeseries_query_scope)
    ### note used: print 'uaac client update mynewclient --authorities "uaa.resource,{},{}"'.format(timeseries_user_scope,timeseries_ingest_scope)
    ##print '################################################'

    logger.debug("Granting access to grafana-client and ingest client")
    os.system('uaac target {}'.format(uaa_instance_uri))
    os.system('uaac token client get admin --secret {}'.format(args.predix_uaa_admin_password))
    # remove existing clients
    os.system('uaac client delete grafana-client')
    os.system('uaac client delete ingestion-client')
    logger.debug("Creating client grafana-client")
    command = 'uaac client add grafana-client --authorities \
        "uaa.resource,{},{},{}" --scope "openid" \
        --autoapprove "openid" --authorized_grant_types \
        "password,client_credentials,refresh_token" \
        --secret {}'.format(
            timeseries_user_scope,
            timeseries_ingest_scope,
            timeseries_query_scope,
            args.predix_uaa_client_password)
    pprint(command)
    os.system(command)
    logger.debug("Creating client ingestion-client")
    command = 'uaac client add ingestion-client --authorities \
        "uaa.resource,{},{},{}" --scope "openid" \
        --autoapprove "openid" --authorized_grant_types \
        "password,client_credentials,refresh_token" \
        --secret {}'.format(
            timeseries_user_scope,
            timeseries_ingest_scope,
            timeseries_query_scope,
            args.predix_uaa_ingest_password)
    pprint(command)
    os.system(command)
    # startup grafana
    logger.debug("Starting GRAFANA")
    start_grafana_app(c, APP_NAME)
    ## Summarize what happened
    logger.debug("################################################")
    logger.debug('Grafana is ready to be used at URL: https://{}'.format(application_uri))
    logger.debug('Use these datasource settings:')
    logger.debug('Predix TS URL: https://time-series-store-predix.run.aws-usw02-pr.ice.predix.io')
    logger.debug('Predix Zone ID: {}'.format(timeseries_zone_id))
    logger.debug('UAA URL: {}/oauth/token'.format(uaa_instance_uri))
    logger.debug('Client ID and Secret: grafana-client:{}'.format(args.predix_uaa_client_password))
    logger.debug('Response Type: token')
    logger.debug('Grant Type: client_credentials')
    logger.debug('Origin: http://localhost')


if __name__ == "__main__":
    EXIT_CODE = main()
    sys.exit(EXIT_CODE)
